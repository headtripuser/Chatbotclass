from django.shortcuts import render
from django.http import JsonResponse
import json
import tempfile  # Neu: Temporäre Dateien für Whisper
from .main import initialize_chatbot, send_message
from .event_handler import MyEventHandler
import openai
import os


# Initialisiere den Chatbot (wird nur einmal ausgeführt)
client, session, thread, vector_store_id = initialize_chatbot()
assistant_id = "asst_KR9HhWRsQXJy63NTFwTVnUe8"

# OpenAI API-Key
openai.api_key = os.getenv("OPENAI_API_KEY")


def chat(request):
    """Verarbeitet Textnachrichten für den Chatbot."""
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

def transcribe_audio(request):
    """Verarbeitet die Audiodatei und gibt die Transkription zurück."""
    if request.method == 'POST' and 'audio' in request.FILES:
        try:
            audio_file = request.FILES['audio']
            print(f"📂 Erhaltene Datei: {audio_file.name}, Typ: {audio_file.content_type}")

            # Audiodatei in temporäre Datei speichern (damit Whisper sie erkennt)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(audio_file.read())
                temp_audio_path = temp_audio.name  # Speicherort merken

            # Öffne die Datei erneut als echte Datei für OpenAI Whisper
            with open(temp_audio_path, "rb") as file_for_whisper:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=file_for_whisper,
                    language="de"
                )

            print(f"📝 Transkription: {transcription.text}")  # Debugging-Ausgabe
            return JsonResponse({'transcription': transcription.text})

        except Exception as e:
            print(f"❌ Fehler bei der Transkription: {str(e)}")  # Fehlermeldung ausgeben
            return JsonResponse({'error': f'Fehler bei der Transkription: {str(e)}'}, status=500)

    print("❌ Ungültige Anfrage - Kein Audio erhalten")
    return JsonResponse({'error': 'Ungültige Anfrage'}, status=400)

