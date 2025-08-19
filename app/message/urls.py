from django.urls import path
from .views import ConversationByEmail, MessagesByConversationIdAPIView

urlpatterns = [
    path('conversations/', ConversationByEmail.as_view(), name='conversation-by-email'),
    path('messages/', MessagesByConversationIdAPIView.as_view(), name='messages-by-conversation-id'),
]