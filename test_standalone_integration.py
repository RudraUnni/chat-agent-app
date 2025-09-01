#!/usr/bin/env python3
"""
Standalone Integration Test for Medical Assistant Pro
Tests the backend when running without Docker
"""

import requests
import time
import json
import sys
import subprocess
import threading
from pathlib import Path

def test_backend_health():
    """Test if the FastAPI backend is healthy"""
    print("🔍 Testing FastAPI Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend: Healthy")
            return True
        else:
            print(f"❌ Backend: Unhealthy (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend: Connection failed - {e}")
        return False

def test_backend_root():
    """Test if the FastAPI backend root endpoint works"""
    print("\n🔍 Testing Backend Root Endpoint...")
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend Root: Working - {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Backend Root: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Root: Error - {e}")
        return False

def test_medical_workflow_simple():
    """Test a simple medical workflow without complex dependencies"""
    print("\n🔍 Testing Simple Medical Query...")
    try:
        payload = {
            "message": "Hello, can you help me with a medical question?",
            "workflow": "pubmed_research",
            "session_id": "test_session_standalone"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15  # Shorter timeout for testing
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Medical Workflow: Basic functionality working")
                response_text = result.get("response", "")
                if len(response_text) > 0:
                    print(f"   Response preview: {response_text[:100]}...")
                return True
            else:
                print(f"❌ Medical Workflow: Failed - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Medical Workflow: HTTP {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Medical Workflow: Error - {e}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔍 Testing CORS Configuration...")
    try:
        response = requests.options(
            "http://localhost:8000/api/v1/chat",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
        if "*" in cors_headers or "localhost:8080" in cors_headers:
            print("✅ CORS: Properly configured")
            return True
        else:
            print(f"❌ CORS: Not configured properly (Origin: {cors_headers})")
            return False
    except Exception as e:
        print(f"❌ CORS: Test failed - {e}")
        return False

def check_backend_running():
    """Check if backend is already running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend_if_needed():
    """Start backend if it's not running"""
    if check_backend_running():
        print("✅ Backend is already running")
        return True
    
    print("🔍 Backend not running. Checking if we can start it...")
    
    # Check if we have the backend files
    backend_path = Path("backend/app/main.py")
    if not backend_path.exists():
        print("❌ Backend files not found. Cannot start backend automatically.")
        print("💡 Please ensure you're in the project root directory.")
        return False
    
    print("💡 To start the backend manually, run in another terminal:")
    print("   python3 run_backend_standalone.py")
    print("")
    print("   Or if you have Docker available:")
    print("   ./run_working_demo.sh")
    
    return False

def main():
    """Run all integration tests"""
    print("🧪 Medical Assistant Pro - Standalone Integration Tests")
    print("=" * 60)
    
    # Check if backend is running
    if not start_backend_if_needed():
        print("\n❌ Backend is not running. Please start it first.")
        return False
    
    tests = [
        test_backend_health,
        test_backend_root,
        test_medical_workflow_simple,
        test_cors_headers
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All tests passed! Backend integration is working correctly.")
        print("\n💡 Next steps:")
        print("   • The backend is working and ready for integration")
        print("   • You can now connect OpenWebUI or other frontends")
        print("   • Try medical queries like: 'What are treatments for diabetes?'")
    elif passed > 0:
        print(f"⚠️ Partial success: {passed} out of {total} tests passed.")
        print("🔧 Some functionality is working. Check the errors above.")
    else:
        print(f"❌ All tests failed. Check the error messages above.")
        print("🔧 Troubleshooting steps:")
        print("   • Ensure backend is running: python3 run_backend_standalone.py")
        print("   • Check backend logs for errors")
        print("   • Verify port 8000 is not blocked")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)