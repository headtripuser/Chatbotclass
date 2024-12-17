import streamlit as st
from main import initialize_chatbot, send_message

# Initialisiere den Chatbot (nur einmal)
if "chatbot_initialized" not in st.session_state:
    client, session, thread, vector_store_id = initialize_chatbot()
    st.session_state.client = client
    st.session_state.session = session
    st.session_state.thread = thread
    st.session_state.vector_store_id = vector_store_id
    st.session_state.chatbot_initialized = True
    st.session_state.chat_log = []
    st.session_state.chat_log.append({"role": "assistant", "content": "Hey! Wie kann ich dir helfen?"})

st.image("logo.png", width=300)

# Chat-Nachrichten anzeigen
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mikrofon-Button immer anzeigen
mic_button_container = st.empty()
mic_button_container.markdown("""
    <style>
    .mic-button {
        position: fixed;
        bottom: 50px;
        right: 550px;
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
    }
    </style>
    <button class="mic-button">🎤</button>
    """, unsafe_allow_html=True)

# Benutzer-Eingabe verarbeiten
if user_input := st.chat_input("Schreiben Sie Ihre Nachricht:"):
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        bot_response = ""

        with st.spinner("Der Assistent denkt nach..."):
            for partial_response in send_message(
                st.session_state.client,
                st.session_state.session,
                st.session_state.thread,
                st.session_state.vector_store_id,
                user_input,
            ):
                bot_response = partial_response
                response_placeholder.markdown(bot_response)

    st.session_state.chat_log.append({"role": "user", "content": user_input})
    st.session_state.chat_log.append({"role": "assistant", "content": bot_response})

    # Mikrofon-Button erneut rendern
    mic_button_container.markdown("""
    <style>
    .mic-button {
        position: fixed;
        bottom: 50px;
        right: 550px;
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
    }
    </style>
    <button class="mic-button">🎤</button>
    """, unsafe_allow_html=True)
