# headtripbot/routing.py

from django.urls import re_path
from . import consumers  # Importiere den Consumer aus consumers.py

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]