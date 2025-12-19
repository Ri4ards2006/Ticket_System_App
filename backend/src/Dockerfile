FROM python:3.11-slim

WORKDIR /app

# Build-Tools für PostgreSQL
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DATABASE_URL=postgresql://ticketuser:password@db:5432/ticketdb

EXPOSE 5000

# Direkt Python Modul starten (robuster als "flask run")
CMD ["python", "-m", "src.app"]
