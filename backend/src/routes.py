from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from src.models import db, Ticket, User

main_routes = Blueprint('main', __name__)

# Dashboard
@main_routes.route('/')
@login_required
def dashboard():
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets, user=current_user)

# Tickets Übersicht
@main_routes.route('/tickets')
@login_required
def tickets_view():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets, user=current_user)

# Ticket erstellen
@main_routes.route('/tickets/create', methods=['POST'])
@login_required
def create_ticket():
    title = request.form.get('title')
    desc = request.form.get('description')
    ticket = Ticket(title=title, description=desc, created_by=current_user.id)
    db.session.add(ticket)
    db.session.commit()
    return redirect(url_for('main.tickets_view'))

# Ticket Status ändern
@main_routes.route('/tickets/<int:id>/update', methods=['POST'])
@login_required
def update_ticket(id):
    ticket = Ticket.query.get(id)
    if ticket:
        ticket.status = request.form.get('status', ticket.status)
        ticket.assigned_to = request.form.get('assigned', ticket.assigned_to)
        db.session.commit()
    return redirect(url_for('main.tickets_view'))

# Logout
@main_routes.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('main.login'))
