from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from src.models import User

login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
