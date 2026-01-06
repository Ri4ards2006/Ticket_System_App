#!/bin/bash
# entrypoint.sh

# Optional: kleine Wartezeit, bis die DB bereit ist
echo "Warte auf PostgreSQL..."
sleep 5  # kann bei Bedarf höher sein

# Datenbank initialisieren
echo "Initialisiere Datenbank..."
python src/init_db.py

# Flask starten
echo "Starte Flask..."
flask run --host=0.0.0.0 --port=5000
