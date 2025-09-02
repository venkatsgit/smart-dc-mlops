# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose MLflow port
EXPOSE 5000

# Set environment variables for MLflow
ENV MLFLOW_TRACKING_URI=http://localhost:5000
ENV MLFLOW_ARTIFACT_ROOT=wasbs://dev-preprocessed-artifacts@kdchitappsdiag.blob.core.windows.net/

# Create directory for MLflow data
RUN mkdir -p /mlflow

# Set the default command to run MLflow server
CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "sqlite:///mlflow.db", \
     "--default-artifact-root", "wasbs://dev-preprocessed-artifacts@kdchitappsdiag.blob.core.windows.net/"]
