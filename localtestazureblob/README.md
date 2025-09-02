# MLflow Azure Blob Storage Integration

This directory contains files to set up MLflow with Azure Blob Storage as the artifact store.

## Files

- `Dockerfile`: Docker image for MLflow server with Azure Blob support
- `requirements.txt`: Python dependencies for MLflow and Azure integration
- `test_mlflow_azure_blob.py`: Test script to create experiments and store artifacts

## Setup Instructions

### 1. Prerequisites

- Azure Storage Account with Blob Storage enabled
- Python 3.9+ (if running locally)
- Docker (if using containerized approach)

### 2. Environment Variables

Create a `.env` file with the following variables (or use the defaults):

```bash
# Azure Storage Account Configuration
AZURE_STORAGE_ACCOUNT_NAME=kdchitappsdiag
AZURE_STORAGE_ACCOUNT_KEY=uvAXtd0wi9jHLYUBY7Kfw+fRFEc5Yw5/Qsn2quay5sy0vTgCNApqp0yVHBt32NHcDA34HajM4yg3PWwHmeBxyw==
AZURE_STORAGE_CONTAINER_NAME=dev-preprocessed-artifacts
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=kdchitappsdiag;AccountKey=uvAXtd0wi9jHLYUBY7Kfw+fRFEc5Yw5/Qsn2quay5sy0vTgCNApqp0yVHBt32NHcDA34HajM4yg3PWwHmeBxyw==;EndpointSuffix=core.windows.net;

# MLflow Configuration (optional - defaults to localhost:5000)
MLFLOW_TRACKING_URI=http://localhost:5000
```

### 3. Azure Storage Setup

The configuration is already set up for:
- Storage Account: `kdchitappsdiag`
- Container: `dev-preprocessed-artifacts`
- Connection String: Provided above

### 4. Running with Docker

```bash
# Build the Docker image
docker build -t mlflow-azure-blob .

# Run the MLflow server
docker run -p 5000:5000 mlflow-azure-blob
```

Or use docker-compose (recommended):
```bash
docker-compose up --build
```

### 5. Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start MLflow server
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root wasbs://dev-preprocessed-artifacts@kdchitappsdiag.blob.core.windows.net/
```

### 6. Running the Test Script

```bash
# Run the test (uses default values)
python test_mlflow_azure_blob.py

# Or set environment variables explicitly
export AZURE_STORAGE_ACCOUNT_NAME=kdchitappsdiag
export AZURE_STORAGE_ACCOUNT_KEY=uvAXtd0wi9jHLYUBY7Kfw+fRFEc5Yw5/Qsn2quay5sy0vTgCNApqp0yVHBt32NHcDA34HajM4yg3PWwHmeBxyw==
export AZURE_STORAGE_CONTAINER_NAME=dev-preprocessed-artifacts
python test_mlflow_azure_blob.py
```

## What the Test Script Does

The test script demonstrates:

1. **Setup**: Configures MLflow with Azure Blob Storage
2. **Data Generation**: Creates synthetic data for testing
3. **Experiment Creation**: Creates a new MLflow experiment
4. **Model Training**: Trains a Random Forest model
5. **Artifact Logging**: Logs various artifacts to Azure Blob:
   - Trained model files
   - Feature importance plots
   - Test data and predictions
   - Model metadata (JSON)
6. **Metrics Logging**: Logs model performance metrics
7. **Run Listing**: Lists all experiments and runs

## Artifacts Stored in Azure Blob

The test creates the following artifact structure in your Azure Blob container (`dev-preprocessed-artifacts`):

```
dev-preprocessed-artifacts/
├── <run_id>/
│   ├── artifacts/
│   │   ├── model/
│   │   │   ├── conda.yaml
│   │   │   ├── MLmodel
│   │   │   ├── python_env.yaml
│   │   │   └── model.pkl
│   │   ├── plots/
│   │   │   └── feature_importance.png
│   │   ├── data/
│   │   │   └── test_predictions.csv
│   │   └── metadata/
│   │       └── model_info.json
│   ├── meta.yaml
│   └── tags
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure Azure credentials are correct
2. **Container Not Found**: Ensure the container exists in your storage account
3. **Permission Error**: Verify the storage account key has proper permissions
4. **MLflow Server Not Running**: Start the MLflow server before running the test

### Debug Commands

```bash
# Check MLflow server status
curl http://localhost:5000/health

# List Azure containers
az storage container list --account-name your_account --account-key your_key

# Test Azure connection
python -c "from azure.storage.blob import BlobServiceClient; print('Connection successful')"
```

## Security Notes

- Never commit `.env` files with real credentials
- Use Azure Key Vault for production environments
- Consider using Managed Identity for Azure services
- Rotate storage account keys regularly
