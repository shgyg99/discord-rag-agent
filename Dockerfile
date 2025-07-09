FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt



# RUN pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu

COPY . /app/


# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DOCS_DIR=/app/docs \
    MODEL_CACHE_DIR=/app/cache/models


CMD ["python", "-u", "src/main.py"]