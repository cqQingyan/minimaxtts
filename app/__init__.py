from flask import Flask
from .config import config_manager
from .routes import main

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    return app
