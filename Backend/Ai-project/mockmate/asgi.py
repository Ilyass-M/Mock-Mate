import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from mockmate.middleware import JWTAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()
from django.urls import path

from AiQuetionare.consumer import * 
from AiQuetionare import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": (
        JWTAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})