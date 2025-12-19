from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, User, Ticket

main_routes = Blueprint("main", __name__)

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        return "Login fehlgeschlagen", 401
    return render_template("login.html")


@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))
