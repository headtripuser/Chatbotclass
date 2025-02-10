let mediaRecorder;
let audioChunks = [];
const recordButton = document.getElementById('record-button');
const chatInput = document.getElementById('userInput');
const status = document.getElementById('record-status');

// **🔄 Button zwischen Mikrofon & Papierflieger wechseln**
chatInput.addEventListener('input', () => {
    if (chatInput.value.trim() === "") {
        recordButton.innerHTML = '<i class="fa fa-microphone"></i>'; // 🎤 Mikrofon-Icon
        recordButton.onclick = startRecording; // Aufnahme starten
    } else {
        recordButton.innerHTML = '<i class="fa fa-paper-plane"></i>'; // 📨 Papierflieger-Icon
        recordButton.onclick = sendMessage; // Nachricht senden
    }
});

// **🔄 Automatische Anpassung der Textarea-Höhe**
function adjustTextareaHeight() {
    chatInput.style.height = "40px"; // Zurücksetzen, um richtige Höhe zu berechnen
    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + "px"; // Begrenzung auf max. 150px
}

// **📌 Event Listener für Eingaben im Textfeld**
chatInput.addEventListener("input", adjustTextareaHeight);


// **🔄 Enter-Taste für Nachrichtensenden aktivieren**
chatInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Verhindert den Zeilenumbruch
        sendMessage(); // Nachricht absenden
    }
});


// **🎤 Aufnahme starten oder stoppen**
async function startRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordButton.innerHTML = '<i class="fa fa-microphone"></i>'; // 🎤 Zurück zu Mikrofon
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    try {
        const response = await fetch('/transcribe/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.transcription) {
            chatInput.value = data.transcription;

            // **Fix: Simuliere Benutzereingabe, damit sich der Button ändert**
            chatInput.dispatchEvent(new Event('input'));
        } else {
            chatInput.value = "Fehler bei der Transkription.";
        }

    } catch (error) {
        console.error("Fehler bei der Transkription:", error);
        chatInput.value = "Fehler bei der Transkription.";
    }

    // **🔄 Button aktualisieren basierend auf Eingabefeld**
    if (chatInput.value.trim() !== "") {
        recordButton.innerHTML = '<i class="fa fa-paper-plane"></i>'; // 📨 Papierflieger-Icon
        recordButton.onclick = sendMessage;
    } else {
        recordButton.innerHTML = '<i class="fa fa-microphone"></i>'; // 🎤 Mikrofon-Icon
        recordButton.onclick = startRecording;
    }
};


        mediaRecorder.start();
        recordButton.innerHTML = '<i class="fa fa-stop"></i>'; // ⏹ Stop-Icon während Aufnahme

    } catch (err) {
        console.error("🚨 Fehler beim Mikrofonzugriff:", err);
        status.textContent = "Mikrofonzugriff verweigert!";
    }
}

// **📨 Nachricht senden**
function sendMessage() {
    const userInput = chatInput.value.trim();
    if (!userInput) return;

    const messages = document.getElementById('messages');
    const chatHistory = document.querySelector('.chat-history');

    // **Benutzernachricht direkt in den Chat einfügen**
    const userMessage = document.createElement("li");
    userMessage.classList.add("clearfix");
    userMessage.innerHTML = `
        <div class="message other-message float-right">${userInput.replace(/\n/g, '<br>')}</div>
    `;
    messages.appendChild(userMessage);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // **Ladeanimation direkt NACH der User-Nachricht einfügen**
    const loadingIndicator = document.createElement("li");
    loadingIndicator.classList.add("clearfix", "bot-message");
    loadingIndicator.innerHTML = `
        <div class="message-data">
            <div class="message my-message">
                <div class="bot-avatar">ht</div>
                <div class="message-text">
                    <span class="typing-indicator"></span>
                </div>
            </div>
        </div>
    `;
    messages.appendChild(loadingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // **Nachricht an den Server senden**
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // **Ladeanimation entfernen**
        messages.removeChild(loadingIndicator);

        if (data.response) {
            // **Bot-Nachricht nach der Animation einfügen**
            const botMessage = document.createElement("li");
            botMessage.classList.add("clearfix");
            botMessage.innerHTML = `
                <div class="message-data">
                    <div class="message my-message">
                        <div class="bot-avatar">ht</div>
                        <div class="message-text">${data.response.replace(/\n/g, "<br>")}</div>

                    </div>
                </div>
            `;
            messages.appendChild(botMessage);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    })
    .catch(error => {
        console.error("Fehler beim Senden der Nachricht:", error);
        messages.removeChild(loadingIndicator);
    });

    chatInput.value = '';
    chatInput.dispatchEvent(new Event('input'));
}





// **📌 Standard-Button-Zuweisung (Mikrofon als Standard)**
recordButton.innerHTML = '<i class="fa fa-microphone"></i>';
recordButton.onclick = startRecording;

// **💡 Debugging-Logs für Serverantworten**
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}