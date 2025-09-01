#!/usr/bin/env python3
"""
Standalone Backend Runner for Medical Assistant Pro
Runs the FastAPI backend without Docker when Docker is not available
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def print_status(message):
    print(f"🔍 [INFO] {message}")

def print_success(message):
    print(f"✅ [SUCCESS] {message}")

def print_error(message):
    print(f"❌ [ERROR] {message}")

def print_warning(message):
    print(f"⚠️ [WARNING] {message}")

def check_dependencies():
    """Check if required Python packages are installed"""
    print_status("Checking Python dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "pydantic",
        "python-multipart"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print_error(f"{package}: Missing")
    
    if missing_packages:
        print_warning("Installing missing packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--break-system-packages"
            ] + missing_packages)
            print_success("Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print_error("Failed to install dependencies")
            print("Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def create_mock_database():
    """Create a mock database connection for testing"""
    print_status("Setting up mock database...")
    
    # Create a simple in-memory database mock
    mock_db_code = '''
import asyncio
from typing import Optional

# Mock database connection
class MockDatabase:
    def __init__(self):
        self.connected = True
    
    async def connect(self):
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    def is_healthy(self):
        return self.connected

# Global mock database instance
mock_db = MockDatabase()

async def init_db():
    """Initialize mock database"""
    await mock_db.connect()
    print("✅ Mock database initialized")

async def close_db():
    """Close mock database"""
    await mock_db.disconnect()
    print("✅ Mock database closed")

def get_db():
    """Get database connection"""
    return mock_db
'''
    
    # Write mock database module
    mock_db_path = backend_path / "app" / "database" / "mock_connection.py"
    with open(mock_db_path, "w") as f:
        f.write(mock_db_code)
    
    print_success("Mock database created")

def update_backend_for_standalone():
    """Update backend configuration for standalone mode"""
    print_status("Updating backend configuration for standalone mode...")
    
    # Read current main.py
    main_py_path = backend_path / "app" / "main.py"
    if not main_py_path.exists():
        print_error(f"Backend main.py not found at {main_py_path}")
        return False
    
    with open(main_py_path, "r") as f:
        content = f.read()
    
    # Update imports to use mock database
    updated_content = content.replace(
        "from app.database.connection import init_db, close_db",
        "from app.database.mock_connection import init_db, close_db"
    )
    
    # Add CORS for all origins in standalone mode
    if "allow_origins=" in updated_content:
        updated_content = updated_content.replace(
            'allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://open-webui:8080"],',
            'allow_origins=["*"],  # Allow all origins in standalone mode'
        )
    
    # Write updated main.py
    with open(main_py_path, "w") as f:
        f.write(updated_content)
    
    print_success("Backend configuration updated for standalone mode")
    return True

def run_backend():
    """Run the FastAPI backend"""
    print_status("Starting FastAPI backend on port 8000...")
    
    # Change to backend directory
    os.chdir(backend_path)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(backend_path)
    os.environ["OPENAI_API_KEY"] = "demo-key-not-required-for-testing"
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print_success("Backend stopped by user")
    except Exception as e:
        print_error(f"Failed to start backend: {e}")

def main():
    """Main function"""
    print("🏥 Medical Assistant Pro - Standalone Backend Runner")
    print("=" * 55)
    
    # Check if backend directory exists
    if not backend_path.exists():
        print_error(f"Backend directory not found: {backend_path}")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create mock database
    create_mock_database()
    
    # Update backend configuration
    if not update_backend_for_standalone():
        return 1
    
    print_success("Setup complete! Starting backend...")
    print_status("Backend will be available at: http://localhost:8000")
    print_status("Health check: http://localhost:8000/health")
    print_status("Press Ctrl+C to stop")
    print()
    
    # Run backend
    try:
        run_backend()
    except KeyboardInterrupt:
        print_success("Backend stopped")
        return 0
    
    return 0

if __name__ == "__main__":
    exit(main())