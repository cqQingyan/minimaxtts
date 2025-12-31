import json
import os
from app import create_app, db
from app.models import User

# Load old config
CONFIG_FILE = 'config.json'

def migrate():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        if User.query.filter_by(username='admin').first():
            print("Admin user already exists.")
            return

        old_password = 'admin'
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    old_password = data.get('admin_password', 'admin')
                    print(f"Found existing admin password configuration.")
            except Exception as e:
                print(f"Error reading config.json: {e}")

        # Create new admin user
        user = User(username='admin')
        user.set_password(old_password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created with password from config (or default 'admin').")

if __name__ == '__main__':
    migrate()
