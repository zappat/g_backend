# WebSocket Usage Guide

## Overview
The WebSocket system now properly handles message saving with sender information.

## Connection Format
Connect to: `ws://localhost:8000/ws/chat/{room_name}/`

### Room Name Format
- Use format: `{user1_id}_{user2_id}` (e.g., `4_5` for conversation between user 4 and user 5)
- The system will automatically determine conversation participants from the room name

## Message Format

### Send Message
```javascript
const message = {
    message: "Your message text here",
    sender: "user_id_or_email"  // Required: User ID (as string) or email
};

socket.send(JSON.stringify(message));
```

### Receive Message
```javascript
{
    "message": "Your message text here",
    "sender": "user_id_or_email",
    "sender_email": "user@example.com",
    "timestamp": "2025-08-16 02:20:40.123456+00:00",
    "type": "message"
}
```

## Error Handling
If there's an error, you'll receive:
```javascript
{
    "error": "Error description"
}
```

## Database Storage
- Messages are automatically saved to the database
- Conversations are created automatically if they don't exist
- Each message includes:
  - Conversation reference
  - Sender (User model)
  - Message text
  - Timestamp
  - Read status

## Frontend Integration
```javascript
// Example frontend usage
const socket = new WebSocket('ws://localhost:8000/ws/chat/4_5/');

socket.onopen = function(event) {
    console.log('Connected to chat');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.error) {
        console.error('Error:', data.error);
    } else {
        console.log('New message:', data);
        // Display message in UI
    }
};

// Send message
function sendMessage(text, senderId) {
    socket.send(JSON.stringify({
        message: text,
        sender: senderId
    }));
}
```

## Logging
The system includes comprehensive logging for debugging:
- Connection attempts and successes
- Message processing
- Database operations
- Error conditions

Check logs with: `sudo docker compose logs app --tail=20`