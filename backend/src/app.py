from flask import Flask
from src.routes import main_routes
from src.models import db
from src.auth import login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/ticketdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True)
