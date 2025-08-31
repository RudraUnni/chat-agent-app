#!/usr/bin/env python3
"""
Simple Deliverable 1 Test
Quick test to prove OpenWebUI and backend are running side-by-side
"""

import requests
import time

def quick_test():
    """Quick test of both services"""
    print("🚀 Quick Deliverable 1 Test")
    print("=" * 40)
    
    # Test Open WebUI
    print("🔍 Testing Open WebUI...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI: RUNNING on http://localhost:8080")
        else:
            print(f"❌ Open WebUI: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Open WebUI: {e}")
        return False
    
    # Test Backend
    print("\n🔍 Testing Backend...")
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend: RUNNING on http://localhost:8001")
            print(f"   • Message: {result.get('message', 'No message')}")
        else:
            print(f"❌ Backend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend: {e}")
        return False
    
    print("\n🎉 DELIVERABLE 1 ACHIEVED!")
    print("✅ OpenWebUI is running side-by-side with your backend")
    print("✅ Both services are operational and accessible")
    
    return True

if __name__ == "__main__":
    quick_test()
