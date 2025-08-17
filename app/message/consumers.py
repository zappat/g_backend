import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_by_identifier(self, identifier):
        """Get user by ID or email"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            if identifier.isdigit():
                return User.objects.get(id=int(identifier))
            else:
                # Try by email first
                user = User.objects.filter(email=identifier).first()
                if user:
                    return user
                # Try by username if email doesn't work
                return User.objects.filter(username=identifier).first()
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_or_create_conversation(self, user1, user2):
        """Get or create conversation between two users"""
        from .models import Conversation
        
        # Ensure user1 has lower ID for consistency
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        conversation, created = Conversation.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return conversation

    @database_sync_to_async
    def save_message(self, conversation, sender, text):
        """Save message to database"""
        from .models import Message
        
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text
        )
        return message

    @database_sync_to_async
    def save_message_with_metadata(self, conversation, sender, text, message_id, client_timestamp):
        """Save message to database with additional metadata"""
        from .models import Message
        
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text
        )
        
        # Store additional metadata in the message object
        # Note: You might want to add custom fields to your Message model for these
        message.custom_id = message_id
        message.client_timestamp = client_timestamp
        message.save()
        
        return message

    async def get_or_create_direct_conversation(self, user1, user2):
        """Get or create direct conversation between two specific users"""
        try:
            conversation = await self.get_or_create_conversation(user1, user2)
            logger.info(f"Direct conversation between {user1.email} and {user2.email}: {conversation.id}")
            return conversation
        except Exception as e:
            logger.error(f"Error creating direct conversation: {str(e)}")
            return None

    async def get_conversation_from_room(self, room_name, sender):
        """Get conversation from room name - supports multiple formats"""
        try:
            # Format 1: "user1_id_user2_id" (e.g., "4_5")
            if '_' in room_name and room_name.replace('_', '').isdigit():
                room_parts = room_name.split('_')
                if len(room_parts) >= 2:
                    user1_id = room_parts[0]
                    user2_id = room_parts[1]
                    
                    user1 = await self.get_user_by_identifier(user1_id)
                    user2 = await self.get_user_by_identifier(user2_id)
                    
                    if user1 and user2:
                        return await self.get_or_create_conversation(user1, user2)
            
            # Format 2: Generic room (e.g., "default", "general")
            # For generic rooms, create a shared conversation that all users can participate in
            if room_name in ['default', 'general', 'public']:
                return await self.get_or_create_generic_room_conversation(room_name, sender)
            
            # Format 3: Custom room names - treat as generic rooms
            return await self.get_or_create_generic_room_conversation(room_name, sender)
            
        except Exception as e:
            logger.error(f"Error getting conversation from room '{room_name}': {str(e)}")
            return None

    @database_sync_to_async
    def get_or_create_generic_room_conversation(self, room_name, sender):
        """Get or create a conversation for generic rooms that multiple users can join"""
        from .models import Conversation
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            # For generic rooms, we'll create a shared conversation
            # We'll use a special approach: create one conversation per room that all users share
            
            # Look for existing conversation for this room
            # We'll identify generic room conversations by looking for the special room user
            room_user_email = f'room_{room_name}@generic.rooms'
            
            existing_conversation = Conversation.objects.filter(
                user1__email=room_user_email
            ).first()
            
            if not existing_conversation:
                existing_conversation = Conversation.objects.filter(
                    user2__email=room_user_email
                ).first()
            
            if existing_conversation:
                logger.info(f"Found existing generic room conversation: {existing_conversation.id}")
                return existing_conversation
            
            # Create a new generic room conversation
            # Create a special user to represent the room
            generic_room_user, created = User.objects.get_or_create(
                email=room_user_email,
                defaults={
                    'role': 'merchant',
                    'is_active': False
                }
            )
            
            # Create conversation between the room and the first user who joins
            conversation = Conversation.objects.create(
                user1=generic_room_user,
                user2=sender
            )
            
            logger.info(f"Created generic room conversation for '{room_name}' with ID: {conversation.id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating generic room conversation: {str(e)}")
            return None

    # Accepts a websocket connection and adds the user to the chat group based on the room name
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            
            logger.info(f"WebSocket connect attempt for room: {self.room_name}")
            logger.info(f"User: {self.scope.get('user', 'Anonymous')}")
            logger.info(f"Headers: {dict(self.scope.get('headers', []))}")

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            
            logger.info(f"WebSocket connected successfully for room: {self.room_name}")
            
            # Send a welcome message to confirm connection
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Connected to room: {self.room_name}',
                'room': self.room_name
            }))
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            await self.close(code=1011)  # Internal server error

    # Removes the user from the chat group when the websocket disconnects
    async def disconnect(self, close_code):
        try:
            logger.info(f"WebSocket disconnecting from room: {self.room_name}, close_code: {close_code}")
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {str(e)}")

    # Handles incoming messages from WebSocket, parses JSON, and sends to group
    async def receive(self, text_data):
        try:
            logger.info(f"Received message in room {self.room_name}: {text_data}")
            data = json.loads(text_data)
            
            # Extract all message fields
            message_text = data.get('message', '')
            sender_identifier = data.get('sender', '')
            receiver_identifier = data.get('receiver', '')
            message_id = data.get('id', '')
            client_timestamp = data.get('timestamp', '')

            # Validate required fields
            if not message_text:
                logger.warning("Received empty message - sending error response")
                await self.send(text_data=json.dumps({
                    'error': 'Message cannot be empty',
                    'type': 'error'
                }))
                return

            if not sender_identifier:
                logger.warning("Received message without sender - sending error response")
                await self.send(text_data=json.dumps({
                    'error': 'Sender information required',
                    'type': 'error'
                }))
                return

            # Get sender user
            sender = await self.get_user_by_identifier(sender_identifier)
            if not sender:
                logger.error(f"User not found: {sender_identifier}")
                await self.send(text_data=json.dumps({
                    'error': f'Sender not found: {sender_identifier}',
                    'type': 'error'
                }))
                return

            # Get receiver user if specified
            receiver = None
            if receiver_identifier:
                # Handle both string and integer receiver identifiers
                if isinstance(receiver_identifier, int) or (isinstance(receiver_identifier, str) and receiver_identifier.isdigit()):
                    # Convert to integer for user ID lookup
                    receiver_id = int(receiver_identifier)
                    receiver = await self.get_user_by_identifier(str(receiver_id))
                else:
                    # Treat as email lookup
                    receiver = await self.get_user_by_identifier(receiver_identifier)
                
                if not receiver:
                    logger.warning(f"Receiver not found: {receiver_identifier}, treating as room message")

            # Parse room name to get conversation participants
            # Support multiple room name formats
            saved_message = None
            try:
                # For room-based messaging, always use room conversation regardless of receiver
                # This ensures all messages in the same room go to the same conversation
                conversation = await self.get_conversation_from_room(self.room_name, sender)
                
                if conversation:
                    # Save message to database with additional fields
                    saved_message = await self.save_message_with_metadata(
                        conversation, sender, message_text, message_id, client_timestamp
                    )
                    logger.info(f"Message saved to database: {saved_message.id}")
                    
                    # Log receiver information for debugging (but don't affect conversation)
                    if receiver:
                        logger.info(f"Message has receiver {receiver.email} but saved to room conversation {conversation.id}")
                else:
                    logger.warning(f"Could not determine conversation for room: {self.room_name}")
            except Exception as e:
                logger.error(f"Error processing conversation: {str(e)}")
                # Don't return here - still broadcast the message even if saving fails
                # Send error to sender but keep connection alive
                await self.send(text_data=json.dumps({
                    'error': f'Message processing failed: {str(e)}',
                    'type': 'warning',
                    'message': message_text,
                    'sender': sender_identifier
                }))

            # Send message to group with all information
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message_text,
                        'sender': sender_identifier,
                        'sender_email': sender.email if sender else 'Unknown',
                        'receiver': receiver_identifier if receiver_identifier else None,
                        'receiver_email': receiver.email if receiver else None,
                        'message_id': message_id,
                        'client_timestamp': client_timestamp,
                        'server_timestamp': str(saved_message.created_at) if saved_message else '',
                        'conversation_id': saved_message.conversation.id if saved_message else None,
                    }
                )
                logger.info(f"Message broadcasted to group: {self.room_group_name}")
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                # Send error to sender but don't close connection
                await self.send(text_data=json.dumps({
                    'error': 'Message sent but failed to broadcast',
                    'type': 'warning'
                }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message',
                'type': 'error',
                'details': str(e)
            }))

    # Receives messages from the group and sends them to WebSocket
    async def chat_message(self, event):
        try:
            message_data = json.dumps({
                'message': event['message'],
                'sender': event.get('sender', ''),
                'sender_email': event.get('sender_email', ''),
                'receiver': event.get('receiver', ''),
                'receiver_email': event.get('receiver_email', ''),
                'message_id': event.get('message_id', ''),
                'client_timestamp': event.get('client_timestamp', ''),
                'server_timestamp': event.get('server_timestamp', ''),
                'conversation_id': event.get('conversation_id', ''),
                'type': 'message'
            })
            await self.send(text_data=message_data)
            logger.info(f"Sent message to WebSocket: {message_data}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")