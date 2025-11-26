# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /app

# 3. CRITICAL: Install system dependencies (zbar)
# This prevents the "ImportError: Unable to find zbar shared library"
RUN apt-get update && apt-get install -y \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn  # Install production server

# 5. Copy the rest of the application code
COPY . .

# 6. Run the application using Gunicorn (NOT python app.py)
# Replace 'app:app' with 'your_filename:flask_app_variable_name'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]