import streamlit as st
from main import initialize_chatbot, send_message  # Importiere deine Funktionen

# Initialisiere den Chatbot (nur einmal)
if "chatbot_initialized" not in st.session_state:
    client, session, thread, vector_store_id = initialize_chatbot()
    st.session_state.client = client
    st.session_state.session = session
    st.session_state.thread = thread
    st.session_state.vector_store_id = vector_store_id
    st.session_state.chatbot_initialized = True
    st.session_state.chat_log = []  # Initialisiere den Chat-Verlauf

    # **Startnachricht hinzufügen***
    st.session_state.chat_log.append(
        {"role": "assistant", "content": "Hey! Wie kann ich dir helfen?"}
    )

st.image("logo.png", width=300)

# Sidebar mit Mikrofon-Button
with st.sidebar:
    st.markdown("### Optionen")
    if st.button("🎤 Mikrofon starten", help="Sprachaufnahme starten"):
        st.info("Mikrofon-Button geklickt! Hier könnte die Aufnahme gestartet werden.")

# Callback-Funktion für das Senden der Nachricht
def send_user_message():
    user_message = st.session_state.user_input.strip()
    if user_message:
        # 1. Benutzer-Nachricht zum Chat-Verlauf hinzufügen
        st.session_state.chat_log.append({"role": "user", "content": user_message})

        # Zeige einen Spinner während der Bot-Antwort generiert wird
        with st.spinner("Bitte warten..."):
            # 2. Chatbot-Antwort generieren
            bot_response = send_message(
                st.session_state.client,
                st.session_state.session,
                st.session_state.thread,
                st.session_state.vector_store_id,
                user_message,
            )

        # 3. Antwort des Chatbots zum Chat-Verlauf hinzufügen
        st.session_state.chat_log.append({"role": "assistant", "content": bot_response})

        # 4. Eingabefeld leeren
        st.session_state.user_input = ""

# Chat-Nachrichten anzeigen
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Schreiben Sie Ihre Nachricht:"):
    # Benutzer-Nachricht anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)

    # Spinner anzeigen, bis die erste Antwort kommt
    with st.chat_message("assistant"):  # Bot Avatar bleibt hier
        response_placeholder = st.empty()  # Platzhalter für die gestreamte Nachricht
        bot_response = ""  # Speichert die gestreamte Nachricht

        with st.spinner("Der Assistent denkt nach..."):  # Spinner bis zum Start des Streams
            for partial_response in send_message(
                st.session_state.client,
                st.session_state.session,
                st.session_state.thread,
                st.session_state.vector_store_id,
                user_input,
            ):
                bot_response = partial_response  # Aktualisierte Nachricht
                response_placeholder.markdown(bot_response)  # Live-Update der Nachricht

    # Bot-Antwort zum Chat-Verlauf hinzufügen
    st.session_state.chat_log.append({"role": "user", "content": user_input})
    st.session_state.chat_log.append({"role": "assistant", "content": bot_response})
