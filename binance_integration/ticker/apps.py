from django.apps import AppConfig
import threading

class TickerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticker'

    def ready(self):
        from .websocket_client import start_websocket
        thread = threading.Thread(target=start_websocket, daemon=True)
        thread.start()