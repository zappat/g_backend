from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat messages - saves to message database
    re_path(r"ws/chat/(?P<room_name>defaultRoom|merchantRoom|\w+Room)/?$", consumers.ChatConsumer.as_asgi()),
    
    # Notifications - saves to notification database
    re_path(r"ws/notification/(?P<room_name>merchantNotificationRoom|\w+)/?$", consumers.NotificationConsumer.as_asgi()),
]