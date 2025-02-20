import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AhorcadoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Conectado al WebSocket"}))

    async def disconnect(self, close_code):
        print("WebSocket cerrado")

    async def receive(self, text_data):
        data = json.loads(text_data)
        letra = data.get("letter")

        # Simula una respuesta de la IA
        response = {"message": f"La IA intentó con la letra: {letra}"}

        await self.send(text_data=json.dumps(response))
