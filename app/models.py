from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.String(64), index=True) # MiniMax Task ID or Internal UUID
    status = db.Column(db.String(20)) # processing, success, failed
    voice_name = db.Column(db.String(64))
    text_preview = db.Column(db.String(100))
    file_path = db.Column(db.String(256)) # Path to saved audio file
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'voice_name': self.voice_name,
            'text_preview': self.text_preview,
            'created_at': self.created_at.isoformat()
        }
