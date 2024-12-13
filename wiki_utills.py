import requests
import json
from vector_utills import upload_to_vector_store
import os
import time

api_url = 'https://wiki.head-trip.de/api.php'

def login_to_wiki(username, password):
    session = requests.Session()

    # Login-Token abrufen
    login_token_params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    }
    login_token_response = session.get(api_url, params=login_token_params)
    login_token = login_token_response.json()['query']['tokens']['logintoken']

    # Login durchführen
    login_params = {
        'action': 'login',
        'lgname': username,
        'lgpassword': password,
        'lgtoken': login_token,
        'format': 'json'
    }
    login_response = session.post(api_url, data=login_params)
    login_result = login_response.json()

    if login_result['login']['result'] == 'Success':
        print("Login erfolgreich!")
        return session
    else:
        print(f"Login fehlgeschlagen: {login_result}")
        return None


def get_article_content(title, session):
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvslots": "main",
        "rvprop": "content",
        "format": "json"
    }

    response = session.get(api_url, params=params)
    print("API Response:", response.json())  # Logge die API-Response

    pages = response.json().get("query", {}).get("pages", {})
    if pages:
        # Nimm das erste (und einzige) Ergebnis
        page_data = list(pages.values())[0]

        # Überprüfe, ob die Seite fehlt
        if "missing" in page_data:
            print(f"Artikel '{title}' existiert nicht.")
            return None

        # Extrahiere den Inhalt, falls vorhanden
        return page_data.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
    else:
        print("Kein Inhalt gefunden.")
        return None


def delete_article(dataname, client, vector_store_id, session):
    """
    Löscht eine Datei aus dem Vector Store basierend auf ihrem Dateinamen, die generische Datei auf Openai und den
    Artikel aus dem Mediawiki.

    :param client: Der OpenAI-Client.
    :param vector_store_id: Die ID des Vector Stores.
    :param dataname: Der Name der Datei, die gelöscht werden soll.
    :param session: Die aktuelle Session im Mediawiki.
    :return: Das Ergebnis der Löschoperation.
    """
    existing_content = get_article_content(dataname, session)

    if existing_content is None:
        print(f"Es existiert kein Artikel mit dem Titel: '{dataname}'.")

    else:

        try:

            # Liste aller Dateien abrufen
            file_list = client.files.list()

            dataname_with_ext = dataname + ".json"
            # Nach der Datei mit dem passenden Namen suchen
            file_id = None
            for file in file_list.data:
                if file.filename == dataname_with_ext:
                    print("Es wurde ein passender Filename gefunden")
                    file_id = file.id
                    break
            print(f"Die gefundene File_id lautet: {file_id}")

            if not file_id:
                print(f"Es existiert leider keine Datei mit dem Namen: '{dataname}'")


            # Generische Datei löschen
            client.files.delete(file_id)
            print("Generische file-datei wurde gelöscht")

            # Datei aus dem Vector Store löschen
            print(f"Lösche Datei '{dataname}' mit ID '{file_id}' aus dem Vector Store...")
            response = client.beta.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )

            print(f"{dataname} wurde erfolgreich aus dem vector store entfernt.")

            if os.path.exists(dataname_with_ext):
                os.remove(dataname_with_ext)
                print(f"Lokale Datei '{dataname_with_ext}' wurde erfolgreich gelöscht.")

            # Schritt 2: Artikel im MediaWiki löschen
            # Lösch-Token abrufen
            delete_token_params = {
                "action": "query",
                "meta": "tokens",
                "type": "csrf",
                "format": "json"
            }

            delete_token_response = session.get(api_url, params=delete_token_params)
            csrf_token = delete_token_response.json().get("query", {}).get("tokens", {}).get("csrftoken", None)

            if not csrf_token:
                print("CSRF-Token konnte nicht abgerufen werden.")
                return {"success": False, "message": "CSRF-Token nicht verfügbar."}

            # Artikel löschen
            delete_params = {
                "action": "delete",
                "title": dataname,
                "token": csrf_token,
                "format": "json"
            }

            delete_response = session.post(api_url, data=delete_params)

            if delete_response.status_code == 200 and "error" not in delete_response.json():
                print(f"Artikel '{dataname}' wurde erfolgreich aus dem MediaWiki gelöscht.")
            else:
                print(f"Fehler beim Löschen des Artikels: {delete_response.json()}")

            return {"success": True, "message": f"Datei '{dataname}' und Artikel '{dataname}' wurden gelöscht."}


        except Exception as e:
            print(f"Fehler beim Löschen der Datei oder des Artikels: {e}")
            return {"success": False, "message": f"Fehler: {e}"}


