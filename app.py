# app.py
from flask import Flask
from dotenv import load_dotenv
from flask_socketio import SocketIO
from source.routes import configure_routes  # Importamos las rutas

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey!"
socketio = SocketIO(app)

configure_routes(app, socketio)

if __name__ == "__main__":
    socketio.run(app)