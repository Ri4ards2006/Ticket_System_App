FROM python:3.13-slim

WORKDIR /app

COPY ./src ./src
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV DATABASE_URL=postgresql://ticketuser:password@db:5432/ticketdb

EXPOSE 5000

CMD ["flask", "run"]
