from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# Dummy login n
users = {"admin": "password"}

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if users.get(username) == password:
            return redirect(url_for('main.home'))
        return "Login failed", 400
    return render_template("login.html")

@main_bp.route("/")
def home():
    return "Willkommen im Ticket System!"
