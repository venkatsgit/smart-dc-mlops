FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    mlflow==2.8.1 \
    psycopg2-binary==2.9.7

# Create directory for artifacts
RUN mkdir -p /mlflow/artifacts

# Set working directory
WORKDIR /mlflow

# Expose port
EXPOSE 5000

# Default command
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]