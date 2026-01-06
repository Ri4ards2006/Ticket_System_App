FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV FLASK_APP=src.app:create_app
ENV FLASK_ENV=development

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DATABASE_URL=postgresql://ticketuser:password@db:5432/ticketdb

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
