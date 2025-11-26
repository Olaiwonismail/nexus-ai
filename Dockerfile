FROM python:3.11-slim

WORKDIR /app

# --- UPDATED SECTION ---
# We added: gcc, python3-dev, libpq-dev (for database drivers)
RUN apt-get update && apt-get install -y \
    libzbar0 \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# -----------------------

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]