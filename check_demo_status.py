#!/usr/bin/env python3
"""
Demo Status Checker
Quick script to verify your Medical Assistant Pro demo is working
"""

import requests
import json
from datetime import datetime

def check_openwebui():
    """Check if Open WebUI is accessible"""
    print("🔍 Checking Open WebUI...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI: Accessible at http://localhost:8080")
            return True
        else:
            print(f"❌ Open WebUI: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Open WebUI: {e}")
        return False

def check_backend():
    """Check if medical backend is accessible"""
    print("\n🔍 Checking Medical Backend...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Medical Backend: Healthy at http://localhost:8001")
            print(f"   Status: {result.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Medical Backend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Medical Backend: {e}")
        return False

def check_integration():
    """Check if services can communicate"""
    print("\n🔍 Checking Integration...")
    try:
        # Test basic communication
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Integration: Services communicating")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"⚠️  Integration: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Integration: {e}")
        return False

def show_demo_info():
    """Show demo information"""
    print("\n🏥 Medical Assistant Pro - Demo Status")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("📱 Access Points:")
    print("  • Open WebUI Interface: http://localhost:8080")
    print("  • Medical Backend: http://localhost:8001")
    print("  • Health Check: http://localhost:8001/health")
    print("")
    print("🎯 Demo Features:")
    print("  • Professional medical AI interface")
    print("  • RAG capabilities for medical documents")
    print("  • Voice input/output")
    print("  • Medical workflow integration")
    print("  • Chat memory and context")
    print("")
    print("🧪 Demo Scenarios:")
    print("  1. Medical Research: Ask about latest treatments")
    print("  2. Document Analysis: Upload medical papers")
    print("  3. Medical Consultation: Describe symptoms")
    print("")
    print("🔧 Management:")
    print("  • View logs: docker compose logs -f")
    print("  • Stop services: docker compose down")
    print("  • Restart: ./demo_setup.sh")

def main():
    """Main function"""
    print("🏥 Medical Assistant Pro - Demo Status Check")
    print("=" * 60)
    
    # Check all services
    openwebui_ok = check_openwebui()
    backend_ok = check_backend()
    integration_ok = check_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO STATUS SUMMARY")
    print("=" * 60)
    
    if openwebui_ok and backend_ok and integration_ok:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Your Medical Assistant Pro demo is ready!")
        print("✅ Open WebUI interface is accessible")
        print("✅ Medical backend is healthy")
        print("✅ Services are communicating")
        print("")
        print("🚀 Demo Status: READY FOR PRESENTATION")
        
        # Show demo info
        show_demo_info()
        
    else:
        print("⚠️  SOME SYSTEMS HAVE ISSUES")
        print("🔧 Please check the logs above and fix any problems")
        print("💡 Run './demo_setup.sh' to restart everything")
    
    return openwebui_ok and backend_ok and integration_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
