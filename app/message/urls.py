from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = router.urls 