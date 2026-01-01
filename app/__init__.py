from flask import Flask
import logging
from .config import config_manager
from .routes import main
from .logging_config import JSONFormatter

def create_app():
    # Configure logging
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    app = Flask(__name__)
    app.register_blueprint(main)
    return app
