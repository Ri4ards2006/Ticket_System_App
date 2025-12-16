# 1️⃣ Base Image: Python slim
FROM python:3.11-slim

# 2️⃣ Arbeitsverzeichnis im Container
WORKDIR /app

# 3️⃣ Copy requirements und installiere Pakete
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy des gesamten Backend Codes
COPY src/ ./src

# 5️⃣ Ports exposed
EXPOSE 5000

# 6️⃣ Standardbefehl zum Starten
CMD ["python", "src/app.py"]
