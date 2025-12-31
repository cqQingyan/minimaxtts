from app import create_app, socketio, db
import os

app = create_app()

def init_db():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print("Database initialized automatically.")

            # Optional: Create default admin if not exists
            from app.models import User
            if not User.query.filter_by(username='admin').first():
                 u = User(username='admin')
                 u.set_password('admin')
                 db.session.add(u)
                 db.session.commit()
                 print("Default admin user created.")

if __name__ == '__main__':
    init_db()
    # In production, use Gunicorn/uWSGI with eventlet/gevent.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
