#!/bin/bash

echo "Deploying simple NGINX Ingress Controller..."

# Apply all YAML files in order
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-basic-auth-secret.yaml
kubectl apply -f 02-nginx-ingress-controller.yaml
kubectl apply -f 03-service.yaml

echo "Waiting for deployment to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app=nginx-ingress-controller \
  --timeout=120s

echo "NGINX Ingress Controller deployed successfully!"
echo ""
echo "To get the external IP:"
echo "kubectl get svc -n ingress-nginx"
echo ""
echo "Basic auth credentials:"
echo "Username: mlops"
echo "Password: mlopsuser"
