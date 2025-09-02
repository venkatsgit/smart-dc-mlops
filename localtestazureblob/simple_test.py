#!/usr/bin/env python3
"""
Simple MLflow Azure Blob Storage Test Script

This script tests basic MLflow functionality with Azure Blob Storage.
"""

import os
import mlflow
import pandas as pd
import numpy as np
from datetime import datetime
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def simple_test():
    """Simple test of MLflow with Azure Blob Storage"""
    print("Simple MLflow Azure Blob Storage Test")
    print("=" * 50)
    
    # Set up Azure credentials
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'kdchitappsdiag')
    storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', 'uvAXtd0wi9jHLYUBY7Kfw+fRFEc5Yw5/Qsn2quay5sy0vTgCNApqp0yVHBt32NHcDA34HajM4yg3PWwHmeBxyw==')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'dev-preprocessed-artifacts')
    
    # Set environment variables for Azure credentials
    os.environ['AZURE_STORAGE_ACCOUNT'] = storage_account
    os.environ['AZURE_STORAGE_KEY'] = storage_key
    
    # Set tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Storage Account: {storage_account}")
    print(f"Container: {container_name}")
    
    try:
        # Create experiment
        experiment_name = "simple-azure-blob-test"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
        else:
            experiment_id = experiment.experiment_id
            print(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
        
        mlflow.set_experiment(experiment_name)
        
        # Start a run
        run_name = f"simple-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            mlflow.log_param("test_type", "simple")
            mlflow.log_param("timestamp", datetime.now().isoformat())
            
            # Log metrics
            mlflow.log_metric("accuracy", 0.95)
            mlflow.log_metric("precision", 0.92)
            mlflow.log_metric("recall", 0.88)
            
            # Create and log a simple artifact
            test_data = {
                "test_id": "simple_test",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "accuracy": 0.95,
                    "precision": 0.92,
                    "recall": 0.88
                }
            }
            
            # Save to temporary file and log as artifact
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
                json.dump(test_data, tmp_file, indent=2)
                mlflow.log_artifact(tmp_file.name, "test_results")
                os.unlink(tmp_file.name)
            
            # Log run metadata
            run_id = mlflow.active_run().info.run_id
            print(f"Run completed successfully! Run ID: {run_id}")
            print(f"View run at: http://localhost:5000/#/experiments/{experiment_id}/runs/{run_id}")
        
        # List experiments
        experiments = mlflow.search_experiments()
        print("\n=== Available Experiments ===")
        for exp in experiments:
            print(f"Name: {exp.name}, ID: {exp.experiment_id}")
        
        print("\n✅ Simple test completed successfully!")
        print("You can view the MLflow UI at: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("\nMake sure:")
        print("1. MLflow server is running on localhost:5000")
        print("2. Azure storage credentials are set in environment variables")
        print("3. Azure storage container exists")

if __name__ == "__main__":
    simple_test()
