#!/usr/bin/env python3
"""
Quick script to check if messages are being saved to the database
Run this after testing WebSocket from frontend
"""
import subprocess
import sys

def check_database():
    try:
        cmd = [
            'sudo', 'docker', 'compose', 'exec', 'app', 
            'python', 'manage.py', 'shell', '-c',
            '''
from message.models import Message, Conversation
from core.models import User

print("=== Database Status After Test ===")
print(f"Total Messages: {Message.objects.count()}")
print(f"Total Conversations: {Conversation.objects.count()}")
print()

if Message.objects.exists():
    print("=== Recent Messages ===")
    for msg in Message.objects.order_by('-created_at')[:5]:
        print(f"From: {msg.sender.email} ({msg.sender.role})")
        print(f"Text: {msg.text}")
        print(f"Time: {msg.created_at}")
        print(f"Conversation: {msg.conversation.id} ({msg.conversation.user1.email} <-> {msg.conversation.user2.email})")
        print("---")
else:
    print("❌ No messages found in database")
    print()
    print("Possible issues:")
    print("1. User email not found in database")
    print("2. Room name format incorrect (should be 'user1_id_user2_id')")
    print("3. WebSocket connection closing before message processing")
            '''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='/home/franky/Documents/Projects/Zappbeast-new/gearhire_backend_os')
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"Error running check: {e}")

if __name__ == "__main__":
    check_database()