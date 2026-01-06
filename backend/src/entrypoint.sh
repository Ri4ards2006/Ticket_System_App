#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
# db ist der Name des DB-Containers in docker-compose.yml
while ! pg_isready -h db -p 5432 > /dev/null 2>&1; do
    sleep 1
done

echo "PostgreSQL is ready, initializing database..."
python src/init_db.py

echo "Starting Flask..."
flask run --host=0.0.0.0 --port=5000
