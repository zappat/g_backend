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


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for notifications - saves to notification database
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'notification_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Notification WebSocket connected to room: {self.room_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Notification WebSocket disconnected from room: {self.room_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print("notification data: ", data)
            title = data.get('title', '')
            message_text = data.get('message', '')
            recipient_id = data.get('recipient_id', '')  # Can be email or user ID
            sender = data.get('sender', '')  # Sender email or ID (optional)
            notification_type = data.get('type', 'general')
            related_object_id = data.get('related_object_id')
            related_object_type = data.get('related_object_type')
            
            if not title or not message_text or not recipient_id:
                await self.send(text_data=json.dumps({
                    'error': 'Missing required fields: title, message, recipient'
                }))
                return

            # Save notification to database
            notification_obj = await self.save_notification(
                title=title,
                message_text=message_text,
                recipient_id=recipient_id,
                sender=sender,
                notification_type=notification_type,
                related_object_id=related_object_id,
                related_object_type=related_object_type
            )

            if notification_obj:
                # Serialize the notification
                notification_data = await self.serialize_notification(notification_obj)
                
                # Send notification to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'notification_message',
                        'notification_data': notification_data
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Failed to save notification'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in notification receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps(event['notification_data']))

    @database_sync_to_async
    def save_notification(self, title, message_text, recipient_id, sender, notification_type, related_object_id, related_object_type):
        try:
            from notification.models import Notification
            from core.models import User
            
            # Get recipient user - handle both email and user ID
            recipient_user = None
            try:
                # Try as integer (user ID) first
                user_id = int(recipient_id)
                recipient_user = User.objects.get(id=user_id)
            except (ValueError, TypeError):
                # If not integer, try as email
                try:
                    recipient_user = User.objects.get(email=recipient)
                except User.DoesNotExist:
                    logger.error(f"User not found with email: {recipient}")
                    return None
            except User.DoesNotExist:
                logger.error(f"User not found with ID: {recipient_id}")
                return None
            
            if not recipient_user:
                logger.error(f"Could not find user with identifier: {recipient_id}")
                return None
            
            # Get sender user (optional) - handle both email and user ID
            sender_user = None
            if sender:
                try:
                    # Try as integer (user ID) first
                    sender_id = int(sender)
                    sender_user = User.objects.get(id=sender_id)
                except (ValueError, TypeError):
                    # If not integer, try as email
                    try:
                        sender_user = User.objects.get(email=sender)
                    except User.DoesNotExist:
                        logger.error(f"Sender not found with email: {sender}")
                        # Don't return None, just proceed without sender
                except User.DoesNotExist:
                    logger.error(f"Sender not found with ID: {sender}")
                    # Don't return None, just proceed without sender
            
            # Create notification
            notification = Notification.objects.create(
                recipient=recipient_user,
                sender=sender_user,
                title=title,
                message=message_text,
                notification_type=notification_type,
                related_object_id=related_object_id,
                related_object_type=related_object_type
            )
            
            sender_info = f" from {sender_user.email}" if sender_user else ""
            logger.info(f"Notification created for user {recipient_user.email}{sender_info}: {title}")
            return notification
            
        except Exception as e:
            logger.error(f"Error saving notification: {str(e)}")
            return None

    @database_sync_to_async
    def serialize_notification(self, notification):
        from notification.serializers import NotificationSerializer
        serializer = NotificationSerializer(notification)
        return serializer.data
