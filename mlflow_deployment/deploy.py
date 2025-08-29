#!/usr/bin/env python3
"""
MLflow Kubernetes Deployment Script
Generates environment-specific YAML files from templates
"""

import base64
import yaml
from pathlib import Path
from string import Template

def load_config(config_file):
    """Load configuration from YAML file"""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def base64_encode(value):
    """Base64 encode a string or integer value"""
    # Convert to string if it's an integer
    if isinstance(value, int):
        value = str(value)
    return base64.b64encode(value.encode()).decode()

def process_template(template_file, config, output_file):
    """Process a template file with configuration and save to output"""
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Create template object
    template = Template(template_content)
    
    # Prepare substitution values
    substitutions = config.copy()
    
    # Base64 encode PostgreSQL values for secrets
    substitutions['PG_USER_B64'] = base64_encode(config['PG_USER'])
    substitutions['PG_PASSWORD_B64'] = base64_encode(config['PG_PASSWORD'])
    substitutions['PG_HOST_B64'] = base64_encode(config['PG_HOST'])
    substitutions['PG_DATABASE_B64'] = base64_encode(config['PG_DATABASE'])
    substitutions['PG_PORT_B64'] = base64_encode(config['PG_PORT'])
    substitutions['PG_SCHEMA_B64'] = base64_encode(config['PG_SCHEMA'])
    
    # Substitute values
    result = template.substitute(substitutions)
    
    # Save result
    with open(output_file, 'w') as f:
        f.write(result)
    
    print(f"Generated: {output_file}")

def main():
    """Main deployment function"""
    script_dir = Path(__file__).parent
    templates_dir = script_dir / "templates"
    
    # Process each environment
    for env in ['dev', 'prod']:
        print(f"\nProcessing {env} environment...")
        
        # Load config
        config_file = script_dir / env / f"mlflow-{env}-config.yaml"
        config = load_config(config_file)
        
        # Create output directory
        output_dir = script_dir / env / "generated"
        output_dir.mkdir(exist_ok=True)
        
        # Process each template
        template_files = [
            "mlflow-deployment-template.yaml",
            "mlflow-service-template.yaml",
            "mlflow-pv-template.yaml",
            "mlflow-pvc-template.yaml",
            "mlflow-postgres-secret-template.yaml"
        ]
        
        # Add Ingress template if MLFLOW_PATH is specified
        if config.get('MLFLOW_PATH'):
            template_files.append("mlflow-ingress-template.yaml")
            print(f"  Using Ingress with path: {config.get('MLFLOW_PATH')}")
        
        for template_file in template_files:
            template_path = templates_dir / template_file
            if template_path.exists():
                output_file = output_dir / template_file.replace('-template', '')
                process_template(template_path, config, output_file)
            else:
                print(f"Warning: Template {template_file} not found")
    
    print("\nDeployment files generated successfully!")
    print("\nTo deploy:")
    print("1. kubectl apply -f <env>/generated/")
    print("2. kubectl get pods -n <namespace>")
    print("3. kubectl get svc -n <namespace>")
    print("4. kubectl get ingress -n <namespace>")
    print("\nAccess MLflow via Load Balancer IP:")
    print("- kubectl get svc -n kube-system | grep LoadBalancer")
    print("- Access: http://<load-balancer-ip>/mlflow")

if __name__ == "__main__":
    main()
