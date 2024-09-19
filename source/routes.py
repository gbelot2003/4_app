# routes.py
from flask import render_template, request
from flask_socketio import send
from source.services.socket_service import init_socketio

def configure_routes(app, socketio):
    # Ruta para el home
    @app.route("/",  methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            return render_template("index.html")
        return render_template("index.html")
    # Inicializar socketio con los servicios
    init_socketio(app)