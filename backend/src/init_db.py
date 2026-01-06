from app import create_app
from models import db, User  # passen die Pfade zu deinen Modellen?

app = create_app()

with app.app_context():
    db.create_all()  # erstellt alle Tabellen
    print("✅ DB tables created!")

    # Test-User anlegen
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="password", role="admin")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
