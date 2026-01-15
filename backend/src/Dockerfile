FROM python:3.12-slim

WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Quellcode
COPY ./src ./src

# Entrypoint-Script kopieren und ausführbar machen
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Umgebungsvariablen
ENV FLASK_APP=src.app:app
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DATABASE_URL=postgresql://ticketuser:password@db:5432/ticketdb

# Port exposed
EXPOSE 5000

# ENTRYPOINT auf das Script setzen
ENTRYPOINT ["/entrypoint.sh"]
