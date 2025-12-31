from flask import Flask, request, current_app
from config import Config
from app.extensions import db, login_manager, socketio, cache, executor, babel
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)
    executor.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # Configure Logging
    configure_logging(app)

    # Import models
    from app import models

    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

def configure_logging(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/minimax_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('MiniMax TTS startup')

def get_locale():
    locale = request.args.get('lang')
    if locale:
        return locale
    return request.accept_languages.best_match(['en', 'zh'])
