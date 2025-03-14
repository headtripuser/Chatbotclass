from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import tempfile  # Neu: Temporäre Dateien für Whisper
from .main import initialize_chatbot, send_message
from .event_handler import MyEventHandler
import openai
import os
from .wiki_utills import login_to_wiki  # MediaWiki-Login nutzen
import requests
import subprocess

# Initialisiere den Chatbot (wird nur einmal ausgeführt)
client, thread, vector_store_id = initialize_chatbot()
assistant_id = "asst_KR9HhWRsQXJy63NTFwTVnUe8"

# OpenAI API-Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat(request):
    wiki_session_data = request.session.get("wiki_session")

    if not wiki_session_data:
        return redirect("login")  # Falls keine Session existiert, zurück zur Anmeldung

    # Neue `requests.Session()` erstellen und Cookies setzen
    wiki_session = requests.Session()
    wiki_session.cookies.update(wiki_session_data["cookies"])  # ✅ Jetzt ist es ein echtes `requests.Session()`

    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')

        handler = MyEventHandler(client, thread.id, wiki_session, assistant_id, vector_store_id)

        bot_response = ""
        for partial_response in send_message(client, wiki_session, thread, vector_store_id, user_input, handler):
            bot_response = partial_response

        if not bot_response and handler.latest_response:
            bot_response = handler.latest_response

        return JsonResponse({'response': bot_response})

    return render(request, 'headtripbot/chat.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        session = login_to_wiki(username, password)

        if session:
            # Speichere die Session in der Django-Session
            request.session["wiki_session"] = {"cookies": session.cookies.get_dict()}
            print("Gespeicherte Session:", request.session.get("wiki_session"))
            return redirect("chat")  # Weiterleitung zur Chat-Seite
        else:
            return render(request, "headtripbot/login.html", {"error": "Login fehlgeschlagen!"})

    return render(request, "headtripbot/login.html")

def logout_view(request):
    """Logout und Session beenden"""
    request.session.flush()  # Lösche die Sitzung
    return redirect("login")


def chatbot_view(request):
    """Chatbot-Seite (Nur nach Login erreichbar)"""
    if "wiki_session" not in request.session:
        return redirect("login")  # Falls kein Login, zurück zur Anmeldung
    return render(request, "chatbot.html")

import tempfile
import openai
from django.http import JsonResponse

def convert_audio_to_wav(input_path):
    """ Konvertiert eine Datei in WAV, wenn sie in einem inkompatiblen Format vorliegt """
    output_path = input_path + ".wav"
    try:
        subprocess.run(["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", output_path], check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der Audio-Konvertierung: {e}")
        return None

def transcribe_audio(request):
    """Verarbeitet die Audiodatei und gibt die Transkription zurück."""
    if request.method == 'POST' and 'audio' in request.FILES:
        try:
            audio_file = request.FILES['audio']
            print(f"📂 Erhaltene Datei: {audio_file.name}, Typ: {audio_file.content_type}")

            # Audiodatei in temporäre Datei speichern
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(audio_file.read())
                temp_audio_path = temp_audio.name

            # 🎯 Konvertiere Datei, falls nötig
            converted_path = convert_audio_to_wav(temp_audio_path)
            if not converted_path:
                return JsonResponse({'error_message': 'Fehler bei der Konvertierung der Audiodatei'}, status=500)

            # 📝 Datei für Whisper öffnen
            with open(converted_path, "rb") as file_for_whisper:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=file_for_whisper,
                    language="de"
                )

            print(f"✅ Erfolgreiche Transkription: {transcription.text}")
            return JsonResponse({'transcription': transcription.text})

        except Exception as e:
            print(f"❌ Fehler bei der Transkription: {str(e)}")
            return JsonResponse({'error_message': f'Fehler bei der Transkription: {str(e)}'}, status=500)

    print("❌ Ungültige Anfrage - Kein Audio erhalten")
    return JsonResponse({'error_message': 'Ungültige Anfrage - keine Audiodatei erhalten'}, status=400)
