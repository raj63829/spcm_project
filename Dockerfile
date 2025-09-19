# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies including sqlite3
RUN apt-get update && apt-get install -y \
    build-essential cmake libpq-dev sqlite3 libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start Django with Gunicorn
CMD gunicorn spcm_project.wsgi --bind 0.0.0.0:$PORT
