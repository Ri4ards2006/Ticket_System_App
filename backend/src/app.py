from flask import Flask
from src.models import db
from src.auth import login_manager
from src.routes import main_routes
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://ticketuser:password@db:5432/ticketdb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(main_routes)

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
