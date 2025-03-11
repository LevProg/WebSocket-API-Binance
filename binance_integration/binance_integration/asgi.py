import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ticker.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance_integration.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ticker.routing.websocket_urlpatterns
        )
    ),
})