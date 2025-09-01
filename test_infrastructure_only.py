#!/usr/bin/env python3
"""
Infrastructure Test Script - Tests everything except API-dependent features
"""

import requests
import time
import json
import subprocess

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

def test_docker_services():
    """Test if all Docker services are running"""
    print("\n🔍 Testing Docker Services...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "table {{.Name}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')[1:]  # Skip header
            all_running = True
            
            for service in services:
                if service.strip():
                    name, status = service.split('\t')
                    if "Up" in status:
                        print(f"✅ {name}: Running")
                    else:
                        print(f"❌ {name}: {status}")
                        all_running = False
            
            return all_running
        else:
            print(f"❌ Docker Compose: Command failed")
            return False
    except Exception as e:
        print(f"❌ Docker Services: Error - {e}")
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

def test_backend_endpoints():
    """Test backend endpoints (without API key)"""
    print("\n🔍 Testing Backend Endpoints...")
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend Root: Accessible")
        else:
            print(f"❌ Backend Root: Failed (Status: {response.status_code})")
            return False
        
        # Test API endpoint structure (should return error, not connection failure)
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={"message": "test", "workflow": "pubmed_research"},
            timeout=10
        )
        
        # Should get a response (even if it's an error about API key)
        if response.status_code in [200, 400, 401, 422]:
            print("✅ Backend API: Endpoint accessible")
            return True
        else:
            print(f"❌ Backend API: Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Backend Endpoints: Error - {e}")
        return False

def test_nginx_proxy():
    """Test nginx proxy functionality"""
    print("\n🔍 Testing Nginx Proxy...")
    try:
        # Test nginx proxy to OpenWebUI
        response = requests.get("http://localhost", timeout=10)
        if response.status_code == 200:
            print("✅ Nginx Proxy: Working (OpenWebUI accessible via proxy)")
            return True
        else:
            print(f"❌ Nginx Proxy: Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Nginx Proxy: Error - {e}")
        return False

def main():
    """Run all infrastructure tests"""
    print("🧪 Medical Assistant Pro - Infrastructure Tests")
    print("=" * 60)
    print("Testing everything except API-dependent features")
    print("=" * 60)
    
    tests = [
        test_docker_services,
        test_backend_health,
        test_openwebui_access,
        test_nginx_proxy,
        test_cors_headers,
        test_backend_endpoints
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print("📊 Infrastructure Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All infrastructure tests passed!")
        print("\n💡 Your integration is working correctly:")
        print("   • All Docker services are running")
        print("   • OpenWebUI interface is accessible")
        print("   • Backend API is responding")
        print("   • Network connectivity is working")
        print("   • CORS is properly configured")
        print("\n🔑 Next step: Update your OpenAI API key in .env file")
        print("   Then run: python3 test_working_integration.py")
    else:
        print(f"❌ Failed: {total - passed}/{total}")
        print("🔧 Some infrastructure issues found. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
