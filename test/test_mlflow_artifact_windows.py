#!/usr/bin/env python3
"""
Test script to log an artifact to MLflow with authentication - Windows Version
This script demonstrates logging artifacts with DEBUG logging enabled for Windows local development
Uses Z: drive mount for Azure File Share access
"""

import mlflow
import os
import tempfile
import json
import logging
import sys
from datetime import datetime
from urllib.parse import urlparse

# Enable detailed logging for MLflow
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable MLflow specific logging
mlflow_logger = logging.getLogger('mlflow')
mlflow_logger.setLevel(logging.DEBUG)

# Enable HTTP request logging
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.DEBUG)

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.DEBUG)

def create_test_artifact():
    """Create a simple test artifact"""
    data = {
        "test_id": "artifact_test_windows_001",
        "timestamp": datetime.now().isoformat(),
        "description": "Test artifact for MLflow DEBUG logging verification - Windows Local",
        "version": "1.0.0",
        "metadata": {
            "environment": "dev",
            "platform": "windows",
            "mount_type": "z_drive",
            "mlflow_tracking_log_level": "DEBUG"
        }
    }
    return data

def verify_mount_access(mount_path):
    """Verify mount path is accessible"""
    print(f"Verifying mount access at: {mount_path}")
    
    if not os.path.exists(mount_path):
        return False, f"Mount path does not exist: {mount_path}"
    
    # Test write access
    test_file = os.path.join(mount_path, "mount_test_windows.txt")
    try:
        with open(test_file, 'w') as f:
            f.write(f"Windows mount test - {datetime.now().isoformat()}")
        
        # Clean up test file
        os.remove(test_file)
        
        return True, "Windows mount is working correctly"
        
    except Exception as e:
        return False, f"Windows mount test failed: {e}"

