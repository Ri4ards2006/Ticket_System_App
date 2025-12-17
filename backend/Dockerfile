# Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src

EXPOSE 5000

CMD ["python", "src/app.py"]
