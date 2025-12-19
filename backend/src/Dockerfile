FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DATABASE_URL=postgresql://ticketuser:password@db:5432/ticketdb

EXPOSE 5000

CMD ["flask", "run"]
