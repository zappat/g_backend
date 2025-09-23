import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import models

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
            sender_id = data.get('sender_id', '')
            sender_role = data.get('sender_role', '')
            # Handle both conversation_id and conversation field names
            conversation_id = data.get('conversation_id') or data.get('conversation')
            message_type = data.get('type', 'general')
            receiver = data.get('receiver')  # For quote messages
            file_url = data.get('file_url')

            logger.info(f"Received message in room {self.room_name}: type={message_type}, senderId={sender_id}, conversation_id={conversation_id}")
            logger.info(f"Sender role: {sender_role}")
            logger.info(f"Receiver: {receiver}")
            logger.info(f"Message text: {message_text}")
            logger.info(f"File URL: {file_url}")
            # Log which field was used for conversation
            if data.get('conversation_id'):
                logger.info("Using conversation_id field")
            elif data.get('conversation'):
                logger.info("Using conversation field")

            # Check for attachment_id or file_url if no message text
            attachment_id = data.get('attachment_id')
            
            if not sender_id:
                await self.send(text_data=json.dumps({
                    'error': 'Missing required field: sender_id'
                }))
                return
                
            # Must have either message text or file attachment
            if not message_text and not attachment_id and not file_url:
                await self.send(text_data=json.dumps({
                    'error': 'Missing required field: message text or file attachment'
                }))
                return

            # Check for duplicate messages (same content, sender, and recent timestamp)
            # Only check for duplicates if there's message text
            if message_text:
                duplicate_check = await self.check_duplicate_message(sender_id, message_text)
                if duplicate_check:
                    logger.info(f"Duplicate message detected, skipping: {message_text[:50]}...")
                    await self.send(text_data=json.dumps({
                        'error': 'Duplicate message detected'
                    }))
                    return

            # Validate quote messages have required fields
            if message_type == 'quote':
                # Check for both rfq_id and rfqId to handle different naming conventions
                rfq_id_value = data.get('rfqId') or data.get('rfq_id')
                logger.info(f"RFQ ID value: {rfq_id_value}")
                if not rfq_id_value:
                    await self.send(text_data=json.dumps({
                        'error': 'Missing required field: rfqId or rfq_id for quote messages'
                    }))
                    return

            # Handle messages without conversation_id - create conversation if receiver is provided
            if not conversation_id and receiver:
                logger.info(f"Creating conversation for message: sender={sender_id}, receiver={receiver}, type={message_type}")
                # Get rfq_id for quote messages
                rfq_id = (data.get('rfqId') or data.get('rfq_id')) if message_type == 'quote' else None
                conversation_id = await self.get_or_create_conversation(
                    sender_id, receiver, rfq_id
                )
                logger.info(f"Conversation created: {conversation_id}")
                if not conversation_id:
                    await self.send(text_data=json.dumps({
                        'error': 'Could not create conversation'
                    }))
                    return
            elif not conversation_id:
                logger.warning(f"Missing conversation_id/conversation for message type {message_type} in room {self.room_name}")
                await self.send(text_data=json.dumps({
                    'error': 'Missing required field: conversation_id or conversation'
                }))
                return

            # Save message to database
            rfq_id = (data.get('rfqId') or data.get('rfq_id')) if message_type == 'quote' else None
            logger.info(f"Saving message with attachment_id: {attachment_id}, file_url: {file_url}")
            message_obj = await self.save_message(
                message_text=message_text,
                sender=sender_id,
                sender_role=sender_role,
                conversation_id=conversation_id,
                message_type=message_type,
                rfq_id=rfq_id,
                attachment_id=attachment_id,
                file_url=file_url
            )

            if message_obj:
                logger.info(f"Message saved successfully: {message_obj.id}, type: {message_type}")

                # Serialize the message
                message_data = await self.serialize_message(message_obj)

                # Add receiver information for all messages
                if receiver:
                    if isinstance(receiver, int):
                        message_data['receiver'] = receiver
                    elif isinstance(receiver, dict):
                        message_data['receiver'] = receiver.get('id', receiver)
                    else:
                        message_data['receiver'] = receiver
                else:
                    # Get receiver from conversation
                    conversation = message_obj.conversation
                    if conversation.user1.id == message_obj.sender.id:
                        message_data['receiver'] = conversation.user2.id
                    else:
                        message_data['receiver'] = conversation.user1.id

                # Add additional data for quote messages
                if message_type == 'quote':
                    message_data['type'] = 'quote'
                    # Use the same logic to get rfq_id from either field name
                    rfq_id_value = data.get('rfqId') or data.get('rfq_id')
                    if rfq_id_value:
                        message_data['rfqId'] = rfq_id_value
                    logger.info(f"Quote message processed with rfqId: {rfq_id_value}")

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_data': message_data
                    }
                )
                logger.info(f"Message sent to room group: {self.room_group_name}")
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
    def save_message(self, message_text, sender, sender_role, conversation_id, message_type='general', rfq_id=None, attachment_id=None, file_url=None):
        try:
            from .models import Message, Conversation
            from core.models import User
            from quote.models import Quote
            from rfq.models import RFQ

            # Get sender user
            try:
                sender = User.objects.get(id=sender)
            except User.DoesNotExist:
                logger.error(f"User not found with ID: {sender}")
                return None

            # Get conversation and verify user is participant
            conversation = Conversation.objects.get(id=conversation_id)
            if sender not in [conversation.user1, conversation.user2]:
                logger.error(f"User {sender.id} not participant in conversation {conversation_id}")
                return None

            # Save quote to database if this is a quote message
            if message_type == 'quote':
                if not rfq_id:
                    logger.error("rfq_id is required for quote messages")
                    return None

                try:
                    rfq = RFQ.objects.get(id=rfq_id)
                    quote = Quote.objects.create(
                        created_by=sender,
                        quote=message_text,
                        rfq=rfq,
                        status='open'  # Explicitly set status
                    )
                    logger.info(f"Quote created: {quote.id} for RFQ {rfq_id} by {sender.email}")
                except RFQ.DoesNotExist:
                    logger.error(f"RFQ with id {rfq_id} does not exist")
                    return None
                except Exception as e:
                    logger.error(f"Error creating quote: {str(e)}")
                    return None

            # Handle file attachment
            attachment = None
            logger.info(f"Processing attachment_id: {attachment_id}, file_url: {file_url}")
            
            if attachment_id:
                try:
                    from .models import Attachment
                    attachment = Attachment.objects.get(id=attachment_id)
                    logger.info(f"Found attachment by ID: {attachment.id} for message")
                except Attachment.DoesNotExist:
                    logger.error(f"Attachment with id {attachment_id} does not exist")
                    return None
                except Exception as e:
                    logger.error(f"Error getting attachment: {str(e)}")
                    return None
            elif file_url:
                # Try to find attachment by file URL
                try:
                    from .models import Attachment
                    # Extract filename from URL
                    filename = file_url.split('/')[-1]
                    logger.info(f"Looking for attachment with filename: {filename}")
                    
                    # Find attachment by filename
                    attachment = Attachment.objects.filter(file__icontains=filename).first()
                    
                    if attachment:
                        logger.info(f"Found attachment by file URL: {attachment.id} for message")
                    else:
                        logger.warning(f"No attachment found for file URL: {file_url}")
                        # List recent attachments for debugging
                        recent_attachments = Attachment.objects.all().order_by('-uploaded_at')[:3]
                        logger.info(f"Recent attachments: {[(a.id, str(a.file)) for a in recent_attachments]}")
                except Exception as e:
                    logger.error(f"Error finding attachment by file URL: {str(e)}")
            else:
                logger.info("No attachment_id or file_url provided")

            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                sender_role=sender_role,
                text=message_text or '',  # Allow empty text for file-only messages
                attachment=attachment
            )

            # Update conversation timestamp
            conversation.save()  # This will update updated_at

            return message

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None

    @database_sync_to_async
    def get_or_create_conversation(self, sender_id, receiver, rfq_id=None):
        """Get existing conversation or create new one for any message type"""
        try:
            from .models import Conversation
            from core.models import User

            # Get sender user
            try:
                sender = User.objects.get(id=sender_id)
                logger.info(f"Found sender user: {sender.email} (ID: {sender.id})")
            except User.DoesNotExist:
                logger.error(f"User not found with ID: {sender_id}")
                return None

            # Get receiver user (can be email, user object, dict, or ID)
            if isinstance(receiver, dict):
                receiver_email = receiver.get('email')
                if receiver_email:
                    try:
                        receiver_user = User.objects.get(email=receiver_email)
                    except User.DoesNotExist:
                        logger.error(f"User not found with email: {receiver_email}")
                        return None
                else:
                    receiver_id = receiver.get('id')
                    try:
                        receiver_user = User.objects.get(id=receiver_id)
                    except User.DoesNotExist:
                        logger.error(f"User not found with ID: {receiver_id}")
                        return None
            elif isinstance(receiver, str):
                # Assume it's an email
                try:
                    receiver_user = User.objects.get(email=receiver)
                except User.DoesNotExist:
                    logger.error(f"User not found with email: {receiver}")
                    return None
            elif isinstance(receiver, int):
                # Handle integer user ID
                try:
                    receiver_user = User.objects.get(id=receiver)
                    logger.info(f"Found receiver user by ID: {receiver_user.email} (ID: {receiver_user.id})")
                except User.DoesNotExist:
                    logger.error(f"User not found with ID: {receiver}")
                    return None
            else:
                logger.error(f"Unsupported receiver type: {type(receiver)} with value: {receiver}")
                return None

            # Don't create conversation if same user
            if sender == receiver_user:
                return None

            # Find or create conversation between sender and receiver
            conversation = Conversation.objects.filter(
                models.Q(user1=sender, user2=receiver_user) |
                models.Q(user1=receiver_user, user2=sender)
            ).first()

            if not conversation:
                conversation = Conversation.objects.create(
                    user1=sender,
                    user2=receiver_user,
                    rfq_id=rfq_id
                )
                logger.info(f"Created new conversation: {conversation.id} between {sender.email} and {receiver_user.email} with rfq_id: {rfq_id}")
            else:
                # If conversation exists but doesn't have rfq_id and we have one, update it
                if rfq_id and not conversation.rfq_id:
                    conversation.rfq_id = rfq_id
                    conversation.save()
                    logger.info(f"Updated existing conversation: {conversation.id} with rfq_id: {rfq_id}")
                else:
                    logger.info(f"Found existing conversation: {conversation.id} between {sender.email} and {receiver_user.email}")

            return conversation.id

        except Exception as e:
            logger.error(f"Error getting/creating conversation: {str(e)}")
            return None

    @database_sync_to_async
    def check_duplicate_message(self, sender_id, message_text):
        """Check if the same message was sent recently by the same sender"""
        try:
            from .models import Message
            from django.utils import timezone
            from datetime import timedelta
            
            # Check for duplicate message in last 5 seconds
            recent_message = Message.objects.filter(
                sender_id=sender_id,
                text=message_text,
                created_at__gte=timezone.now() - timedelta(seconds=5)
            ).first()
            
            return recent_message is not None
        except Exception as e:
            logger.error(f"Error checking duplicate message: {str(e)}")
            return False

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
            mode = data.get('mode')
            
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
                related_object_type=related_object_type,
                mode=mode
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
    def save_notification(self, title, message_text, recipient_id, sender, notification_type, related_object_id, related_object_type, mode):
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
                    recipient_user = User.objects.get(email=recipient_id)
                except User.DoesNotExist:
                    logger.error(f"User not found with email: {recipient_id}")
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
                related_object_type=related_object_type,
                mode=mode
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
