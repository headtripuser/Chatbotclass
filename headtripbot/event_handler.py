from openai import AssistantEventHandler
import json
from .wiki_utills import edit_article, create_article, delete_article


class MyEventHandler(AssistantEventHandler):
    def __init__(self, client, thread_id, session, assistant_id, vector_store_id):
        super().__init__()
        self.client = client
        self.thread_id = thread_id
        self.session = session
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id
        self.latest_response = ""
        self.last_function_called = None  # Speichert die zuletzt aufgerufene Funktion
        self.last_function_result = None  # Speichert das Ergebnis der letzten Funktion

    def on_event(self, event):
        if event.event == "thread.message.delta":
            # Extrahiere den Text aus dem Delta
            delta_content = event.data.delta.content
            for item in delta_content:
                if item.type == "text":  # Direkt auf das Attribut zugreifen
                    self.latest_response += item.text.value
                    message_text = item.text.value  # Zugriff auf das 'value'-Attribut von TextDelta
                    print(item.text.value, end="", flush=True)  # Streamt die Nachricht fließend ohne Zeilenumbruch

        elif event.event == "thread.message.completed":
            # Nachricht vollständig: füge einen Zeilenumbruch hinzu
            print("\n")  # Zeilenumbruch nach abgeschlossener Nachricht

        elif event.event == "thread.run.requires_action":
            run_id = event.data.id
            print(f"[DEBUG] Run benötigt Aktion: {run_id}")
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        print(f"[DEBUG] Bearbeite erforderliche Aktion für Run: {run_id}")
        print(self.assistant_id)
        tool_outputs = []

        for tool_call in data.required_action.submit_tool_outputs.tool_calls:
            # Die Argumente aus dem Tool-Call extrahieren
            arguments = json.loads(tool_call.function.arguments)
            title = arguments.get("title", "")
            content = arguments.get("content", "")  # Für create_article_and_json
            user_request = arguments.get("user_request", "")  # Für edit_article

            print(
                f"[DEBUG] Tool-Call: {tool_call.function.name}, für Title: {title}, Content: {content}, User Request: {user_request}")

            # Logik basierend auf der Funktion
            if tool_call.function.name == "create_article_and_json":
                self.last_function_called = "create_article_and_json"
                if title and content:
                    print(f"[DEBUG] Erstelle neuen Artikel: {title} mit Inhalt: {content}")
                    result = create_article(title, content, self.session, self.client, self.vector_store_id)
                    self.latest_response = f"Der Artikel {title} wurde mit folgendem Content: \n  {content} \n erstellt."
                else:
                    result = {"success": False, "message": "Titel oder Inhalt fehlen für die Erstellung des Artikels."}

            elif tool_call.function.name == "edit_article":
                self.last_function_called = "edit_article"
                if title and user_request:
                    print(f"[DEBUG] Bearbeite Artikel: {title} mit Anfrage: {user_request}")
                    result = edit_article(title, user_request, self.session, self.client, self.vector_store_id)
                    self.latest_response = f"Der Artikel {title} wurde erfolgreich bearbeitet."
                else:
                    result = {"success": False,
                              "message": "Titel oder Benutzeranfrage fehlen für die Bearbeitung des Artikels."}

            elif tool_call.function.name == "delete_article":
                self.last_function_called = "delete_article"
                if title:
                    print(f"Lösche Artikel mit dem Titel {title}...")
                    result = delete_article(title, self.client, self.vector_store_id, self.session)
                    self.latest_response = f"Der Artikel {title} wurde erfolgreich gelöscht."
                else:
                    result = {"success": False, "message": "Titel fehlt für die Löschung des Artikels."}

            else:
                self.last_function_called = "unknown"
                result = {"success": False, "message": f"Unbekannte Funktion: {tool_call.function.name}"}

            # Speichere das Ergebnis der letzten Funktion
            self.last_function_result = result

            # Tool-Output sammeln
            tool_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(result)})

        # Tool-Outputs abschicken
        if tool_outputs:
            self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        print(f"[DEBUG] Sende Tool-Outputs für Run: {run_id}")
        response = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        print(f"[DEBUG] Tool-Outputs erfolgreich übermittelt. Neuer Run-Status: {response.status}")