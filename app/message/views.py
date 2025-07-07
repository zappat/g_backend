from rest_framework import viewsets, permissions
from .models import Conversation, Message, Attachment
from .serializers import ConversationSerializer, MessageSerializer, AttachmentSerializer
from core.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(models.Q(user1=user) | models.Q(user2=user)).order_by('-updated_at')

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(models.Q(conversation__user1=user) | models.Q(conversation__user2=user)).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 