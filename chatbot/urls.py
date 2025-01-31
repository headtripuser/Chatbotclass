# chatbot/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Funktion für eine einfache Startseite
def home(request):
    return HttpResponse("<h1>Willkommen beim Chatbot!</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Startseite hinzufügen
    path('chat/', include('headtripbot.urls')),
]
