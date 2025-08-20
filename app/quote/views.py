from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
import json
from .models import Quote, QuoteAttachment
from .serializers import QuoteSerializer
from message.models import Conversation, Message
from message.serializers import MessageSerializer


class QuoteListCreateView(generics.ListCreateAPIView):
    queryset = Quote.objects.all().order_by('-id')
    serializer_class = QuoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    print("🔍 QuoteListCreateView")

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            if 'created_by' in data:
                del data['created_by']

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)

            # Attach files if provided
            files = list(request.FILES.getlist('attachments')) + list(request.FILES.getlist('attachments[]'))
            for file in files:
                QuoteAttachment.objects.create(quote=serializer.instance, file=file)

            # Create conversation and send message
            self.create_quote_conversation_and_message(serializer.instance)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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