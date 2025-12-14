FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r micron && useradd -r -g micron micron

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./micron .

RUN chown -R micron:micron /app
USER micron

EXPOSE 8000

CMD ["gunicorn", "micron.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
