import requests
from .wiki_utills import get_article_content
from .vector_utills import upload_to_vector_store
import json

API_URL = "https://wiki.head-trip.de/api.php"

def get_wiki_articles(session):
    """Ruft alle Artikeltitel aus dem MediaWiki ab."""
    params = {
        "action": "query",
        "list": "allpages",
        "format": "json",
        "aplimit": "max"
    }
    response = session.get(API_URL, params=params)
    data = response.json()

    # **Debugging: API-Antwort ausgeben**
    print(f"📡 MediaWiki API Response: {json.dumps(data, indent=2)}")

    if "query" in data and "allpages" in data["query"]:
        articles = [page["title"] for page in data["query"]["allpages"]]
        print(f"✅ MediaWiki enthält {len(articles)} Artikel: {articles}")
        return articles
    else:
        print("⚠️ Fehler: Keine Artikel im MediaWiki gefunden.")
        return []

def list_vector_store_files(client, vector_store_id):
    """Ruft alle gespeicherten Dateien aus dem Vector Store ab."""
    try:
        file_list = client.files.list()
        filenames = []

        # Durchsuche alle Dateien und extrahiere die Namen wie in delete_article
        for file in file_list.data:
            if file.filename.endswith(".json"):
                filenames.append(file.filename.replace(".json", ""))  # Entferne .json-Endung

        print(f"[DEBUG] Vector Store enthält {len(filenames)} Dateien: {filenames}")
        return filenames

    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der Vector Store Dateien: {e}")
        return []


def check_sync_status(client, vector_store_id, session):
    """Vergleicht den aktuellen Stand des MediaWiki mit dem Vector Store und gibt eine Liste der Unterschiede zurück."""
    print("🔄 Starte Vergleich zwischen MediaWiki und Vector Store...")

    # Abrufen aller Artikel im MediaWiki
    try:
        mediawiki_articles = get_wiki_articles(session)

        print(f"📄 MediaWiki enthält {len(mediawiki_articles)} Artikel.")
    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der MediaWiki-Artikel: {e}")
        return {"status": "error", "message": f"Fehler bei MediaWiki-Abfrage: {e}"}

    # Abrufen aller Dateien im Vector Store
    try:
        vector_store_files = list_vector_store_files(client, vector_store_id)
        print(f"📂 Vector Store enthält {len(vector_store_files)} Dateien.")
    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der Vector Store Dateien: {e}")
        return {"status": "error", "message": f"Fehler bei Vector Store-Abfrage: {e}"}

    # Vergleich der beiden Listen
    missing_in_vector = [title for title in mediawiki_articles if title not in vector_store_files]
    missing_in_wiki = [title for title in vector_store_files if title not in mediawiki_articles]

    # Ausgabe für bessere Nachvollziehbarkeit
    print(f"🔍 Vergleich abgeschlossen: {len(missing_in_vector)} fehlen im Vector Store, {len(missing_in_wiki)} fehlen im MediaWiki.")

    if not missing_in_vector and not missing_in_wiki:
        return {"status": "ok", "message": "📂 MediaWiki und Vector Store sind synchron!"}

    return {
        "status": "mismatch",
        "missing_in_vector_store": missing_in_vector,
        "missing_in_wiki": missing_in_wiki,
        "message": f"🟢 {len(missing_in_vector)} fehlen im Vector Store, 🟠 {len(missing_in_wiki)} fehlen im MediaWiki."
    }

