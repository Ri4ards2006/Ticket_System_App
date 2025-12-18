from flask import Flask
from .routes import main_routes
from .models import db
from .auth import login_manager
import time
import os
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ticketuser:password@db:5432/ticketdb"
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')

# PostgreSQL URI aus Environment Variables (Container-freundlich)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://ticketuser:password@db:5432/ticketdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions initialisieren
db.init_app(app)
login_manager.init_app(app)

# Blueprints registrieren
app.register_blueprint(main_routes)

# Tabellen automatisch erstellen, falls sie nicht existieren
def create_tables():
    for _ in range(10):  # 10 Versuche
        try:
            with app.app_context():
                db.create_all()
            print("DB connected!")
            return
        except OperationalError:
            print("DB noch nicht bereit, warte 2 Sekunden...")
            time.sleep(2)
    raise RuntimeError("Konnte keine Verbindung zur DB herstellen!")

if __name__ == "__main__":
    create_tables()  # Tabellen direkt beim Start erstellen
    app.run(host="0.0.0.0", port=5000, debug=True)
