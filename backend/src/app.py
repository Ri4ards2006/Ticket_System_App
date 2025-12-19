from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .routes import main
from src import create_app
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://ticketuser:password@db:5432/ticketdb"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main)

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Frontend/Docker kann so darauf zugreifen