from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Ticket

main = Blueprint("main", __name__, template_folder="templates")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("main.dashboard"))
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

@main.route("/tickets")
@login_required
def tickets_view():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets, user=current_user)

@main.route("/tickets/create", methods=["POST"])
@login_required
def create_ticket():
    ticket = Ticket(
        title=request.form["title"],
        description=request.form["description"],
        created_by=current_user.id,
        status="open"
    )
    db.session.add(ticket)
    db.session.commit()
    return redirect(url_for("main.dashboard"))
