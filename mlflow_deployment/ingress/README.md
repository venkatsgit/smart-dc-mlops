# Simple NGINX Ingress Controller

Basic NGINX Ingress Controller setup with basic authentication.

## Files

- `00-namespace.yaml` - Creates the ingress-nginx namespace
- `01-basic-auth-secret.yaml` - Basic authentication secret (mlops:mlopsuser)
- `02-nginx-ingress-controller.yaml` - Simple NGINX Ingress Controller deployment
- `03-service.yaml` - LoadBalancer service for external access
- `deploy.sh` - Deployment script
- `cleanup.sh` - Cleanup script

## Usage

### Deploy
```bash
cd ingress
chmod +x deploy.sh
./deploy.sh
```

### Cleanup
```bash
cd ingress
chmod +x cleanup.sh
./cleanup.sh
```

### Get External IP
```bash
kubectl get svc -n ingress-nginx
```

## Basic Authentication

- **Username**: mlops
- **Password**: mlopsuser

## Notes

- Simple setup without complex RBAC
- Basic authentication enabled
- LoadBalancer service type for external access
- Runs on port 80 (HTTP)
