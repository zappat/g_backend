from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
from .models import Quote, QuoteAttachment
from .serializers import QuoteCreateSerializer, QuoteSerializer
from message.models import Conversation, Message
from message.serializers import MessageSerializer
from core.models import User


class QuoteListCreateView(generics.ListCreateAPIView):
    queryset = Quote.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    print("🔍 QuoteListCreateView")

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuoteCreateSerializer
        return QuoteSerializer


class QuoteCountView(APIView):
    """
    Get quote count for a specific user by id.
    URL: /api/quote/quotes/count/{id}/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            # Find user by id
            user = get_object_or_404(User, id=id)
            
            # Get query parameters for filtering
            status_filter = request.query_params.get('status', None)
            rfq_filter = request.query_params.get('rfq', None)
            
            # Build queryset
            queryset = Quote.objects.filter(created_by=user)
            
            # Apply filters if provided
            if status_filter:
                try:
                    quote_status = status_filter.lower()
                    queryset = queryset.filter(status=quote_status)
                except ValueError:
                    pass
                
            if rfq_filter:
                try:
                    rfq_id = int(rfq_filter)
                    queryset = queryset.filter(rfq_id=rfq_id)
                except ValueError:
                    pass
            
            # Get counts
            total_quotes = queryset.count()
            recent_quotes = queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
            
            return Response({
                'user_id': id,
                'total_quotes': total_quotes,
                'recent_quotes': recent_quotes,
                'quotes_this_month': recent_quotes
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this id not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            # Handle FormData from frontend
            data = request.data.copy()

            # Convert attachments to list if it's a single file or multiple files
            if 'attachments' in request.FILES:
                files = request.FILES.getlist('attachments')
                data['attachments'] = files
            else:
                data['attachments'] = []

            serializer = self.get_serializer(data=data, context={'request': request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            quote = serializer.save()

            # Create conversation and send message
            self.create_quote_conversation_and_message(quote)

            # Return using the read serializer for consistent response format
            response_serializer = QuoteSerializer(quote)
            headers = self.get_success_headers(response_serializer.data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_quote_conversation_and_message(self, quote):
        """Create conversation between provider and renter, and send quote as message"""
        try:
            provider = quote.created_by  # The user who submitted the quote
            renter = quote.rfq.created_by  # The user who posted the RFQ
            
            # Don't create conversation if same user (shouldn't happen but safety check)
            if provider == renter:
                return
            
            # Find or create conversation between provider and renter
            conversation = Conversation.objects.filter(
                models.Q(user1=provider, user2=renter) | 
                models.Q(user1=renter, user2=provider)
            ).first()
            
            if not conversation:
                conversation = Conversation.objects.create(
                    user1=provider,
                    user2=renter
                )
            
            # Create message with quote content
            message_text = f"{quote.quote}"
            
            message = Message.objects.create(
                conversation=conversation,
                sender=provider,
                text=message_text
            )
            
            # Update conversation timestamp
            conversation.save()
            
            # Send via WebSocket
            self.send_quote_via_websocket(message, conversation)
            
        except Exception as e:
            # Log error but don't fail the quote creation
            print(f"Error creating quote conversation: {str(e)}")

    def send_quote_via_websocket(self, message, conversation):
        """Send the quote message via WebSocket to defaultRoom"""
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                return
            
            # Serialize the message
            message_data = MessageSerializer(message).data
            
            # Add receiver information (renter who posted the RFQ)
            renter = conversation.user1 if conversation.user1 != message.sender else conversation.user2
            message_data['receiver'] = {
                'id': renter.id,
                'email': renter.email
            }
            
            # Send to defaultRoom
            async_to_sync(channel_layer.group_send)(
                "chat_defaultRoom",
                {
                    'type': 'chat_message',
                    'message_data': message_data
                }
            )
                    
        except Exception as e:
            print(f"Error sending quote via WebSocket: {str(e)}")


class QuoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class QuoteByRFQIdsView(APIView):
    """
    Get quotes by array of RFQ IDs
    URL: /api/quote/quotes/get-by-rfq-ids/
    Method: POST
    Body: {"rfq_ids": [1, 2, 3, ...]}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get rfq_ids from request body
            rfq_ids = request.data.get('rfq_ids', [])
            
            if not rfq_ids:
                return Response({
                    'error': 'rfq_ids array is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(rfq_ids, list):
                return Response({
                    'error': 'rfq_ids must be an array'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate that all rfq_ids are integers
            try:
                rfq_ids = [int(rfq_id) for rfq_id in rfq_ids]
            except (ValueError, TypeError):
                return Response({
                    'error': 'All rfq_ids must be valid integers'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get quotes for the specified RFQ IDs
            quotes = Quote.objects.filter(rfq_id__in=rfq_ids).order_by('-created_at')
            
            # Serialize the quotes
            serializer = QuoteSerializer(quotes, many=True)
            
            return Response({
                'quotes': serializer.data,
                'total_count': quotes.count(),
                'rfq_ids_requested': rfq_ids,
                'rfq_ids_found': list(quotes.values_list('rfq_id', flat=True).distinct())
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in QuoteByRFQIdsView: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuoteAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            quote = Quote.objects.get(id=pk)
            quote.status = 'accepted'
            quote.save()
            return Response({"id": quote.id, "status": quote.status}, status=status.HTTP_200_OK)

        except Quote.DoesNotExist:
            return Response({"error": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)


class QuoteRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            quote = Quote.objects.get(id=pk)
            quote.status = 'rejected'
            quote.save()
            return Response({"id": quote.id, "status": quote.status}, status=status.HTTP_200_OK)

        except Quote.DoesNotExist:
            return Response({"error": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)


class QuoteDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]