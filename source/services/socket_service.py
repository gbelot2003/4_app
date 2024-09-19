#socket_service.py
from flask_socketio import SocketIO, send
from source.services.openai_service import OpenAIService

socketio = SocketIO()
conversation = OpenAIService()

def init_socketio(app):
    socketio.init_app(app)

    @socketio.on('message')
    def handle_message(msg):
        conversation.add_message('user', msg)
        response = conversation.get_response()    

        send(response, broadcast=True)

    return socketio