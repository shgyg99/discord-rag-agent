FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/src/

# Create directories with correct permissions
RUN mkdir -p /app/cache /app/docs /app/logs && \
    adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DOCS_DIR=/app/docs \
    MODEL_CACHE_DIR=/app/cache/models

USER appuser

CMD ["python", "-u", "src/main.py"]