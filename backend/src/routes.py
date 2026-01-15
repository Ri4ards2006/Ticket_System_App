# src/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Ticket

main = Blueprint("main", __name__, template_folder="templates")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("main.dashboard"))
        return "Invalid credentials", 401

    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main.route("/")
@login_required
def dashboard():
    tickets = Ticket.query.all()
    return render_template("index.html", tickets=tickets, user=current_user)
