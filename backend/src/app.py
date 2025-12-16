from flask import Flask
from src.routes import main_routes
from src.models import db
from src.auth import login_manager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')

# PostgreSQL URI aus Environment Variables (Container-freundlich)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://ticketuser:password@db:5432/ticketdb'  # default für Container
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions initialisieren
db.init_app(app)
login_manager.init_app(app)

# Blueprints registrieren
app.register_blueprint(main_routes)

# Tabellen automatisch erstellen, falls sie nicht existieren
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    # Debug nur lokal
    app.run(host="0.0.0.0", port=5000, debug=True)
