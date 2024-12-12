import streamlit as st
from main import main  # Importiere deine Chatbot-Logik

st.title("Chatbot UI")

# Session State für die Chat-Logs initialisieren
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# Eingabefeld für Benutzer*innen und so
user_input = st.text_input("Enter your message:", key="user_input")

if st.button("Send"):
    if user_input:
        # Benutzer-Message anzeigen
        st.session_state.chat_log.append({"role": "user", "content": user_input})

        # Chatbot-Antwort abrufen
        response = main(user_input)
        st.session_state.chat_log.append({"role": "assistant", "content": response})

# Chatlog rendern
for message in st.session_state.chat_log:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")
