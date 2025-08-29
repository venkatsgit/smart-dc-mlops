#!/bin/bash

# MLflow Kubernetes Cleanup Script
# Usage: ./cleanup.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is specified
if [ $# -eq 0 ]; then
    print_error "Please specify environment: dev or prod"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

ENVIRONMENT=$1

# Validate environment
if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: dev, prod"
    exit 1
fi

print_status "Cleaning up MLflow deployment from $ENVIRONMENT environment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

NAMESPACE="smart-dc-$ENVIRONMENT"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_warning "Namespace $NAMESPACE does not exist. Nothing to clean up."
    exit 0
fi

# Confirm deletion
echo -e "${YELLOW}This will delete all MLflow resources in namespace: $NAMESPACE${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled."
    exit 0
fi

# Delete all MLflow resources
print_status "Deleting MLflow resources..."

# Delete deployment
if kubectl get deployment "mlflow-$ENVIRONMENT" -n "$NAMESPACE" &> /dev/null; then
    print_status "Deleting MLflow deployment..."
    kubectl delete deployment "mlflow-$ENVIRONMENT" -n "$NAMESPACE"
else
    print_warning "MLflow deployment not found"
fi

# Delete service
if kubectl get service "mlflow-service-$ENVIRONMENT" -n "$NAMESPACE" &> /dev/null; then
    print_status "Deleting MLflow service..."
    kubectl delete service "mlflow-service-$ENVIRONMENT" -n "$NAMESPACE"
else
    print_warning "MLflow service not found"
fi

# Delete ingress
if kubectl get ingress "mlflow-ingress-$ENVIRONMENT" -n "$NAMESPACE" &> /dev/null; then
    print_status "Deleting MLflow ingress..."
    kubectl delete ingress "mlflow-ingress-$ENVIRONMENT" -n "$NAMESPACE"
else
    print_warning "MLflow ingress not found"
fi

# Delete PVC
if kubectl get pvc "mlflow-artifacts-pvc-$ENVIRONMENT" -n "$NAMESPACE" &> /dev/null; then
    print_status "Deleting MLflow PVC..."
    kubectl delete pvc "mlflow-artifacts-pvc-$ENVIRONMENT" -n "$NAMESPACE"
else
    print_warning "MLflow PVC not found"
fi

# Delete PV
if kubectl get pv "mlflow-artifacts-pv-$ENVIRONMENT" &> /dev/null; then
    print_status "Deleting MLflow PV..."
    kubectl delete pv "mlflow-artifacts-pv-$ENVIRONMENT"
else
    print_warning "MLflow PV not found"
fi

# Delete secrets
if kubectl get secret "mlflow-postgres-secret-$ENVIRONMENT" -n "$NAMESPACE" &> /dev/null; then
    print_status "Deleting MLflow PostgreSQL secret..."
    kubectl delete secret "mlflow-postgres-secret-$ENVIRONMENT" -n "$NAMESPACE"
else
    print_warning "MLflow PostgreSQL secret not found"
fi

# Wait for resources to be deleted
print_status "Waiting for resources to be deleted..."
sleep 10

# Check if any MLflow resources remain
print_status "Checking for remaining MLflow resources..."
kubectl get all -n "$NAMESPACE" -l app=mlflow 2>/dev/null || true

print_status "MLflow cleanup from $ENVIRONMENT environment completed!"
print_status "Note: The namespace $NAMESPACE was not deleted. Delete it manually if needed:"
echo "kubectl delete namespace $NAMESPACE"
