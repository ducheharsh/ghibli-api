FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p static/css static/js static/img templates

# Copy application files
COPY app.py .
COPY database.json .
COPY index.html templates/
COPY api.html templates/
COPY placeholder.html templates/
COPY style.css static/css/
COPY main.js static/js/
COPY logo.png static/img/
COPY logo.svg static/img/

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 