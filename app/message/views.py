from rest_framework import viewsets, permissions
from .models import Conversation, Message, Attachment
from .serializers import ConversationSerializer, MessageSerializer, AttachmentSerializer
from core.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(models.Q(user1=user) | models.Q(user2=user)).order_by('-updated_at')


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 

class MessagesByConversationIdAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Support either single id (?conversation_id=2) or CSV (?conversation_ids=1,2,3)
        single_id = request.query_params.get('conversation_id')
        csv_ids = request.query_params.get('conversation_ids')

        conversation_ids = []
        if single_id is not None:
            try:
                conversation_ids = [int(single_id)]
            except (TypeError, ValueError):
                return Response({'error': 'conversation_id must be integer'}, status=status.HTTP_400_BAD_REQUEST)
        elif csv_ids is not None:
            raw_parts = [p.strip() for p in csv_ids.split(',') if p.strip()]
            for part in raw_parts:
                try:
                    conversation_ids.append(int(part))
                except ValueError:
                    # skip invalid entries
                    continue
            if not conversation_ids:
                return Response({'error': 'No valid conversation IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Missing required query param: conversation_id or conversation_ids'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        qs = (
            Message.objects
            .select_related('sender', 'attachment', 'conversation')
            .filter(
                models.Q(conversation__user1=user) | models.Q(conversation__user2=user),
                conversation_id__in=conversation_ids
            )
            .order_by('created_at')
        )

        # Return 200 with empty list if no messages
        return Response(MessageSerializer(qs, many=True).data)

class ConversationByEmail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Read target email from query params
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Missing required query param: email'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email not found'}, status=status.HTTP_404_NOT_FOUND)

        conversations = Conversation.objects.filter(
            models.Q(user2_id=target_user.id) |
            models.Q(user1_id=target_user.id)
        )

        if not conversations:
            return Response({'error': 'No conversations found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ConversationSerializer(conversations, many=True).data)


class FileUploadView(APIView):
    """
    Handle file uploads for messages
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            # Get the uploaded file
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Get request ID for deduplication (if provided by frontend)
            request_id = request.headers.get('X-Request-ID') or request.data.get('request_id')
            if request_id:
                # Check if this exact request was already processed
                from django.core.cache import cache
                cache_key = f"file_upload_{request_id}"
                if cache.get(cache_key):
                    return Response({
                        'error': 'Duplicate request detected'
                    }, status=status.HTTP_409_CONFLICT)
                # Set cache for 30 seconds
                cache.set(cache_key, True, 30)

            # Check for duplicate uploads based on file content hash
            import hashlib
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Check if same file content was uploaded in last 5 seconds
            recent_uploads = Attachment.objects.filter(
                uploaded_at__gte=timezone.now() - timezone.timedelta(seconds=5)
            ).order_by('-uploaded_at')
            
            for recent_upload in recent_uploads:
                try:
                    with recent_upload.file.open('rb') as f:
                        existing_content = f.read()
                        existing_hash = hashlib.md5(existing_content).hexdigest()
                        if existing_hash == file_hash:
                            return Response({
                                'message': 'File already uploaded recently',
                                'attachment': AttachmentSerializer(recent_upload).data
                            }, status=status.HTTP_200_OK)
                except:
                    continue  # Skip this file if we can't read it

            # Generate unique filename to avoid conflicts
            file_extension = file.name.split('.')[-1] if '.' in file.name else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())

            # Create attachment record
            logger.info(f"Creating attachment with file: {file.name}")
            attachment = Attachment.objects.create(
                file=file,
                uploaded_at=timezone.now()
            )
            logger.info(f"Attachment created successfully: {attachment.id}")

            # Return the attachment data
            serializer = AttachmentSerializer(attachment)
            return Response({
                'message': 'File uploaded successfully',
                'attachment': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'File upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)