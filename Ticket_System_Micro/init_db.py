import sqlite3

db = sqlite3.connect("tickets.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    status TEXT,
    comment TEXT,
    user_id INTEGER
)
""")

users = [
    ("admin", "admin", "admin"),
    ("support", "support", "support"),
    ("user", "user", "user")
]

cur.executemany("INSERT INTO users VALUES (NULL, ?, ?, ?)", users)

db.commit()
db.close()

print("✅ Datenbank initialisiert")
