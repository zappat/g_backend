"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import logging

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import message.routing

# Configure logging for debugging
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Create a custom middleware to log WebSocket connections
class WebSocketLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            logger.info(f"WebSocket connection attempt: {scope.get('path', 'unknown')}")
            logger.info(f"Headers: {dict(scope.get('headers', []))}")
        return await self.app(scope, receive, send)

# Custom authentication middleware that allows unauthenticated WebSocket connections
class WebSocketAuthMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            # For WebSocket connections, we'll allow unauthenticated access
            # You can add custom authentication logic here if needed
            scope['user'] = scope.get('user', None)
        return await self.app(scope, receive, send)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": WebSocketLoggingMiddleware(
        WebSocketAuthMiddleware(
            URLRouter(message.routing.websocket_urlpatterns)
        )
    ),
})
