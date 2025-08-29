#!/bin/bash

# MLflow Kubernetes Deployment Script
# Usage: ./deploy.sh [dev|prod]

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

print_status "Generating MLflow YAML files for $ENVIRONMENT environment..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Generate YAML files
print_status "Generating Kubernetes YAML files from templates..."
python deploy.py

print_status "YAML files generated successfully for $ENVIRONMENT environment!"
print_status "Files are located in: $ENVIRONMENT/generated/"
echo ""
print_status "To deploy to Kubernetes (when ready):"
echo "kubectl apply -f $ENVIRONMENT/generated/"
echo ""
print_status "To check deployment status:"
echo "kubectl get pods -n smart-dc-$ENVIRONMENT"
echo "kubectl get svc -n smart-dc-$ENVIRONMENT"
