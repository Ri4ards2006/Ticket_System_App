from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, User, Ticket
from flask_login import login_user
from werkzeug.security import check_password_hash

main_routes = Blueprint("main", __name__, template_folder="../../frontend/src")

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main_routes.route("/")
@login_required
def dashboard():
    tickets = Ticket.query.all()
    return render_template("dashboard.html", tickets=tickets, user=current_user)

@main_routes.route("/tickets")
@login_required
def tickets_view():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets, user=current_user)

@main_routes.route("/tickets/create", methods=["POST"])
@login_required
def create_ticket():
    ticket = Ticket(
        title=request.form["title"],
        description=request.form["description"],
        created_by=current_user.id
    )
    db.session.add(ticket)
    db.session.commit()
    return redirect(url_for("main.tickets_view"))

@main_routes.route("/tickets/<int:id>/update", methods=["POST"])
@login_required
def update_ticket(id):
    ticket = Ticket.query.get(id)
    if ticket:
        ticket.status = request.form.get("status", ticket.status)
        assigned = request.form.get("assigned_to")
        ticket.assigned_to = int(assigned) if assigned else None
        db.session.commit()
    return redirect(url_for("main.tickets_view"))

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('main.dashboard'))
    return render_template('login.html')
