# Use the latest stable MLflow image as base
FROM ghcr.io/mlflow/mlflow:v3.3.2

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PostgreSQL driver
RUN pip install --no-cache-dir psycopg2-binary

# Verify installation
RUN python -c "import psycopg2; print('psycopg2 installed successfully')"

# Set working directory
WORKDIR /mlflow
