FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the test script
COPY test_mlflow_artifact.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=""
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=""

# Default command
CMD ["python", "test_mlflow_artifact.py"]
