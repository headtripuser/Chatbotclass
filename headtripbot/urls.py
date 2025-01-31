# headtripbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),  # Startseite der App direkt erreichbar
    path('transcribe/', views.transcribe_audio, name='transcribe'),
]