def main():
    """Main function to test MLflow artifact logging on Windows"""
    
    # Windows-specific mount path - Z: drive
    mount_root = 'Z:\\'
    
    # Check if we're running with environment override
    if os.environ.get('MLFLOW_DEFAULT_ARTIFACT_ROOT'):
        # Extract path from file:// URL
        artifact_root = os.environ.get('MLFLOW_DEFAULT_ARTIFACT_ROOT')
        if artifact_root.startswith('file://'):
            mount_root = artifact_root[7:]  # Remove 'file://' prefix
        else:
            mount_root = artifact_root
    
    # Verify mount access
    mount_ok, mount_message = verify_mount_access(mount_root)
    if not mount_ok:
        print(f"ERROR: {mount_message}")
        print("Please ensure the Azure File Share is mounted to Z: drive")
        print("Mount command example:")
        print("  net use Z: \\\\yourstorageaccount.file.core.windows.net\\dev-preprocessed-artifacts /user:yourstorageaccount yourstoragekey")
        sys.exit(1)
    else:
        print(f"✓ {mount_message}")
    
    # Use the MLflow server URL for tracking
    # Check if we're running with environment override or use defaults
    if os.environ.get('MLFLOW_TRACKING_URI'):
        MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI')
        # Check if authentication credentials are provided via environment variables
        USERNAME = os.environ.get('MLFLOW_USERNAME')
        PASSWORD = os.environ.get('MLFLOW_PASSWORD')
    else:
        # Windows local development - use external IP
        MLFLOW_TRACKING_URI = "http://4.144.173.96/mlflowdev"
        USERNAME = "mlops"
        PASSWORD = "mlopsuser"
    
    print("=" * 60)
    print("MLFLOW ARTIFACT TEST - WINDOWS")
    print(f"Mount root: {mount_root}")
    print("=" * 60)
    
    # Print tracking URI first
    print(f"TRACKING URI: {MLFLOW_TRACKING_URI}")
    print(f"Connecting to MLflow server at: {MLFLOW_TRACKING_URI}")
    
    # Set the tracking URI with authentication
    if USERNAME and PASSWORD:
        # Format: http://username:password@host:port/path
        from urllib.parse import urlparse
        parsed_url = urlparse(MLFLOW_TRACKING_URI)
        auth_url = f"http://{USERNAME}:{PASSWORD}@{parsed_url.netloc}{parsed_url.path}"
        print(f"Tracking URI with authentication: {auth_url}")
        mlflow.set_tracking_uri(auth_url)
    else:
        # No authentication needed
        print(f"Tracking URI (no auth): {MLFLOW_TRACKING_URI}")
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Set environment variable for artifact store
    os.environ['MLFLOW_DEFAULT_ARTIFACT_ROOT'] = f"file://{mount_root}"
    print(f"Artifact store: file://{mount_root}")
    
    # Create test data
    test_data = create_test_artifact()
    
    # Start an MLflow run
    with mlflow.start_run(run_name="test_artifact_logging_windows") as run:
        print(f"Started MLflow run: {run.info.run_id}")
        
        # Log parameters
        mlflow.log_param("test_type", "artifact_logging")
        mlflow.log_param("environment", "dev")
        mlflow.log_param("platform", "windows")
        mlflow.log_param("mount_type", "z_drive")
        mlflow.log_param("mlflow_tracking_log_level", "DEBUG")
        mlflow.log_param("connection_mode", "windows_local")
        
        # Log metrics
        mlflow.log_metric("test_score", 0.95)
        mlflow.log_metric("artifact_count", 1)
        mlflow.log_metric("platform_score", 1.0)
        
        # Create and log a JSON artifact
        artifact_path = os.path.join(mount_root, "test-write-access-windows.txt")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        
        with open(artifact_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        try:
            # Log the artifact with detailed logging
            print(f"DEBUG: About to log artifact: {artifact_path}")
            print(f"DEBUG: File exists: {os.path.exists(artifact_path)}")
            print(f"DEBUG: File size: {os.path.getsize(artifact_path)} bytes")
            
            mlflow.log_artifact(artifact_path)
            print(f"Successfully logged artifact: {artifact_path}")
            
            # Log additional metadata
            print("DEBUG: About to log metadata dictionary")
            mlflow.log_dict(test_data, "metadata_windows.json")
            print("Successfully logged metadata dictionary")
            
        except Exception as e:
            print(f"Error logging artifacts: {e}")
            import traceback
            traceback.print_exc()
        
        # Log run info
        print(f"Run completed successfully!")
        print(f"Run ID: {run.info.run_id}")
        print(f"Experiment ID: {run.info.experiment_id}")
        print(f"Status: {run.info.status}")
        
        # Show where artifacts are stored and MLflow UI URL
        print(f"Artifacts stored at: {mount_root}")
        print(f"Run artifacts: {os.path.join(mount_root, run.info.run_id, 'artifacts')}")
        print()
        print("Configuration Summary:")
        print(f"  Tracking Server: {MLFLOW_TRACKING_URI}")
        print(f"  Artifact Store: file://{mount_root}")
        print(f"  Platform: Windows")
        print(f"  Mount Type: Z: Drive")
        print()
        print("View run in MLflow UI:")
        print(f"http://4.144.173.96/mlflowdev/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")

if __name__ == "__main__":
    print("MLflow Artifact Test - Windows Version")
    print("=" * 40)
    print()
    print("Configuration:")
    print("  Tracking Server: http://4.144.173.96/mlflowdev (with authentication)")
    print("  Artifact Store: Z:\\ (Azure File Share mounted locally)")
    print("  Platform: Windows")
    print()
    print("Prerequisites:")
    print("1. Mount Azure File Share to Z: drive:")
    print("   net use Z: \\\\yourstorageaccount.file.core.windows.net\\dev-preprocessed-artifacts /user:yourstorageaccount yourstoragekey")
    print()
    print("2. Verify Z: drive is accessible")
    print()
    print("3. View results in MLflow UI: http://4.144.173.96/mlflowdev/#/experiments")
    print()
    print("Usage:")
    print("  python test_mlflow_artifact_windows.py")
    print()
    print("Environment Variables (optional):")
    print("  MLFLOW_TRACKING_URI - Override tracking server URL")
    print("  MLFLOW_USERNAME - Override username")
    print("  MLFLOW_PASSWORD - Override password")
    print("  MLFLOW_DEFAULT_ARTIFACT_ROOT - Override artifact root")
    print()
    main()
