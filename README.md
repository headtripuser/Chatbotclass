# **Dokumentation Chatbot Matze 25.02.25**

## **Inhaltsverzeichnis**

1. [**Einleitung**](#1-einleitung)
   - [Projektname](#11-projektname)
   - [Ziel](#12-ziel)
   - [Zielgruppe](#13-zielgruppe)
   - [Kurzüberblick](#14-kurzuberblick)
2. [**Technischer Überblick**](#2-technischer-uberblick)
   - [Architektur](#21-architektur)
   - [Hauptkomponenten](#23-hauptkomponenten)
     - [Backend](#231-backend)
     - [Frontend](#232-frontend)
     - [Datenquelle](#233-datenquelle)
   - [Datenfluss](#24-datenfluss)
3. [**OpenAI API-Dokumentation**](#5-api-dokumentation)
   - [Endpunkte & Methoden](#51-endpunkte-methoden)
   - [Beispielanfragen und Antworten](#52-beispielanfragen-und-antworten)
4. [**Installation & Setup**](#3-installation--setup)
   - [Voraussetzungen](#31-voraussetzungen)
   - [Installation](#32-installation)
   - [Umgebungsvariablen](#33-umgebungsvariablen)
   - [Starten des Chatbots](#34-starten-des-chatbots)
5. [**Deployment & Wartung**](#8-deployment-wartung)
   - [Hosting](#81-hosting)
   - [Backup](#82-backup)
6. [**Zukunftspläne & Erweiterungen**](#9-zukunftsplaene-erweiterungen)
   - [Mögliche Verbesserungen](#91-moegliche-verbesserungen)
   - [Langfristige Wartung & Skalierung](#92-langfristige-wartung-skalierung)


## **1. Einleitung**


### **1.1 Projektname**
Das Projekt ist in **Python** geschrieben und nutzt das **Django Web-Framework**. Der Chatbot **Kolek Steve** verwendet die **OpenAI API** und **MediaWiki**, um Fragen zu **Headtrip** zu beantworten. Zudem kann er Artikel im **Headtrip-Wikipedia** erstellen, bearbeiten, formatieren und löschen. Dies ermöglicht eine einfache Handhabung über den Chat.

### **1.2 Ziel**
Kolek Steve soll das in Vergessenheit geratene **Wikipedia von Headtrip Immersive Media GmbH** wiederbeleben. Mitarbeiter können damit Strukturen und Prozesse dokumentieren und für alle zugänglich machen. Ziel ist es, eine benutzerfreundliche Plattform zur **Wissenssammlung und -weitergabe** zu schaffen.

### **1.3 Zielgruppe**
Die Hauptnutzer sind die **Mitarbeiter von Headtrip**, die mit dem Chatbot eine gemeinsame **Wissensdatenbank** aufbauen sollen.

### **1.4 Kurzüberblick**
Der Chatbot ist eine **Web-Applikation**, die auf der **OpenAI API** basiert. Sie analysiert Nutzeranfragen und ruft je nach Bedarf unterschiedliche Funktionen auf. Die Daten werden in einem **Vector Store** gespeichert, wodurch eine **intelligente Suche** gewährleistet wird. Hauptfunktionen:
- Antworten aus dem **Headtrip Wikipedia** generieren
- Neue **Artikel erstellen**
- Artikel **bearbeiten**
- Artikel **löschen**
- Artikel **formatieren**

---

## **2. Technischer Überblick** {#2-technischer-uberblick}

### **2.1 Architektur**
Der Chatbot basiert auf dem **Django Web Framework** und folgt der **MVC-Architektur** (Model-View-Controller), implementiert als **MVT-Muster** (Model-View-Template).

- **Model**: Verwaltet die **Datenbank**
- **View**: Verarbeitet **Benutzereingaben** und gibt **HTTP-Responses** zurück
- **Template**: Rendern der HTML-Seiten mit **DTL (Django Template Language)**

Das Projekt enthält mehrere **Django-Apps**, u.a.:
- `chatbot`: Enthält allgemeine Einstellungen
- `headtripbot`: Kernfunktionen des Chatbots (Kommunikation mit **OpenAI** und **MediaWiki**)

### **2.2 Ordnerstruktur**
```
Chatbotclass
├── .venv
├── chatbot
│   ├── settings.py
│   ├── urls.py
├── headtripbot
│   ├── views.py
│   ├── models.py
│   ├── main.py
│   ├── event_handler.py
│   ├── wiki_utils.py
├── staticfiles
│   ├── headtripbot
│   ├── images
│   ├── css
├── db.sqlite3
├── manage.py
├── requirements.txt
```



#### **2.3.1 Backend**
Das Backend läuft über **Python** in der `headtripbot`-App und enthält folgende Kernmodule:

- `views.py`: Empfängt Anfragen, verarbeitet sie und leitet sie an den `event_handler.py` weiter.
- `event_handler.py`: Kernsteuerung, verarbeitet Nachrichten von **OpenAI**.
- `main.py`: Initialisiert den **OpenAI-Client**, die **Wiki-Session** und ist für das Senden sowie das Empfangen von Nachrichten verantwortlich.
- `wiki_utils.py`: Schnittstelle zur **MediaWiki API**.

#### **Ablauf einer Benutzerinteraktion**
1. Benutzer gibt eine Nachricht ein
2. `views.py` verarbeitet die Anfrage und sendet sie an OpenAI
3. `event_handler.py` empfängt die Antwort
4. Falls notwendig, werden Aktionen im **MediaWiki** ausgeführt
5. Die Antwort wird ans **Frontend** zurückgegeben

#### **Code-Ausschnitt: Nachricht an OpenAI senden**
```python
client.beta.threads.messages.create(
   thread_id=thread.id,
   role="user",
   content=user_message
)
```

### **2.3 Hauptkomponenten**

## **Event Handling**

### `on_event(self, event)`

Diese Methode verarbeitet eingehende Events und steuert deren Reaktion:

- **`thread.message.delta`**\
  → Verarbeitet Textantworten, indem der Assistent Nachrichtendeltas sendet.\
  → Speichert empfangenen Text in `latest_response` und gibt ihn in Echtzeit aus.

- **`thread.message.completed`**\
  → Signalisiert das Ende einer Nachricht und gibt einen Zeilenumbruch aus.

- **`thread.run.requires_action`**\
  → Erkennt, wenn eine Aktion erforderlich ist (z. B. das Bearbeiten eines Wiki-Artikels).\
  → Leitet an `handle_requires_action()` weiter.

---

## **Bearbeitung von Aktionen**

### `handle_requires_action(self, data, run_id)`

```python
def handle_requires_action(self, data, run_id):
```

Diese Methode verarbeitet benötigte Aktionen basierend auf dem Tool-Aufruf.\
Sie unterstützt drei Funktionen für die MediaWiki-Verwaltung:

1. **Artikel erstellen** (`create_article_and_json`)

   ```python
   result = create_article(title, content, self.session, self.client, self.vector_store_id)
   ```

   - Erstellt einen neuen Artikel mit `title` und `content`.
   - Speichert das Ergebnis und gibt einen Link zum Artikel aus.

2. **Artikel bearbeiten** (`edit_article`)

   ```python
   result = edit_article(title, user_request, self.session, self.client, self.vector_store_id)
   ```

   - Bearbeitet einen bestehenden Artikel basierend auf `user_request`.
   - Gibt eine Bestätigung mit einem Link zum bearbeiteten Artikel aus.

3. **Artikel löschen** (`delete_article`)

   ```python
   result = delete_article(title, self.client, self.vector_store_id, self.session)
   ```

   - Löscht den Artikel mit dem angegebenen `title`.
   - Gibt eine Erfolgsmeldung oder einen Fehler zurück.

**Allgemeine Fehlerbehandlung:**

- Falls die erforderlichen Parameter (`title`, `content`, `user_request`) fehlen, wird eine Fehlermeldung zurückgegeben.
- Nicht erkannte Tool-Aufrufe werden mit einer Fehlermeldung abgefangen.

---

## **Tool-Outputs senden** (Siehe OpenAI Konfigurationen)

### `submit_tool_outputs(self, tool_outputs, run_id)`

```python
def submit_tool_outputs(self, tool_outputs, run_id):
```

- Sendet die generierten Tool-Outputs an den OpenAI-Client.
- Gibt eine Debug-Meldung mit dem neuen Run-Status aus.



# Wiki Utils Dokumentation

## **1. Einleitung**
`wiki_utils` ist ein Modul zur Interaktion mit einer MediaWiki-API. Es ermöglicht das Anmelden, Erstellen, Bearbeiten, Abrufen und Löschen von Artikeln in einem MediaWiki-System sowie die Verwaltung von zugehörigen Dateien in einem Vektorspeicher.

## **2. Funktionen**

### **2.1 login_to_wiki(username, password)**
**Beschreibung:**
Meldet sich bei der MediaWiki-API mit den angegebenen Zugangsdaten an und gibt eine Sitzung zur weiteren Verwendung zurück.

**Parameter:**
- `username` (str): Benutzername für den Login.
- `password` (str): Passwort für den Login.

**Rückgabewert:**
- `session` (requests.Session): Eine authentifizierte Sitzung.
- `None`, falls der Login fehlschlägt.

---

### **2.2 get_article_content(title, session)**
**Beschreibung:**
Ruft den Inhalt eines MediaWiki-Artikels basierend auf dem Titel ab.

**Parameter:**
- `title` (str): Titel des Artikels.
- `session` (requests.Session): Authentifizierte Sitzung.

**Rückgabewert:**
- `str`: Artikelinhalt, falls gefunden.
- `None`, falls der Artikel nicht existiert oder kein Inhalt gefunden wurde.

---

### **2.3 delete_article(dataname, client, vector_store_id, session)**
**Beschreibung:**
Löscht einen Artikel aus dem MediaWiki, entfernt die zugehörige Datei aus dem OpenAI-Speicher und aus dem Vektorspeicher.

**Parameter:**
- `dataname` (str): Name des zu löschenden Artikels.
- `client` (object): OpenAI-Client-Objekt zur Verwaltung von Dateien.
- `vector_store_id` (str): ID des Vektorspeichers.
- `session` (requests.Session): Authentifizierte Sitzung.

**Rückgabewert:**
- `dict`: Erfolgs- oder Fehlermeldung mit Details.

---

### **2.4 create_article(title, content, session, client, vector_store_id)**
**Beschreibung:**
Erstellt einen neuen Artikel im MediaWiki mit dem angegebenen Inhalt und speichert eine JSON-Version im Vektorspeicher.

**Parameter:**
- `title` (str): Titel des neuen Artikels.
- `content` (str): Inhalt des Artikels.
- `session` (requests.Session): Authentifizierte Sitzung.
- `client` (object): OpenAI-Client-Objekt zur Verwaltung von Dateien.
- `vector_store_id` (str): ID des Vektorspeichers.

**Rückgabewert:**
- `dict`: Erfolgs- oder Fehlermeldung mit Details.

---

### **2.5 edit_article(title, user_request, session, client, vector_store_id)**
**Beschreibung:**
Bearbeitet einen bestehenden Artikel basierend auf einer Benutzeranfrage. Der Artikel wird zuerst gelöscht und dann mit den neuen Inhalten neu erstellt.

**Parameter:**
- `title` (str): Titel des zu bearbeitenden Artikels.
- `user_request` (str): Die vom Benutzer angeforderte Änderung.
- `session` (requests.Session): Authentifizierte Sitzung.
- `client` (object): OpenAI-Client-Objekt zur Verwaltung von Dateien.
- `vector_store_id` (str): ID des Vektorspeichers.

**Rückgabewert:**
- `dict`: Erfolgs- oder Fehlermeldung mit Details.

---

### **2.6 save_article(title, text, session)**
**Beschreibung:**
Speichert den bearbeiteten Artikel im MediaWiki.

**Parameter:**
- `title` (str): Titel des Artikels.
- `text` (str): Neuer Inhalt des Artikels.
- `session` (requests.Session): Authentifizierte Sitzung.


## 3. OpenAI Assistant-Konfiguration

**Assistent:** [Headtrip Assistant](https://platform.openai.com/assistants/asst_KR9HhWRsQXJy63NTFwTVnUe8)

### 1. Assistenten-Einstellungen

- **Name:** Kolek Steve
- **Aufgabe:** Wikipedia-Assistent für Headtrip
- **Modell:** GPT-4o (ursprünglich GPT-3.5 Turbo, aber GPT-4o liefert deutlich bessere Antworten)
- **Kostenüberlegung:** GPT-4o ist leistungsstärker, aber teurer als GPT-3.5 Turbo

### 2. Integrierte OpenAI-Tools

#### **File Search**

- Unterstützt **Keyword-Suche, Indexierung und semantische Suche**
- Nutzt **Retrieval-Augmented Generation (RAG)** für präzisere Antworten
- Ersetzt eigene Suchalgorithmen und reduziert Entwicklungsaufwand

#### **Vector Store**

- Ermöglicht **vektorbasierte Suche mit Embeddings**
- Sucht nicht nach exakten Begriffen, sondern nach inhaltlicher Nähe
- Kombinierbar mit klassischer Stichwortsuche (**Hybride Suche**)

### 3. Function Calling & Mediawiki-Funktionen

Der Assistent nutzt OpenAIs **Function Calling**, um direkt mit der Mediawiki API zu interagieren. Dafür sind drei Funktionen definiert:

#### **1. create\_article\_and\_json**

- **Beschreibung:** Erstellt einen neuen Artikel im Mediawiki mit korrekt formatierter Struktur.
- **Parameter:**
  - `title` (string) → Der Titel des neuen Artikels.
  - `content` (string) → Der Inhalt des Artikels, inklusive Mediawiki-Formatierung.
- **Beispiel:**

```json
{
  "title": "KI in der Medizin",
  "content": "== Einführung ==\nKünstliche Intelligenz revolutioniert das Gesundheitswesen..."
}
```

#### **2. edit\_article**

- **Beschreibung:** Bearbeitet einen existierenden Artikel und wendet Mediawiki-spezifische Formatierung an.
- **Parameter:**
  - `title` (string) → Der Titel des zu bearbeitenden Artikels.
  - `user_request` (string) → Die spezifische Änderung, die durchgeführt werden soll.
- **Beispiel:**

```json
{
  "title": "KI in der Medizin",
  "user_request": "Füge einen neuen Abschnitt über KI-gestützte Diagnosen hinzu."
}
```

#### **3. delete\_article**

- **Beschreibung:** Löscht einen Artikel aus Mediawiki und entfernt die dazugehörige Datei aus dem Vector Store.
- **Parameter:**
  - `title` (string) → Der Titel des zu löschenden Artikels.
- **Beispiel:**

```json
{
  "title": "Veraltete Technologie"
}
```

### 4. Integration in das Backend

- Der Assistent wird über seine **Assistant ID** (`asst_KR9HhWRsQXJy63NTFwTVnUe8`) im Code eingebunden
- Implementiert in `main.py` unter *initialize Chatbot*



---

## **4. Installation & Setup**

# Installationsanleitung für die Chatbotclass Django-App

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass du Folgendes installiert hast:

- Python (>=3.8)
- pip (Python-Paketmanager)
- Git
- Ein Konto bei Render.com

## Lokale Installation

1. **Repository klonen**
   ```bash
   git clone <your-repo-url>
   cd Chatbotclass-master
   ```

2. **Virtuelle Umgebung erstellen und aktivieren**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unter Windows: `venv\Scripts\activate`
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Migrationen anwenden**
   ```bash
   python manage.py migrate
   ```

5. **Entwicklungsserver starten**
   ```bash
   python manage.py runserver
   ```
   Die Anwendung sollte jetzt unter `http://127.0.0.1:8000/` erreichbar sein.

## Deployment auf Render

1. **Projekt auf GitHub hochladen**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Neuen Web-Service auf Render erstellen**
   - Gehe zu [Render](https://dashboard.render.com/) und melde dich an.
   - Klicke auf "New" -> "Web Service".
   - Verbinde dein GitHub-Repository.
   - Wähle den Branch (z. B. `main`).
   - Wähle `Python 3.x` als Laufzeitumgebung.
   
3. **Umgebungsvariablen konfigurieren**
   - Gehe im Render-Dashboard zu "Environment" und füge die benötigten Variablen hinzu, z. B.:
     ```
     DJANGO_SECRET_KEY=dein-geheimer-schlüssel
     DEBUG=False
     ALLOWED_HOSTS=deine-render-url
     ```

4. **Build- und Startbefehle definieren**
   - Build-Befehl: `pip install -r requirements.txt`
   - Start-Befehl: `gunicorn dein_projekt_name.wsgi:application`

5. **Datenbankmigrationen auf Render anwenden**
   - Im "Shell"-Tab von Render ausführen:
     ```bash
     python manage.py migrate
     ```

6. **Zugriff auf die bereitgestellte Anwendung**
   - Sobald das Deployment abgeschlossen ist, ist deine Django-App unter der zugewiesenen Render-URL live.

---
Deine Django-Anwendung wurde erfolgreich auf Render bereitgestellt!


## **5. Hosting auf Render**

Render ist eine Cloud-Plattform für das einfache Hosting von Webanwendungen. Sie bietet automatische Deployments, Skalierung und Monitoring.

## Wichtige Einstellungen

- **Name**: `headtrip-assist`
- **Region**: `Frankfurt (EU Central)`
- **Instance Type**: `Starter (0.5 CPU, 512 MB RAM)`
- **Repository**: [GitHub-Link](https://github.com/Matzecoding/Chatbotclass)
- **Branch**: `master`
- **Build-Befehl**: `pip install -r requirements.txt`
- **Start-Befehl**: `gunicorn --timeout 120 chatbot.wsgi:application --bind 0.0.0.0:8000`
- **Auto-Deploy**: Aktiviert
- **Health Check Path**: `/healthz`

## Umgebungsvariablen

In den "Environment"-Einstellungen müssen folgende Variablen gesetzt werden:
```plaintext
DJANGO_SECRET_KEY=dein-geheimer-schlüssel
DEBUG=False
ALLOWED_HOSTS=chatbotclass-jv31.onrender.com
```

## Logs

Render bietet eine Live-Log-Ansicht, in der man den Status der Anwendung und Fehlermeldungen überprüfen kann. Diese sind im "Logs"-Bereich des Render-Dashboards verfügbar.

## Wartungsmodus

Falls nötig, kann der Wartungsmodus aktiviert werden, um eine statische Wartungsseite anzuzeigen.

## Zugang zur Anwendung

Nach erfolgreichem Deployment ist die Django-Anwendung unter folgender URL erreichbar:
[https://chatbotclass-jv31.onrender.com](https://chatbotclass-jv31.onrender.com)



---


## **6. Zukunftspläne & Erweiterungen**  

### **Datenbankintegration für Chatverläufe**  
Derzeit basiert der Chatbot ausschließlich auf einem Vector Store und verfügt über keine Datenbank. Eine sinnvolle Erweiterung wäre die Implementierung einer Datenbank, die es ermöglicht, Chatverläufe zu speichern und für Benutzer abrufbar zu machen. Da die Anwendung auf der Django-Plattform basiert, sind bereits die notwendigen Strukturen vorhanden, um diese Funktion effizient zu integrieren. 

### **Optimierung der Performance durch asynchrone Verarbeitung**  
Die aktuellen `wiki_utils`-Funktionen sollten in asynchrone Funktionen umgewandelt werden, um die Performance des Chatbots zu verbessern. Zwar ist die Funktionalität bereits gegeben, jedoch leidet die Geschwindigkeit der Anwendung erheblich unter der Verfügbarkeit von OpenAI. Zusätzlich könnte die Implementierung von OpenAI-Streaming helfen, die Wartezeit für Nutzer zu verkürzen und eine flüssigere Interaktion zu ermöglichen.  

### **Integration einer Internetsuche**  
Eine weitere nützliche Erweiterung wäre die Implementierung einer Internetsuche. Dadurch könnte der Chatbot auf aktuelle Informationen zugreifen und sich dynamisch an neue Inhalte anpassen, was seine Einsatzmöglichkeiten erheblich erweitern würde.  



