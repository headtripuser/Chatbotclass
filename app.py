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

# Callback-Funktion für das Senden der Nachricht
def send_user_message():
    user_message = st.session_state.user_input.strip()
    if user_message:
        # 1. Benutzer-Nachricht zum Chat-Verlauf hinzufügen
        st.session_state.chat_log.append({"role": "user", "content": user_message})

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

# Haupttitel
st.title("headtrip Chatbot")

# Chat-Nachrichten anzeigen
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabefeld
if user_input := st.chat_input("Schreiben Sie Ihre Nachricht:"):
    # Benutzer-Nachricht anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)

    # Nachricht zum Verlauf hinzufügen
    st.session_state.chat_log.append({"role": "user", "content": user_input})

    # Bot-Antwort generieren
    bot_response = send_message(
        st.session_state.client,
        st.session_state.session,
        st.session_state.thread,
        st.session_state.vector_store_id,
        user_input,
    )

    # Bot-Antwort anzeigen
    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # Bot-Antwort zum Verlauf hinzufügen
    st.session_state.chat_log.append({"role": "assistant", "content": bot_response})
