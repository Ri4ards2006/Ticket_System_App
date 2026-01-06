#!/bin/bash
# entrypoint.sh

# Warte, bis PostgreSQL erreichbar ist
echo "Waiting for postgres..."
while ! pg_isready -h db -p 5432 > /dev/null 2>&1; do
    sleep 1
done

# DB initialisieren
python src/init_db.py

# Flask starten
flask run --host=0.0.0.0 --port=5000
