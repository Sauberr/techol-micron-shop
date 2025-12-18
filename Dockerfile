FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./micron .

RUN mkdir -p /app/staticfiles /app/static/images

EXPOSE 8000

CMD ["gunicorn", "micron.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]