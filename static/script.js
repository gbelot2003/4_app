// Conexión con el servidor WebSocket
var socket = io();

// Al hacer clic en el botón enviar
document.getElementById('send-btn').addEventListener('click', function() {
    let message = document.getElementById('message').value;
    if (message) {
        socket.send(message);  // Enviar el mensaje al servidor
        addMessageToChat(message, 'user');  // Añadir el mensaje del usuario al chat
        document.getElementById('message').value = '';  // Limpiar el campo
    }
});

// Escuchar mensajes desde el servidor
socket.on('message', function(msg) {
    addMessageToChat(msg, 'other');  // Añadir el mensaje de otros al chat
});

// Función para añadir un mensaje al chat
function addMessageToChat(message, sender) {
    let chatBox = document.getElementById('chat-box');
    let messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);  // Añadir clase 'user' o 'other'
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll automático
}