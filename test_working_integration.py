#!/usr/bin/env python3
"""
Test script for the working OpenWebUI + FastAPI integration
"""

import requests
import time
import json

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

def test_openwebui_access():
    """Test if OpenWebUI is accessible"""
    print("\n🔍 Testing OpenWebUI Access...")
    try:
        response = requests.get("http://localhost:8080", timeout=10)
        if response.status_code == 200:
            print("✅ OpenWebUI: Accessible")
            return True
        else:
            print(f"❌ OpenWebUI: Not accessible (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ OpenWebUI: Connection failed - {e}")
        return False

def test_medical_workflow():
    """Test the medical workflow endpoint"""
    print("\n🔍 Testing Medical Workflow...")
    try:
        payload = {
            "message": "What are the latest treatments for diabetes?",
            "workflow": "pubmed_research",
            "session_id": "test_session_123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Medical Workflow: Working")
                print(f"   Response length: {len(result.get('response', ''))} characters")
                return True
            else:
                print(f"❌ Medical Workflow: Failed - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Medical Workflow: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Medical Workflow: Error - {e}")
        return False

def test_cors_headers():
    """Test CORS headers for OpenWebUI integration"""
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
        if "localhost:8080" in cors_headers or "*" in cors_headers:
            print("✅ CORS: Properly configured for OpenWebUI")
            return True
        else:
            print(f"❌ CORS: Not configured for OpenWebUI (Origin: {cors_headers})")
            return False
    except Exception as e:
        print(f"❌ CORS: Test failed - {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 Medical Assistant Pro - Integration Tests")
    print("=" * 50)
    
    tests = [
        test_backend_health,
        test_openwebui_access,
        test_medical_workflow,
        test_cors_headers
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print("\n💡 You can now:")
        print("   • Access OpenWebUI at http://localhost:8080")
        print("   • Create an account and start chatting")
        print("   • Ask medical questions to test the integration")
    else:
        print(f"❌ Failed: {total - passed}/{total}")
        print("🔧 Some tests failed. Check the error messages above.")
        print("   • Ensure all services are running: docker compose ps")
        print("   • Check logs: docker compose logs")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)