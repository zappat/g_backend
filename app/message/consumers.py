import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected to room: {self.room_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from room: {self.room_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_text = data.get('message', '')
            sender_email = data.get('sender', '')
            conversation_id = data.get('conversation_id')
            
            if not message_text or not sender_email or not conversation_id:
                await self.send(text_data=json.dumps({
                    'error': 'Missing required fields: message, sender, conversation_id'
                }))
                return

            # Save message to database
            message_obj = await self.save_message(
                message_text=message_text,
                sender_email=sender_email,
                conversation_id=conversation_id
            )

            if message_obj:
                # Serialize the message
                message_data = await self.serialize_message(message_obj)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_data': message_data
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Failed to save message'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message_data']))

    @database_sync_to_async
    def save_message(self, message_text, sender_email, conversation_id):
        try:
            from .models import Message, Conversation
            from core.models import User
            
            # Get sender user
            sender = User.objects.get(email=sender_email)
            
            # Get conversation and verify user is participant
            conversation = Conversation.objects.get(id=conversation_id)
            if sender not in [conversation.user1, conversation.user2]:
                logger.error(f"User {sender_email} not participant in conversation {conversation_id}")
                return None
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                text=message_text
            )
            
            # Update conversation timestamp
            conversation.save()  # This will update updated_at
            
            return message
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None

    @database_sync_to_async
    def serialize_message(self, message):
        from .serializers import MessageSerializer
        serializer = MessageSerializer(message)
        return serializer.data
