from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "data/tickets.db"

def init_db():
    if not os.path.exists("data"):
        os.mkdir("data")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            title TEXT,
            category TEXT,
            priority TEXT,
            status TEXT,
            comment TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return render_template("index.html", tickets=tickets)

@app.route("/create", methods=["POST"])
def create():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO tickets (title, category, priority, status) VALUES (?, ?, ?, 'Neu')",
        (request.form["title"], request.form["category"], request.form["priority"])
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/update/<int:id>")
def update(id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tickets SET status='Erledigt' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
