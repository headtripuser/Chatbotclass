# headtripbot/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .main import send_message
from .event_handler import MyEventHandler

# Initialisiere den Chatbot einmalig
from .main import initialize_chatbot
client, session, thread, vector_store_id = initialize_chatbot()
assistant_id = "asst_KR9HhWRsQXJy63NTFwTVnUe8"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connected!")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        print(f"Message received: {text_data}")
        data = json.loads(text_data)
        user_message = data.get("message", "")

        # Erstelle den Event-Handler
        handler = MyEventHandler(client, thread.id, session, assistant_id, vector_store_id)

        # Starte die asynchrone Verarbeitung der Bot-Antwort
        await self.stream_bot_response(user_message, handler)

    async def stream_bot_response(self, user_message, handler):
        """
        Streamt die Bot-Antwort stückweise an den WebSocket-Client.
        """
        for partial_response in send_message(client, session, thread, vector_store_id, user_message, handler):
            # Sende jeden Chunk sofort über den WebSocket
            await self.send(text_data=json.dumps({"message": partial_response}))
