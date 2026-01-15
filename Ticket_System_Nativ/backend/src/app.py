from .app_factory import create_app

# Das ist das Objekt, das Flask beim Start benutzt
app = create_app()

if __name__ == "__main__":
    # Nur zum Testen lokal, Docker benutzt flask run
    app.run(host="0.0.0.0", port=5000, debug=True)
