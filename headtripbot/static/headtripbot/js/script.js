let mediaRecorder;
let audioChunks = [];
let isRecording = false; // Variable zur Verfolgung des Aufnahmezustands
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

function adjustLayout() {
  const chatHistory = document.querySelector('.chat-history');
  const headerHeight = document.querySelector('.chat-header').offsetHeight;
  const inputHeight = document.querySelector('.chat-message').offsetHeight;
  const windowHeight = window.innerHeight;

  chatHistory.style.height = `${windowHeight - headerHeight - inputHeight - 20}px`;
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Initial und bei Größenänderung anpassen
window.addEventListener('resize', adjustLayout);
window.addEventListener('orientationchange', adjustLayout);
adjustLayout();

// Bei Fokus auf das Eingabefeld
document.getElementById('userInput').addEventListener('focus', () => {
  setTimeout(() => {
    adjustLayout();
    window.scrollTo(0, document.body.scrollHeight);
  }, 300);
});

// **🎤 Aufnahme starten oder stoppen**
async function startRecording() {
    if (isRecording) {
        // Aufnahme beenden
        mediaRecorder.stop();
        isRecording = false;
        chatInput.placeholder = "Enter text here..."; // Placeholder zurücksetzen
        recordButton.innerHTML = '<i class="fa fa-microphone"></i>'; // 🎤 Mikrofon-Icon
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;

        chatInput.placeholder = "Bitte jetzt sprechen . . . erneutes Drücken beendet die Eingabe."; // Ändere den Placeholder-Text

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            isRecording = false;
            chatInput.placeholder = "Enter text here..."; // Placeholder nach Aufnahme zurücksetzen

            const mimeType = mediaRecorder.mimeType || 'audio/webm';
            let audioBlob = new Blob(audioChunks, { type: mimeType });

            console.log("📂 Gesendeter Datei-Typ:", audioBlob.type);
            console.log("📂 Größe der Datei:", audioBlob.size);

            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('csrfmiddlewaretoken', getCSRFToken());

            try {
                const response = await fetch('/transcribe/', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.transcription) {
                    console.log("✅ Transkription erfolgreich:", data.transcription);
                    chatInput.value = data.transcription; // Eingabetext mit der transkribierten Nachricht ersetzen
                } else {
                    let errorMsg = data.error_message || data.error || "Unbekannter Fehler";
                    console.error("❌ Transkription fehlgeschlagen:", errorMsg);
                    displayErrorMessage(errorMsg);
                }
            } catch (error) {
                console.error("❌ Fehler beim Senden der Audio-Datei:", error);
                displayErrorMessage("Fehler bei der Transkription: Verbindung fehlgeschlagen.");
            }

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

// 💡 Funktion, um die Fehlermeldung direkt im Chat-Feld anzuzeigen
function displayErrorMessage(message) {
    const messages = document.getElementById('messages');
    const chatHistory = document.querySelector('.chat-history');

    const errorMessage = document.createElement("li");
    errorMessage.classList.add("clearfix", "bot-message");
    errorMessage.innerHTML = `
        <div class="message-data">
            <div class="message my-message">
                <div class="bot-avatar">ht</div>
                <div class="message-text" style="color: red;">
                    ❌ ${message}
                </div>
            </div>
        </div>
    `;
    messages.appendChild(errorMessage);
    chatHistory.scrollTop = chatHistory.scrollHeight;
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

    // **Nachricht an den Server senden**
    fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
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
