# MLflow Artifact Testing Script

This script tests MLflow artifact logging with two different connection modes:

## 1. Nginx Authentication Mode (Default)
Uses the nginx-protected URL with username/password authentication.

```bash
python test_mlflow_artifact.py
```

**Features:**
- Connects to `http://4.144.173.96/mlflowdev`
- Uses nginx authentication (username: `mlops`, password: `mlopsuser`)
- Prints tracking URI first as requested
- Full DEBUG logging enabled

## 2. Kubectl Port-Forward Mode (Bypasses Nginx)
Connects directly to the MLflow service, bypassing nginx authentication.

### Setup Port-Forward
First, set up the port-forward in a separate terminal:

**Linux/Mac:**
```bash
./setup_port_forward.sh
```

**Windows:**
```cmd
setup_port_forward.bat
```

Or manually:
```bash
kubectl port-forward svc/mlflow-service 5000:5000
```

### Run the Test
Then run the test script with port-forward mode:

```bash
python test_mlflow_artifact.py --port-forward
```

**Features:**
- Connects to `http://localhost:5000`
- No authentication required (bypasses nginx)
- Direct connection to MLflow service
- Useful for debugging nginx-related issues

## Key Changes Made

1. **Print Tracking URI First**: The script now prints the tracking URI at the beginning
2. **Dual Mode Support**: Added `--port-forward` flag to bypass nginx
3. **Connection Mode Logging**: Logs whether using nginx auth or port-forward
4. **Helper Scripts**: Created setup scripts for port-forward

## Troubleshooting

### If nginx authentication fails:
1. Use port-forward mode to test if MLflow itself is working
2. Check nginx configuration and credentials
3. Verify network connectivity to the server

### If port-forward fails:
1. Ensure kubectl is configured correctly
2. Check if the MLflow service exists in the cluster
3. Verify the service name matches `mlflow-service`

## Debug Information

The script includes extensive DEBUG logging for:
- MLflow operations
- HTTP requests
- File operations
- Artifact logging details
