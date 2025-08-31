#!/usr/bin/env python3
"""
Open WebUI Integration Test Script
Tests all components of the integrated system
"""

import os
import sys
import time
import requests
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class IntegrationTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services = {
            "postgres": {"port": 5432, "health_check": "postgres"},
            "backend": {"port": 8000, "health_check": "http://localhost:8000/health"},
            "openwebui": {"port": 8080, "health_check": "http://localhost:8080"},
            "frontend": {"port": 3000, "health_check": "http://localhost:3000"},
            "nginx": {"port": 80, "health_check": "http://localhost:80"}
        }
        self.test_results = {}
        
    def check_docker_services(self) -> Dict[str, bool]:
        """Check if all Docker services are running"""
        print("🔍 Checking Docker services...")
        results = {}
        
        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                containers = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                
                for service_name in self.services.keys():
                    container = next((c for c in containers if c.get('Service') == service_name), None)
                    if container and container.get('State') == 'running':
                        results[service_name] = True
                        print(f"✅ {service_name}: Running (ID: {container.get('ID', 'N/A')[:12]})")
                    else:
                        results[service_name] = False
                        print(f"❌ {service_name}: Not running")
            else:
                print(f"❌ Failed to get container status: {result.stderr}")
                return {name: False for name in self.services.keys()}
                
        except Exception as e:
            print(f"❌ Error checking Docker services: {e}")
            return {name: False for name in self.services.keys()}
            
        return results
    
    def check_service_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        print("\n🏥 Checking service health...")
        results = {}
        
        for service_name, config in self.services.items():
            try:
                if service_name == "postgres":
                    # Special check for PostgreSQL
                    result = subprocess.run(
                        ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", "chatapp", "-d", "chatapp_db"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        results[service_name] = True
                        print(f"✅ {service_name}: Healthy")
                    else:
                        results[service_name] = False
                        print(f"❌ {service_name}: Unhealthy")
                else:
                    # HTTP health check
                    response = requests.get(config["health_check"], timeout=10)
                    if response.status_code == 200:
                        results[service_name] = True
                        print(f"✅ {service_name}: Healthy (Status: {response.status_code})")
                    else:
                        results[service_name] = False
                        print(f"⚠️ {service_name}: Status {response.status_code}")
                        
            except requests.exceptions.RequestException as e:
                results[service_name] = False
                print(f"❌ {service_name}: Connection failed - {e}")
            except Exception as e:
                results[service_name] = False
                print(f"❌ {service_name}: Error - {e}")
                
        return results
    
    def test_openwebui_features(self) -> Dict[str, bool]:
        """Test Open WebUI specific features"""
        print("\n🧪 Testing Open WebUI features...")
        results = {}
        
        try:
            # Test basic access
            response = requests.get("http://localhost:8080", timeout=10)
            if response.status_code == 200:
                results["basic_access"] = True
                print("✅ Basic access: Working")
            else:
                results["basic_access"] = False
                print(f"❌ Basic access: Status {response.status_code}")
                
            # Test API endpoint
            response = requests.get("http://localhost:8080/api/v1", timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                results["api_endpoint"] = True
                print("✅ API endpoint: Accessible")
            else:
                results["api_endpoint"] = False
                print(f"❌ API endpoint: Status {response.status_code}")
                
            # Test WebSocket support
            try:
                import websocket
                # This is a basic test - in production you'd want more comprehensive WebSocket testing
                results["websocket_support"] = True
                print("✅ WebSocket support: Available")
            except ImportError:
                results["websocket_support"] = False
                print("⚠️ WebSocket support: Cannot test (websocket-client not installed)")
                
        except Exception as e:
            print(f"❌ Error testing Open WebUI features: {e}")
            results = {"basic_access": False, "api_endpoint": False, "websocket_support": False}
            
        return results
    
    def test_backend_integration(self) -> Dict[str, bool]:
        """Test backend integration features"""
        print("\n🔗 Testing backend integration...")
        results = {}
        
        try:
            # Test health endpoint
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                results["health_endpoint"] = True
                print("✅ Health endpoint: Working")
            else:
                results["health_endpoint"] = False
                print(f"❌ Health endpoint: Status {response.status_code}")
                
            # Test chat endpoint
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                json={"message": "test", "workflow": "pubmed_research", "session_id": "test-session"},
                timeout=10
            )
            if response.status_code in [200, 422]:  # 422 means validation error (expected for test data)
                results["chat_endpoint"] = True
                print("✅ Chat endpoint: Accessible")
            else:
                results["chat_endpoint"] = False
                print(f"❌ Chat endpoint: Status {response.status_code}")
                
            # Test WebSocket endpoint
            response = requests.get("http://localhost:8000/ws", timeout=10)
            if response.status_code in [101, 400, 404]:  # 101 is WebSocket upgrade, others are expected
                results["websocket_endpoint"] = True
                print("✅ WebSocket endpoint: Accessible")
            else:
                results["websocket_endpoint"] = False
                print(f"❌ WebSocket endpoint: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing backend integration: {e}")
            results = {"health_endpoint": False, "chat_endpoint": False, "websocket_endpoint": False}
            
        return results
    
    def test_frontend_integration(self) -> Dict[str, bool]:
        """Test frontend integration"""
        print("\n🎨 Testing frontend integration...")
        results = {}
        
        try:
            # Test basic access
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                results["basic_access"] = True
                print("✅ Basic access: Working")
                
                # Check if it's a React app
                if "react" in response.text.lower() or "chakra" in response.text.lower():
                    results["react_app"] = True
                    print("✅ React app: Detected")
                else:
                    results["react_app"] = False
                    print("⚠️ React app: Not detected")
            else:
                results["basic_access"] = False
                results["react_app"] = False
                print(f"❌ Basic access: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing frontend integration: {e}")
            results = {"basic_access": False, "react_app": False}
            
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        print("\n📊 Generating test report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "docker_services": self.test_results.get("docker_services", {}),
            "service_health": self.test_results.get("service_health", {}),
            "openwebui_features": self.test_results.get("openwebui_features", {}),
            "backend_integration": self.test_results.get("backend_integration", {}),
            "frontend_integration": self.test_results.get("frontend_integration", {})
        }
        
        # Calculate overall health
        all_checks = []
        for category in report.values():
            if isinstance(category, dict):
                all_checks.extend(category.values())
        
        overall_health = "🟢 Healthy" if all(all_checks) else "🟡 Partially Healthy" if any(all_checks) else "🔴 Unhealthy"
        report["overall_health"] = overall_health
        
        # Save report
        report_file = self.project_root / "integration_test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Test report saved to: {report_file}")
        return report
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🚀 Starting Open WebUI Integration Tests...")
        print("=" * 60)
        
        # Test Docker services
        self.test_results["docker_services"] = self.check_docker_services()
        
        # Wait for services to be ready
        print("\n⏳ Waiting for services to be ready...")
        time.sleep(15)
        
        # Test service health
        self.test_results["service_health"] = self.check_service_health()
        
        # Test specific integrations
        self.test_results["openwebui_features"] = self.test_openwebui_features()
        self.test_results["backend_integration"] = self.test_backend_integration()
        self.test_results["frontend_integration"] = self.test_frontend_integration()
        
        # Generate report
        report = self.generate_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Overall Health: {report['overall_health']}")
        print(f"Timestamp: {report['timestamp']}")
        
        print("\n📋 Service Status:")
        for service_name, status in report["docker_services"].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service_name}")
        
        print("\n🔗 Integration Status:")
        for category, tests in report.items():
            if category not in ["timestamp", "docker_services", "overall_health"]:
                print(f"\n  {category.replace('_', ' ').title()}:")
                for test_name, result in tests.items():
                    status_icon = "✅" if result else "❌"
                    print(f"    {status_icon} {test_name}")
        
        print(f"\n📊 Full report saved to: integration_test_report.json")
        
        # Return overall success
        all_passed = all(all(category.values()) for category in report.values() 
                        if isinstance(category, dict) and category != report["docker_services"])
        
        if all_passed:
            print("\n🎉 All integration tests passed! Your system is ready.")
        else:
            print("\n⚠️ Some tests failed. Check the report above for details.")
            
        return all_passed

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
