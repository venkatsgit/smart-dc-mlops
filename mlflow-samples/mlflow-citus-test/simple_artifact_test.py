
#!/usr/bin/env python3
"""
Simple test to check if artifacts work
"""

import mlflow
import tempfile
import json

# Connect to MLflow
mlflow.set_tracking_uri("http://localhost:5000")

print("🧪 Testing simple artifact logging...")

# Set experiment
try:
    mlflow.create_experiment("simple_artifact_test")
except:
    pass
mlflow.set_experiment("simple_artifact_test")

# Start run
with mlflow.start_run() as run:
    print(f"Run ID: {run.info.run_id}")
    print(f"Artifact URI: {run.info.artifact_uri}")
    
    # Test 1: Log a simple parameter and metric (should work)
    mlflow.log_param("test_param", "artifact_test")
    mlflow.log_metric("test_metric", 1.0)
    print("✅ Parameters and metrics logged")
    
    # Test 2: Try mlflow.log_dict (JSON artifacts)
    try:
        test_data = {"message": "Hello from MLflow!", "timestamp": "2025-08-21"}
        mlflow.log_dict(test_data, "test_message.json")
        print("✅ JSON artifact logged successfully")
    except Exception as e:
        print(f"❌ JSON artifact failed: {e}")
    
    # Test 3: Try creating and logging a simple text file
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test artifact file\n")
            f.write(f"Run ID: {run.info.run_id}\n")
            temp_path = f.name
        
        mlflow.log_artifact(temp_path, "test_files")
        print("✅ Text file artifact logged successfully")
        
        # Clean up
        import os
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Text file artifact failed: {e}")

print("🎉 Simple artifact test completed")
print("🌐 Check MLflow UI: http://localhost:5000")


# Run the simple test
