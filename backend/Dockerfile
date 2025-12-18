# Base Image
FROM python:3.12-slim

# Systemabhängigkeiten für psycopg2 (Postgres)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Python-Abhängigkeiten kopieren und installieren
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY backend/src/ ./src/

# Port freigeben
EXPOSE 5000

# Startbefehl
CMD ["python", "src/app.py"]
