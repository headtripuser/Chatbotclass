# headtripbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
import json
from .main import initialize_chatbot, send_message
from .event_handler import MyEventHandler

# Initialisiere den Chatbot (wird nur einmal ausgeführt)
client, session, thread, vector_store_id = initialize_chatbot()
assistant_id = "asst_KR9HhWRsQXJy63NTFwTVnUe8"

def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')

        # Event-Handler erstellen
        handler = MyEventHandler(client, thread.id, session, assistant_id, vector_store_id)

        # Chatbot-Nachricht senden und Antwort empfangen
        bot_response = ""
        for partial_response in send_message(client, session, thread, vector_store_id, user_input, handler):
            bot_response = partial_response

        # Falls keine Antwort empfangen wurde, verwende die letzte Antwort des Handlers
        if not bot_response and handler.latest_response:
            bot_response = handler.latest_response

        return JsonResponse({'response': bot_response})

    return render(request, 'headtripbot/chat.html')