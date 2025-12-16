from flask import Blueprint, render_template, request, redirect, session

auth_routes = Blueprint("auth", __name__)

users = {"admin":"admin123"}  # Demo User

@auth_routes.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.get(username)==password:
            session["user"]=username
            return redirect("/")
        else:
            return "Login failed", 401
    return render_template("login.html")

@auth_routes.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
