from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_executor import Executor
from flask_babel import Babel

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Set login view
socketio = SocketIO(cors_allowed_origins="*")
cache = Cache()
executor = Executor()
babel = Babel()
