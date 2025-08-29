#!/usr/bin/env python3
"""
Test script to verify MLflow deployment
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def test_namespace(environment):
    """Test if namespace exists"""
    namespace = f"smart-dc-{environment}"
    print(f"Testing namespace: {namespace}")
    
    stdout, stderr, returncode = run_command(f"kubectl get namespace {namespace}")
    if returncode == 0:
        print(f"✅ Namespace {namespace} exists")
        return True
    else:
        print(f"❌ Namespace {namespace} does not exist")
        return False

def test_pods(environment):
    """Test if MLflow pods are running"""
    namespace = f"smart-dc-{environment}"
    print(f"Testing MLflow pods in namespace: {namespace}")
    
    stdout, stderr, returncode = run_command(f"kubectl get pods -n {namespace} -l app=mlflow -o json")
    if returncode == 0:
        try:
            pods_data = json.loads(stdout)
            if pods_data['items']:
                for pod in pods_data['items']:
                    pod_name = pod['metadata']['name']
                    pod_status = pod['status']['phase']
                    print(f"Pod: {pod_name} - Status: {pod_status}")
                    
                    if pod_status == 'Running':
                        print(f"✅ Pod {pod_name} is running")
                    else:
                        print(f"⚠️  Pod {pod_name} is not running (status: {pod_status})")
                return True
            else:
                print("❌ No MLflow pods found")
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse pod information")
            return False
    else:
        print(f"❌ Failed to get pods: {stderr}")
        return False

def test_services(environment):
    """Test if MLflow services are created"""
    namespace = f"smart-dc-{environment}"
    print(f"Testing MLflow services in namespace: {namespace}")
    
    stdout, stderr, returncode = run_command(f"kubectl get svc -n {namespace} -l app=mlflow -o json")
    if returncode == 0:
        try:
            svc_data = json.loads(stdout)
            if svc_data['items']:
                for svc in svc_data['items']:
                    svc_name = svc['metadata']['name']
                    svc_type = svc['spec']['type']
                    svc_port = svc['spec']['ports'][0]['port']
                    print(f"✅ Service {svc_name} ({svc_type}) on port {svc_port}")
                return True
            else:
                print("❌ No MLflow services found")
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse service information")
            return False
    else:
        print(f"❌ Failed to get services: {stderr}")
        return False

def test_storage(environment):
    """Test if storage resources are created"""
    namespace = f"smart-dc-{environment}"
    print(f"Testing storage resources in namespace: {namespace}")
    
    # Test PVC
    stdout, stderr, returncode = run_command(f"kubectl get pvc -n {namespace} -l app=mlflow -o json")
    if returncode == 0:
        try:
            pvc_data = json.loads(stdout)
            if pvc_data['items']:
                for pvc in pvc_data['items']:
                    pvc_name = pvc['metadata']['name']
                    pvc_status = pvc['status']['phase']
                    print(f"✅ PVC {pvc_name} - Status: {pvc_status}")
                return True
            else:
                print("❌ No MLflow PVCs found")
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse PVC information")
            return False
    else:
        print(f"❌ Failed to get PVCs: {stderr}")
        return False

def test_secrets(environment):
    """Test if secrets are created"""
    namespace = f"smart-dc-{environment}"
    print(f"Testing secrets in namespace: {namespace}")
    
    stdout, stderr, returncode = run_command(f"kubectl get secrets -n {namespace} -l app=mlflow -o json")
    if returncode == 0:
        try:
            secret_data = json.loads(stdout)
            if secret_data['items']:
                for secret in secret_data['items']:
                    secret_name = secret['metadata']['name']
                    secret_type = secret['type']
                    print(f"✅ Secret {secret_name} ({secret_type})")
                return True
            else:
                print("❌ No MLflow secrets found")
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse secret information")
            return False
    else:
        print(f"❌ Failed to get secrets: {stderr}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) != 2:
        print("Usage: python test-deployment.py [dev|prod]")
        sys.exit(1)
    
    environment = sys.argv[1]
    if environment not in ['dev', 'prod']:
        print("Invalid environment. Use 'dev' or 'prod'")
        sys.exit(1)
    
    print(f"🧪 Testing MLflow deployment for {environment} environment")
    print("=" * 50)
    
    tests = [
        ("Namespace", test_namespace),
        ("Pods", test_pods),
        ("Services", test_services),
        ("Storage", test_storage),
        ("Secrets", test_secrets)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} Test:")
        try:
            result = test_func(environment)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MLflow deployment looks good.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
