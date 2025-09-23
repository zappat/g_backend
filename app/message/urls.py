from django.urls import path
from .views import ConversationViewSet, ConversationByEmail, MessagesByConversationIdAPIView, FileUploadView

urlpatterns = [
    # Conversation CRUD operations (including retrieve by ID)
    path('conversations/', ConversationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='conversation-detail'),

    # Additional conversation endpoints
    path('conversations/by-email/', ConversationByEmail.as_view(), name='conversation-by-email'),
    path('messages/', MessagesByConversationIdAPIView.as_view(), name='messages-by-conversation-id'),
    
    # File upload endpoint
    path('file-upload/', FileUploadView.as_view(), name='file-upload'),
]