from rest_framework import serializers
from .models import Notification
from core.models import User


class NotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'recipient_email',
            'sender',
            'sender_email',
            'title',
            'message',
            'notification_type',
            'is_read',
            'created_at',
            'updated_at',
            'related_object_id',
            'related_object_type',
            'mode'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'recipient',
            'title',
            'message',
            'mode',
            'notification_type',
            'related_object_id',
            'related_object_type',
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of notification IDs to mark as read"
    )