# init_db.py
from time import sleep
from app import create_app
from models import db, User
from sqlalchemy.exc import OperationalError

app = create_app()

# warten, bis DB ready ist
while True:
    try:
        with app.app_context():
            db.create_all()
            print("✅ Tables created")
            if not User.query.filter_by(username="admin").first():
                admin = User(username="admin", password="password", role="admin")
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created")
            break
    except OperationalError:
        print("DB not ready, retrying in 1s...")
        sleep(1)
