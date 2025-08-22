from django.db import models
from core.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('quote', 'New Quote'),
        ('message', 'New Message'),
        ('following', 'New Follower'),
        ('review', 'New Review'),
        ('rfq_expired', 'RFQ Expired'),
        ('rfq_expiring', 'RFQ Expiring'),
        ('rfq_new', 'New RFQ'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for linking to specific objects
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)  # 'rfq', 'quote', 'message', etc.
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()