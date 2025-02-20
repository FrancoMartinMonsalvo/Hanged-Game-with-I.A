from django.urls import re_path
from ..game.consumers import AhorcadoConsumer

websocket_urlpatterns = [
    re_path(r'ws/ahorcado/$', AhorcadoConsumer.as_asgi()),
]