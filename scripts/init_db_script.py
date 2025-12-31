from app import create_app, db
from app.models import User
import os

app = create_app()

def init_db():
    if os.path.exists('app.db'):
        os.remove('app.db')
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == '__main__':
    init_db()
