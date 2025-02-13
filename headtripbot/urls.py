from django.urls import path
from .views import login_view, logout_view, chatbot_view, chat, transcribe_audio

urlpatterns = [
    path("", login_view, name="login"),  # Startseite → Login-Seite
    path("logout/", logout_view, name="logout"),  # Logout-URL
    path("chatbot/", chatbot_view, name="chatbot"),  # Chatbot-Übersichtsseite
    path("chat/", chat, name="chat"),  # Chat-Interaktion
    path("transcribe/", transcribe_audio, name="transcribe"),
]
