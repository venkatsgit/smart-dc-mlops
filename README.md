# MLflow Kubernetes Deployment

This directory contains Kubernetes deployment configurations for MLflow in both development and production environments.

## Overview

The deployment includes:
- **MLflow Server**: For experiment tracking and model registry (v2.0.1)
- **PostgreSQL Database**: For storing MLflow metadata
- **Azure File Share**: For storing model artifacts and files
- **Kubernetes Resources**: Deployment, Service, PV, PVC, Secrets, and Ingress
- **Automatic Load Balancer**: AKS creates public Load Balancer for external access

## Directory Structure

```
mlflow_deployment/
├── templates/                          # Base template files
│   ├── mlflow-deployment-template.yaml
│   ├── mlflow-service-template.yaml
│   ├── mlflow-pv-template.yaml
│   ├── mlflow-pvc-template.yaml
│   ├── mlflow-postgres-secret-template.yaml
│   └── mlflow-ingress-template.yaml
├── dev/                               # Dev environment configs
│   ├── mlflow-dev-config.yaml
│   └── generated/                     # Generated YAML files
├── prod/                              # Prod environment configs
│   ├── mlflow-prod-config.yaml
│   └── generated/                     # Generated YAML files
├── deploy.py                          # Deployment script
├── deploy.sh                          # Shell deployment script
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Prerequisites

1. **Kubernetes Cluster**: Access to a Kubernetes cluster (AKS recommended)
2. **Azure File Share**: Access to Azure File Storage with shares:
   - `dev-preprocessed-artifacts` (dev)
   - `prod-preprocessed-artefacts` (prod)
3. **PostgreSQL Database**: Access to the specified databases
4. **Azure Secret**: `azure-secret` containing Azure File Share credentials
5. **NGINX Ingress Controller**: For handling external traffic routing
6. **Python Dependencies**: Install requirements with `pip install -r requirements.txt`

## Configuration

### Environment Variables

Each environment has its own configuration file with:
- **Namespace**: `smart-dc-dev` or `smart-dc-prod`
- **PostgreSQL**: Connection details and schema
- **Azure File Share**: Share names for artifacts
- **MLflow**: Image (v2.0.1), ports, and settings
- **Access**: Ingress path configuration (`/mlflow`)

### Database Schema

The MLflow metadata will be stored in the `mlflow` schema of the PostgreSQL database.

### Access Configuration

MLflow is accessible via:
- **Path**: `/mlflow` (configurable)
- **Service Type**: ClusterIP (internal access)
- **External Access**: Through Ingress with automatic Load Balancer

## Deployment

### Option 1: Using deploy.sh (Recommended for Linux/Mac)

The `deploy.sh` script generates Kubernetes YAML files from templates for easy deployment.

#### Prerequisites for deploy.sh
- Linux/Mac environment (or WSL on Windows)
- `python` available in PATH

#### Generate YAML files for Dev Environment
```bash
./deploy.sh dev
```

#### Generate YAML files for Production Environment
```bash
./deploy.sh prod
```

#### What deploy.sh does:
1. ✅ Validates environment parameter (dev/prod)
2. ✅ Checks if Python is available
3. ✅ Generates Kubernetes YAML files from templates
4. ✅ Places generated files in `<env>/generated/` directory
5. ✅ Provides kubectl commands for manual deployment

#### After generating YAML files, deploy manually:
```bash
# Deploy to Kubernetes
kubectl apply -f <env>/generated/
```

### Option 2: Manual Deployment

#### 1. Generate YAML Files

Run the deployment script to generate environment-specific YAML files:

```bash
python deploy.py
```

This will create the `generated/` directories with ready-to-deploy YAML files.

#### 2. Deploy to Kubernetes

##### Dev Environment
```bash
kubectl apply -f dev/generated/
```

##### Production Environment
```bash
kubectl apply -f prod/generated/
```

#### 3. Verify Deployment

Check the deployment status:

```bash
# Check pods
kubectl get pods -n smart-dc-dev
kubectl get pods -n smart-dc-prod

# Check services
kubectl get svc -n smart-dc-dev
kubectl get svc -n smart-dc-prod

# Check ingress
kubectl get ingress -n smart-dc-dev
kubectl get ingress -n smart-dc-prod
```

## Access MLflow

### UI Access (Human Users)

Once deployed, MLflow will be accessible via:
- **Dev**: `http://<load-balancer-ip>/mlflow`
- **Prod**: `http://<load-balancer-ip>/mlflow`

To get the Load Balancer IP:
```bash
kubectl get svc -n kube-system | grep LoadBalancer
```

### Client Code Access (Python/Preprocessing/Training)

#### Through Ingress (Recommended)
```python
import mlflow

# Dev Environment
mlflow.set_tracking_uri("http://<load-balancer-ip>/mlflow")
mlflow.set_experiment("my_experiment")

# Production Environment
mlflow.set_tracking_uri("http://<load-balancer-ip>/mlflow")
mlflow.set_experiment("my_experiment")
```

### Example Client Code

```python
# training_script.py
import mlflow
import mlflow.sklearn

# Connect to MLflow (Dev)
mlflow.set_tracking_uri("http://<load-balancer-ip>/mlflow")

# Set experiment
mlflow.set_experiment("chiller_anomaly_detection")

# Start run
with mlflow.start_run():
    # Your ML code here
    mlflow.log_param("model_type", "random_forest")
    mlflow.log_metric("accuracy", 0.95)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Environment-Based Configuration

```python
import os

# Set MLflow URI based on environment
if os.getenv("ENV") == "prod":
    mlflow.set_tracking_uri("http://<load-balancer-ip>/mlflow")
else:
    mlflow.set_tracking_uri("http://<load-balancer-ip>/mlflow")
```

## Customization

### Update Configuration

Edit the environment-specific config files:
- `dev/mlflow-dev-config.yaml`
- `prod/mlflow-prod-config.yaml`

### Modify Templates

Edit files in the `templates/` directory and regenerate using `deploy.py`.

### Add New Environments

1. Create a new config file in a new directory
2. Update `deploy.py` to include the new environment
3. Run the deployment script

## Troubleshooting

### Common Issues

1. **Azure File Share Access**: Ensure `azure-secret` exists and has correct credentials
2. **PostgreSQL Connection**: Verify database connectivity and schema existence
3. **Storage Issues**: Verify PV/PVC binding and Azure File Share access
4. **Ingress Issues**: Check if NGINX Ingress Controller is running

### Logs

Check MLflow pod logs:
```bash
kubectl logs -f deployment/mlflow-dev -n smart-dc-dev
kubectl logs -f deployment/mlflow-prod -n smart-dc-prod
```

Check Ingress logs:
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Security Notes

- Database credentials are stored as Kubernetes secrets
- Azure File Share credentials should be managed securely
- Consider implementing network policies for additional security
- MLflow is accessible via HTTP (no built-in authentication)

## Support

For issues or questions, check:
1. Kubernetes cluster logs
2. MLflow application logs
3. Network connectivity to Azure and PostgreSQL
4. Resource quotas and limits
5. NGINX Ingress Controller status
6. Load Balancer provisioning status
