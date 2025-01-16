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

# Chatverlauf und Mikrofon-Button in einem Container
with st.container():
    # Chat-Nachrichten anzeigen
    for message in st.session_state.chat_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Mikrofon-Button unter dem Chatverlauf
    if st.button("🎤 Mikrofon", help="Sprachaufnahme starten"):
        st.info("Mikrofon-Button geklickt! Hier könnte die Aufnahme gestartet werden.")

# Eingabefeld am unteren Ende
if user_input := st.chat_input("Schreiben Sie Ihre Nachricht:"):
    # Benutzer-Nachricht anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)

    # Spinner anzeigen, während der Chatbot antwortet
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # Platzhalter für die Antwort
        bot_response = ""  # Variable für die gesamte Antwort

        with st.spinner("Der Assistent denkt nach..."):  # Spinner während der Verarbeitung
            bot_response = send_message(
                st.session_state.client,
                st.session_state.session,
                st.session_state.thread,
                st.session_state.vector_store_id,
                user_input
            )

        # Zeige die vollständige Antwort im Chatfenster an
        response_placeholder.markdown(bot_response)

    # Chat-Verlauf aktualisieren
    st.session_state.chat_log.append({"role": "user", "content": user_input})
    st.session_state.chat_log.append({"role": "assistant", "content": bot_response})
