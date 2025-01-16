import streamlit as st
from main import initialize_chatbot, send_message  # Importiere deine Funktionen
from event_handler import MyEventHandler

# Initialisiere den Chatbot (nur einmal)
if "chatbot_initialized" not in st.session_state:
    client, session, thread, vector_store_id = initialize_chatbot()
    st.session_state.client = client
    st.session_state.session = session
    st.session_state.thread = thread
    st.session_state.vector_store_id = vector_store_id
    st.session_state.chatbot_initialized = True
    st.session_state.chat_log = []  # Initialisiere den Chat-Verlauf
    st.session_state.assistant_id = "asst_KR9HhWRsQXJy63NTFwTVnUe8"

    # **Startnachricht hinzufügen***
    st.session_state.chat_log.append(
        {"role": "assistant", "content": "Hey! Wie kann ich dir helfen?"}
    )

st.image("logo.png", width=300)

# Chatverlauf und Mikrofon-Button in einem Container
with st.container():
    # Chat-Nachrichten anzeigen
    for message in st.session_state.chat_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Mikrofon-Button unter dem Chatverlauf
    if st.button("🎤 Mikrofon", help="Sprachaufnahme starten"):
        st.info("Mikrofon-Button geklickt! Hier könnte die Aufnahme gestartet werden.")
if user_input := st.chat_input("Schreiben Sie Ihre Nachricht:"):
    # Benutzer-Nachricht anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)

    # Spinner anzeigen, während der Chatbot antwortet
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        bot_response = ""

        # Event-Handler erstellen
        handler = MyEventHandler(
            st.session_state.client,
            st.session_state.thread.id,
            st.session_state.session,
            st.session_state.assistant_id,
            st.session_state.vector_store_id
        )

        with st.spinner("Der Assistent denkt nach..."):
            for partial_response in send_message(
                st.session_state.client,
                st.session_state.session,
                st.session_state.thread,
                st.session_state.vector_store_id,
                user_input,
                handler
            ):
                bot_response = partial_response
                response_placeholder.markdown(bot_response)

        # Prüfen, ob `self.latest_response` genutzt werden soll
        if not bot_response and handler.latest_response:
            bot_response = handler.latest_response
            response_placeholder.markdown(bot_response)

    # Chat-Verlauf aktualisieren
    st.session_state.chat_log.append({"role": "user", "content": user_input})
    st.session_state.chat_log.append({"role": "assistant", "content": bot_response})
