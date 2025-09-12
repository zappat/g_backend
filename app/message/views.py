from rest_framework import viewsets, permissions
from .models import Conversation, Message, Attachment
from .serializers import ConversationSerializer, MessageSerializer, AttachmentSerializer
from core.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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