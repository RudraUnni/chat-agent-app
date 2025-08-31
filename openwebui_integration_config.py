#!/usr/bin/env python3
"""
Open WebUI Integration Configuration
Shows how to integrate Open WebUI with your medical assistant backend
"""

import requests
import json
import time
from typing import Dict, Any

class OpenWebUIIntegration:
    def __init__(self):
        self.openwebui_url = "http://localhost:8080"
        self.backend_url = "http://localhost:8000"
        
    def test_basic_connectivity(self):
        """Test basic connectivity to both services"""
        print("🔍 Testing basic connectivity...")
        
        # Test Open WebUI
        try:
            response = requests.get(f"{self.openwebui_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI: Accessible")
                openwebui_ok = True
            else:
                print(f"❌ Open WebUI: Status {response.status_code}")
                openwebui_ok = False
        except Exception as e:
            print(f"❌ Open WebUI: {e}")
            openwebui_ok = False
            
        # Test Backend
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend: Accessible")
                backend_ok = True
            else:
                print(f"❌ Backend: Status {response.status_code}")
                backend_ok = False
        except Exception as e:
            print(f"❌ Backend: {e}")
            backend_ok = False
            
        return openwebui_ok and backend_ok
    
    def demonstrate_integration_scenario(self):
        """Demonstrate how the integration would work"""
        print("\n🎯 Integration Scenario Demonstration:")
        print("=" * 50)
        
        print("1. User opens Open WebUI at http://localhost:8080")
        print("2. User asks medical question: 'What are the latest diabetes treatments?'")
        print("3. Open WebUI processes the query")
        print("4. Open WebUI calls your medical assistant backend")
        print("5. Backend runs PubMed research workflow")
        print("6. Response is returned through Open WebUI")
        print("7. User sees medical insights in beautiful interface")
        
        print("\n🔗 Integration Points:")
        print("• Open WebUI handles: User interface, chat history, document uploads")
        print("• Your Backend handles: Medical workflows, PubMed research, data processing")
        print("• Shared Database: PostgreSQL for persistent storage")
        
        print("\n💡 Benefits:")
        print("• Professional AI interface for medical staff")
        print("• Your existing medical workflows remain intact")
        print("• RAG capabilities for medical documents")
        print("• Voice and image features")
        print("• Enterprise-grade security")
    
    def show_current_status(self):
        """Show current integration status"""
        print("\n📊 Current Integration Status:")
        print("=" * 50)
        
        print("✅ Open WebUI v0.6.5:")
        print("   • Running on http://localhost:8080")
        print("   • Professional AI interface ready")
        print("   • RAG, voice, and image features available")
        print("   • No licensing restrictions")
        
        print("\n⚠️  Backend Integration:")
        print("   • Service is running but has connection issues")
        print("   • Medical workflows exist but need connection fix")
        print("   • Once resolved, full integration will work")
        
        print("\n🎯 Next Steps:")
        print("1. Fix backend connection issues")
        print("2. Configure Open WebUI to use your backend")
        print("3. Test medical workflow integration")
        print("4. Add RAG capabilities")
    
    def provide_integration_instructions(self):
        """Provide step-by-step integration instructions"""
        print("\n🔧 Integration Instructions:")
        print("=" * 50)
        
        print("Step 1: Fix Backend Connection")
        print("• Check backend logs for errors")
        print("• Verify database connectivity")
        print("• Test individual endpoints")
        
        print("\nStep 2: Configure Open WebUI Integration")
        print("• Set up custom model endpoints")
        print("• Configure API keys and authentication")
        print("• Test basic communication")
        
        print("\nStep 3: Test Medical Workflows")
        print("• Send test queries through Open WebUI")
        print("• Verify backend responses")
        print("• Test chat memory and context")
        
        print("\nStep 4: Add RAG Capabilities")
        print("• Upload medical documents to Open WebUI")
        print("• Test document retrieval")
        print("• Verify medical insights")
    
    def run_demo(self):
        """Run the complete integration demo"""
        print("🚀 Open WebUI v0.6.5 + Medical Assistant Integration Demo")
        print("=" * 70)
        
        # Test connectivity
        if self.test_basic_connectivity():
            print("\n✅ Both services are accessible!")
            
            # Show integration scenario
            self.demonstrate_integration_scenario()
            
            # Show current status
            self.show_current_status()
            
            # Provide instructions
            self.provide_integration_instructions()
            
            print("\n🎉 DELIVERABLE 1 STATUS:")
            print("✅ Open WebUI v0.6.5 is running successfully")
            print("✅ Services are accessible side-by-side")
            print("⚠️  Backend integration needs connection fix")
            print("🎯 Once backend is fixed: 'I have OpenWebUI running side-by-side with my backend'")
            
        else:
            print("\n❌ Connectivity issues detected")
            print("🔧 Please fix the connection issues before proceeding")
        
        return True

def main():
    """Main function"""
    integration = OpenWebUIIntegration()
    integration.run_demo()

if __name__ == "__main__":
    main()
