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

        # 4. Zusätzliche Nachricht bei Funktionsaufrufen hinzufügen
        if "create_article_and_json" in bot_response:  # Beispielprüfung auf Funktionsaufruf
            st.session_state.chat_log.append({
                "role": "system",
                "content": "Der Artikel wurde erfolgreich erstellt und in das System eingepflegt."
            })
        elif "edit_article" in bot_response:
            st.session_state.chat_log.append({
                "role": "system",
                "content": "Der Artikel wurde erfolgreich bearbeitet."
            })
        elif "delete_article" in bot_response:
            st.session_state.chat_log.append({
                "role": "system",
                "content": "Der Artikel wurde erfolgreich gelöscht."
            })

        # 3. Antwort des Chatbots zum Chat-Verlauf hinzufügen
        st.session_state.chat_log.append({"role": "assistant", "content": bot_response})

        # 4. Eingabefeld leeren
        st.session_state.user_input = ""

# CSS für Layout und automatisches Scrollen
st.markdown(
    """
    <style>
    .chat-container {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        max-height: 70vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        border: 1px solid #ddd;
    }
    .chat-container::-webkit-scrollbar {
        width: 5px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background-color: #ccc;
        border-radius: 5px;
    }
    .user-message {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        align-self: flex-end;
        max-width: 80%;
    }
    .bot-message {
        background-color: #e7f3fe;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        align-self: flex-start;
        max-width: 80%;
    }
    </style>
    <script>
    window.onload = () => {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
    };
    </script>
    """,
    unsafe_allow_html=True,
)

# Haupttitel
st.title("Chatbot mit deiner Logik")

# Chat-Container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.chat_log:
    if message["role"] == "user":
        st.markdown(
            f'<div class="user-message">{message["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif message["role"] == "assistant":
        st.markdown(
            f'<div class="bot-message">{message["content"]}</div>',
            unsafe_allow_html=True,
        )
st.markdown("</div>", unsafe_allow_html=True)  # Schließe den Container

# Eingabefeld
user_input = st.text_input(
    "Schreiben Sie Ihre Nachricht:",
    key="user_input",
    on_change=send_user_message,
    placeholder="Nachricht hier eingeben...",
)
