FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt aus dem gleichen Ordner wie das Dockerfile kopieren
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY src/ ./src/

EXPOSE 5000

# Nutze:
CMD ["python", "-m", "src.app"]
