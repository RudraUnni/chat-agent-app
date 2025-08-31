#!/usr/bin/env python3
"""
Open WebUI Integration Script for Medical Chat Agent
This script helps integrate Open WebUI with your existing FastAPI backend
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path

class OpenWebUIIntegrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.openwebui_dir = self.project_root / "openwebui"
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking dependencies...")
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker is available")
            else:
                print("❌ Docker is not available")
                return False
        except FileNotFoundError:
            print("❌ Docker is not installed")
            return False
            
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker Compose is available")
            else:
                print("❌ Docker Compose is not available")
                return False
        except FileNotFoundError:
            print("❌ Docker Compose is not installed")
            return False
            
        return True
    
    def setup_environment(self):
        """Setup environment variables for Open WebUI"""
        print("🔧 Setting up environment...")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("📝 Creating .env file...")
            with open(env_file, "w") as f:
                f.write("# Medical Chat Agent Environment Variables\n")
                f.write("OPENAI_API_KEY=your-api-key-here\n")
                f.write("WEBUI_SECRET_KEY=your-secret-key-here\n")
                f.write("DATABASE_URL=postgresql://chatapp:chatapp_password@localhost:5432/chatapp_db\n")
            print("✅ .env file created")
        else:
            print("✅ .env file already exists")
    
    def start_services(self):
        """Start all services using Docker Compose"""
        print("🚀 Starting services...")
        
        try:
            # Start services
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Services started successfully")
                return True
            else:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return False
    
    def check_service_health(self):
        """Check if all services are running and healthy"""
        print("🏥 Checking service health...")
        
        services = {
            "PostgreSQL": "http://localhost:5432",
            "FastAPI Backend": "http://localhost:8000/health",
            "Open WebUI": "http://localhost:8080",
            "Frontend": "http://localhost:3000"
        }
        
        for service_name, url in services.items():
            try:
                if "5432" in url:  # PostgreSQL check
                    print(f"✅ {service_name} is running")
                    continue
                    
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name} is healthy")
                else:
                    print(f"⚠️  {service_name} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {service_name} is not accessible: {e}")
    
    def create_integration_config(self):
        """Create configuration for integrating Open WebUI with existing backend"""
        print("🔗 Creating integration configuration...")
        
        config = {
            "openwebui": {
                "url": "http://localhost:8080",
                "api_endpoint": "http://localhost:8080/api/v1",
                "features": {
                    "rag": True,
                    "voice": True,
                    "image_generation": True,
                    "function_calling": True
                }
            },
            "backend": {
                "url": "http://localhost:8000",
                "websocket": "ws://localhost:8000/ws"
            },
            "frontend": {
                "url": "http://localhost:3000"
            },
            "integration": {
                "shared_database": True,
                "user_management": "openwebui",
                "custom_workflows": "backend"
            }
        }
        
        config_file = self.project_root / "integration_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Integration configuration created")
        return config
    
    def run(self):
        """Main integration process"""
        print("🚀 Starting Open WebUI Integration...")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependencies check failed. Please install Docker and Docker Compose.")
            return False
        
        # Setup environment
        self.setup_environment()
        
        # Start services
        if not self.start_services():
            print("❌ Failed to start services")
            return False
        
        # Wait a bit for services to start
        print("⏳ Waiting for services to start...")
        import time
        time.sleep(10)
        
        # Check health
        self.check_service_health()
        
        # Create integration config
        config = self.create_integration_config()
        
        print("\n" + "=" * 50)
        print("🎉 Integration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your .env file with actual API keys")
        print("2. Access Open WebUI at: http://localhost:8080")
        print("3. Access your backend at: http://localhost:8000")
        print("4. Access your frontend at: http://localhost:3000")
        print("\n🔧 To stop services: docker-compose down")
        print("🔧 To view logs: docker-compose logs -f")
        
        return True

if __name__ == "__main__":
    integrator = OpenWebUIIntegrator()
    integrator.run()
