# Simple NGINX Ingress Controller

Basic NGINX Ingress Controller setup with basic authentication and proper RBAC permissions.

## Files

- `00-namespace.yaml` - Creates the ingress-nginx namespace
- `01-rbac.yaml` - RBAC configuration (ServiceAccount, ClusterRole, ClusterRoleBinding)
- `01-basic-auth-secret.yaml` - Basic authentication secret (mlops:mlopsuser)
- `02-nginx-ingress-controller.yaml` - NGINX Ingress Controller deployment with proper permissions
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

## Features

- Proper RBAC permissions for Ingress Classes and resources
- Environment variables properly configured (POD_NAME, POD_NAMESPACE)
- Security context with minimal privileges
- Health checks (liveness and readiness probes)
- LoadBalancer service type for external access
- Runs on port 80 (HTTP) and 443 (HTTPS)

## Troubleshooting

If you encounter permission errors, ensure the RBAC resources are properly applied:
```bash
kubectl get serviceaccount -n ingress-nginx
kubectl get clusterrole nginx-ingress-clusterrole
kubectl get clusterrolebinding nginx-ingress-clusterrole-nisa-binding
```
