#!/usr/bin/env python3
"""
Simple MLflow Azure Blob Storage Test - Artifacts Only

This script demonstrates logging artifacts to Azure Blob Storage via MLflow.
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

def simple_artifact_test():
    """Simple test focusing only on artifact logging to Azure Blob"""
    print("MLflow Azure Blob Storage - Artifacts Test")
    print("=" * 50)
    
    # Set up Azure credentials
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'kdchitappsdiag')
    storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', 'uvAXtd0wi9jHLYUBY7Kfw+fRFEc5Yw5/Qsn2quay5sy0vTgCNApqp0yVHBt32NHcDA34HajM4yg3PWwHmeBxyw==')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'dev-preprocessed-artifacts')
    
    # Set environment variables for Azure credentials (this is the key part)
    os.environ['AZURE_STORAGE_ACCOUNT'] = storage_account
    os.environ['AZURE_STORAGE_KEY'] = storage_key
    os.environ['AZURE_STORAGE_CONNECTION_STRING'] = f'DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={storage_key};EndpointSuffix=core.windows.net;'
    
    # Set tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Storage Account: {storage_account}")
    print(f"Container: {container_name}")
    
    try:
        # Create experiment
        experiment_name = "artifacts-test"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
        else:
            experiment_id = experiment.experiment_id
            print(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
        
        mlflow.set_experiment(experiment_name)
        
        # Start a run
        run_name = f"artifacts-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        with mlflow.start_run(run_name=run_name):
            print(f"Started run: {run_name}")
            
            # Log basic parameters
            mlflow.log_param("test_type", "artifacts_only")
            mlflow.log_param("timestamp", datetime.now().isoformat())
            
            # Create and log a JSON artifact
            print("Creating JSON artifact...")
            json_data = {
                "test_id": "artifact_test",
                "timestamp": datetime.now().isoformat(),
                "description": "Test artifact for Azure Blob storage",
                "data": {
                    "value1": 100,
                    "value2": 200,
                    "value3": 300
                }
            }
            
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp_file:
                json.dump(json_data, tmp_file, indent=2)
                tmp_file.flush()
                tmp_file.close()  # Close the file before logging
                mlflow.log_artifact(tmp_file.name, "json_data")
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass  # Ignore deletion errors
            print("✅ JSON artifact logged")
            
            # Create and log a CSV artifact
            print("Creating CSV artifact...")
            csv_data = pd.DataFrame({
                'id': range(1, 11),
                'value': np.random.randn(10),
                'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
            })
            
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as tmp_file:
                csv_data.to_csv(tmp_file.name, index=False)
                tmp_file.flush()
                tmp_file.close()  # Close the file before logging
                mlflow.log_artifact(tmp_file.name, "csv_data")
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass  # Ignore deletion errors
            print("✅ CSV artifact logged")
            
            # Create and log a text file artifact
            print("Creating text artifact...")
            text_content = f"""
            MLflow Azure Blob Storage Test
            =============================
            Timestamp: {datetime.now().isoformat()}
            Storage Account: {storage_account}
            Container: {container_name}
            
            This is a test artifact stored in Azure Blob Storage.
            """
            
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as tmp_file:
                tmp_file.write(text_content)
                tmp_file.flush()
                tmp_file.close()  # Close the file before logging
                mlflow.log_artifact(tmp_file.name, "text_data")
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass  # Ignore deletion errors
            print("✅ Text artifact logged")
            
            # Log run metadata
            run_id = mlflow.active_run().info.run_id
            print(f"\n🎉 Run completed successfully!")
            print(f"Run ID: {run_id}")
            print(f"View run at: http://localhost:5000/#/experiments/{experiment_id}/runs/{run_id}")
            print(f"Artifacts stored in Azure Blob: wasbs://{container_name}@{storage_account}.blob.core.windows.net/")
        
        print("\n✅ All artifacts logged successfully!")
        print("Check your Azure Blob container for the stored artifacts.")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_artifact_test()
