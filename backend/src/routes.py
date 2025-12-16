from flask import Blueprint, render_template, request, redirect, session
from models import Ticket, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

main_routes = Blueprint("main", __name__)

# DB setup
engine = create_engine("postgresql://postgres:postgres@db:5432/ticketdb")
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)

@main_routes.route("/")
def index():
    db = DBSession()
    tickets = db.query(Ticket).all()
    db.close()
    return render_template("index.html", tickets=tickets)

@main_routes.route("/create", methods=["POST"])
def create_ticket():
    title = request.form["title"]
    description = request.form["description"]
    db = DBSession()
    ticket = Ticket(title=title, description=description)
    db.add(ticket)
    db.commit()
    db.close()
    return redirect("/")
    
@main_routes.route("/close/<int:ticket_id>")
def close_ticket(ticket_id):
    db = DBSession()
    ticket = db.query(Ticket).filter_by(id=ticket_id).first()
    if ticket:
        ticket.status = "closed"
        db.commit()
    db.close()
    return redirect("/")
