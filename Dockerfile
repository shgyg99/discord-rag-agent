FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /app/src/

RUN mkdir -p /app/cache /app/docs /app/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DOCS_DIR=/app/docs
ENV MODEL_CACHE_DIR=/app/cache/models

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "-u", "src/main.py"]
