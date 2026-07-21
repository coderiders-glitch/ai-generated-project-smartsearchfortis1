FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pipelines/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipelines/ .

ENV PYTHONUNBUFFERED=1
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=fortis_db
ENV DB_USER=postgres

CMD ["airflow", "scheduler"]