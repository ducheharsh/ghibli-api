FROM docker.io/library/python:3.9-slim

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
COPY templates/ templates/
COPY static/ static/

# Print directory contents for debugging
RUN ls -la /app && \
    ls -la /app/templates && \
    ls -la /app/static

# Expose the port
EXPOSE 5001

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--log-level", "debug", "app:app"] 