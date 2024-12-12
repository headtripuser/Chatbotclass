from openai import OpenAI
from event_handler import MyEventHandler
from wiki_utills import login_to_wiki
import os
from config import assistant_id


vector_store_id ="vs_56heQwFcoW60pFQuPCX48O8l"

def main():
    # API-Client und Wiki-Session initialisieren
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    session = login_to_wiki("Matze", "Head$ripyeah")
    vector_store_id ="vs_56heQwFcoW60pFQuPCX48O8l"

    # Thread erstellen
    thread = client.beta.threads.create()
    print(f"Thread erstellt: {thread.id}")

    # EventHandler initialisieren und Stream starten
    handler = MyEventHandler(client, thread.id, session, assistant_id, vector_store_id)

    print("Hallo! Wie kann ich dir helfen? Gib 'exit' ein, um das Programm zu beenden.\n")

    while True:  # Endlosschleife für die Konversation
        # Benutzerinput
        user_message = input("Du: ")

        if user_message.lower() == "exit":  # Beenden der Schleife
            print("Auf Wiedersehen!")
            break

        # Nachricht an den Assistant senden
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        print(f"Nachricht gesendet: {user_message}")

        # Erstelle einen neuen Eventhandler für jeden Stream
        new_handler = MyEventHandler(client, thread.id, session, assistant_id, vector_store_id)

        # Starten des Streamings für die Antwort
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant_id,
                event_handler=new_handler
        ) as stream:
            stream.until_done()  # Warten, bis der Assistant fertig ist


if __name__ == "__main__":
    main()
