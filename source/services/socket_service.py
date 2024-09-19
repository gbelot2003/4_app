#socket_service.py
from flask_socketio import SocketIO, send

socketio = SocketIO()

def init_socketio(app):
    socketio.init_app(app)

    @socketio.on('message')
    def handle_message(msg):
        response = msg

        send(response, broadcast=True)

    return socketio