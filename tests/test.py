from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "secret123"

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def home():
    return "Flask + Login OK!"

if __name__ == "__main__":
    app.run(debug=True)
