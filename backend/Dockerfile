FROM python:3.12-slim

# Systemabhängigkeiten für psycopg2 installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# src-Verzeichnis kopieren, damit Imports funktionieren
COPY src/ ./src/

EXPOSE 5000

CMD ["python", "app.py"]
