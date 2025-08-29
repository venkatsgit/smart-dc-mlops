#!/bin/bash

echo "Cleaning up NGINX Ingress Controller..."

kubectl delete -f 03-service.yaml
kubectl delete -f 02-nginx-ingress-controller.yaml
kubectl delete -f 01-basic-auth-secret.yaml
kubectl delete -f 00-namespace.yaml

echo "NGINX Ingress Controller cleaned up successfully!"
