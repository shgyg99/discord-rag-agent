# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/wheels /wheels
COPY src/ /app/src/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Create required directories
RUN mkdir -p /app/cache /app/docs /app/logs
VOLUME ["/app/docs", "/app/logs"]

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DOCS_DIR=/app/docs
ENV MODEL_CACHE_DIR=/app/cache/models

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["python", "-u", "src/main.py"]
