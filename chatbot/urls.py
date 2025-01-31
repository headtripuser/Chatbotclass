# chatbot/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


urlpatterns = [
    path('chat/', include('headtripbot.urls')),
]
