FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Abhängigkeiten kopieren (Pfad relativ zum Build-Kontext!)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY backend/src/ ./src/

EXPOSE 5000

CMD ["python", "src/app.py"]
