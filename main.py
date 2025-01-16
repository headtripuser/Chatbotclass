from openai import OpenAI
from event_handler import MyEventHandler
from wiki_utills import login_to_wiki
import os
from config import assistant_id


def initialize_chatbot():
    """Initialisiert den OpenAI-Client und die Wiki-Session."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    session = login_to_wiki("Matze", "Head$ripyeah")  # Beispiel-Login-Daten
    vector_store_id = "vs_56heQwFcoW60pFQuPCX48O8l"
    thread = client.beta.threads.create()
    return client, session, thread, vector_store_id

def send_message(client, session, thread, vector_store_id, user_message):
    """Sendet eine Nachricht an den Chatbot und empfängt die Antwort stückweise."""
    # Nachricht an den Assistant senden
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # Antwort vom Chatbot streamen
    handler = MyEventHandler(client, thread.id, session, assistant_id, vector_store_id)
    complete_response = ""

    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
            event_handler=handler

    ) as stream:
        for event in stream:
            # Prüfe, ob das Event vom Typ "thread.message.delta" ist
            if event.event == "thread.message.delta":
                delta_content = event.data.delta.content
                for item in delta_content:
                    if item.type == "text":
                        text_chunk = item.text.value
                        complete_response += text_chunk
                        yield complete_response  # Text stückweise zurückgeben



