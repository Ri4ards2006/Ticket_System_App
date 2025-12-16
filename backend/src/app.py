from flask import Flask
from routes import main_routes
from auth import auth_routes

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register Blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