def create_article(title, content, session, client, vector_store_id):
    """Erstellt einen neuen Artikel im Wiki mit dem angegebenen Titel und Inhalt."""
    # Bearbeitungstoken abrufen

    existing_content = get_article_content(title, session)


    if existing_content is not None:
        print(f"Ein Artikel mit dem Titel '{title}' existiert bereits.")
        print(f"Inhalt des vorhandenen Artikels:\n{existing_content}")

    else:

        edit_token_params = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        edit_token_response = session.get(api_url, params=edit_token_params)
        edit_token = edit_token_response.json()["query"]["tokens"]["csrftoken"]

        # Artikel erstellen
        create_params = {
            "action": "edit",
            "title": title,
            "text": content,
            "token": edit_token,
            "format": "json"
        }
        response = session.post(api_url, data=create_params)



        # JSON-Datei mit Artikeldaten erstellen
        json_filename = f"{title}.json"
        json_data = {"title": title, "content": content}
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file)

        # Die erstellte Datei dem Vector Store zugänglich machen und hochladen:
        upload_to_vector_store(client, vector_store_id,json_filename)

        if response.status_code != 200 or "error" in response.json():
            return {"success": False, "message": f"Fehler beim Erstellen des Artikels: {response.json()}"}




def edit_article(title, user_request, session, client, vector_store_id):
    """Bearbeitet den Inhalt eines existierenden Artikels."""
    # 1. Artikelinhalt abrufen
    print(f"Rufe Artikel '{title}' ab...")
    current_content = get_article_content(title, session)
    if not current_content:
        return {"success": False, "message": f"Artikel '{title}' nicht gefunden."}

    # 2. System-Prompt erstellen
    system_prompt = (
        f"Bearbeite den folgenden Artikel basierend auf der Benutzeranfrage. "
        f"Gib nur den aktualisierten Artikelinhalt zurück, ohne zusätzliche Kommentare:\n\n"
        f"Artikelinhalt:\n{current_content}\n\n"
        f"Benutzeranfrage: {user_request}"
    )

    try:
        # Anfrage an den Chat Completion Endpunkt
        print("Sende Anfrage an den OpenAI-Chat Completion Endpunkt...")
        response = client.chat.completions.create(
            model="gpt-4",  # Modell auswählen (ggf. anpassen)
            messages=[
                {"role": "system", "content": "Du bist ein Assistent, der Artikel bearbeitet."},
                {"role": "user", "content": system_prompt}
            ]
        )
        assistant_output = response.choices[0].message.content.strip()


        if not assistant_output:
            return {"success": False, "message": "Keine Antwort vom Assistant erhalten."}

        # Aktuallisieren des Vector_stores
        delete_article(title, client, vector_store_id, session)

        create_article(title, assistant_output, session, client, vector_store_id)

        # 3. Speichern des neuen Artikels
        print("Speichere die Änderungen im Wiki...")
        save_response = save_article(title, assistant_output, session)

        if save_response.get("edit", {}).get("result") == "Success":
            return {"success": True, "message": f"Artikel '{title}' erfolgreich bearbeitet."}
        else:
            return {"success": False, "message": f"Fehler beim Bearbeiten des Artikels: {save_response}"}


    except Exception as e:
        print(f"Fehler bei der Bearbeitung: {e}")
        return {"success": False, "message": f"Fehler bei der Bearbeitung: {e}"}



def save_article(title, text, session):
    """Speichert den bearbeiteten Artikel im MediaWiki."""
    try:
        # Bearbeitungstoken abrufen
        edit_token_params = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        edit_token_response = session.get(api_url, params=edit_token_params)
        edit_token = edit_token_response.json().get('query', {}).get('tokens', {}).get('csrftoken', None)
        if not edit_token:
            return {"success": False, "message": "Bearbeitungstoken konnte nicht abgerufen werden."}

        # Artikel speichern
        params = {
            "action": "edit",
            "title": title,
            "text": text,
            "token": edit_token,
            "format": "json"
        }
        response = session.post(api_url, data=params)

        # Erfolgsprüfung
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": f"Fehler beim Speichern: {response.text}"}

    except Exception as e:
        return {"success": False, "message": f"Ein Fehler ist aufgetreten: {e}"}
