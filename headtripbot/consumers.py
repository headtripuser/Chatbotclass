# headtripbot/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Hier kannst du die Nachricht an den Chatbot senden
        # und die Antwort streamen
        for chunk in self.generate_response(message):
            await self.send(text_data=json.dumps({
                'message': chunk
            }))

    def generate_response(self, message):
        # Simuliere das Streaming von Antworten
        response = f"Du hast gesagt: {message}"
        for word in response.split():
            yield word + " "