# PathCraft AI Production Dockerfile for GCP Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn google-cloud-bigquery

# Copy application code
COPY . .

# Grant execute permissions
RUN chmod +x entrypoint.sh

# Expose default Cloud Run port
EXPOSE 8080

# Run entrypoint script
CMD ["./entrypoint.sh"]
