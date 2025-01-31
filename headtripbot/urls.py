from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),  # Bestehender Chat-Endpunkt
    path('transcribe/', views.transcribe_audio, name='transcribe'),  # Neuer Transkriptions-Endpunkt
]
