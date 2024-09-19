# app.py
import chromadb
from flask import Flask
from dotenv import load_dotenv
from flask_socketio import SocketIO
from source.routes import configure_routes  # Importamos las rutas
from source.FileVectorizationModule import FileVectorizationModule

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey!"
socketio = SocketIO(app)

chroma_client = chromadb.Client()
vectorization_module = FileVectorizationModule(chroma_client)
    
# Ruta al archivo que deseas procesar
file_path = 'files/Encomiendas_Express-B.pdf'
    
# Procesar y vectorizar el archivo
vectorization_module.process_file(file_path)

configure_routes(app, socketio)

if __name__ == "__main__":
    socketio.run(app, debug=True)