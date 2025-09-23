from rest_framework import serializers
from .models import Conversation, Message, Attachment
from core.models import User

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    attachment = AttachmentSerializer(read_only=True)
    attachment_id = serializers.PrimaryKeyRelatedField(queryset=Attachment.objects.all(), source='attachment', write_only=True, required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_role', 'text', 'attachment', 'attachment_id', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'is_read', 'attachment']

class ConversationSerializer(serializers.ModelSerializer):
    user1 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user2 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    messages = MessageSerializer(many=True, read_only=True)
    rfq_id = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = Conversation
        fields = ['id', 'user1', 'user2', 'created_at', 'updated_at', 'messages', 'rfq_id'] 