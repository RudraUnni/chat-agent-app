#!/bin/bash

# Docker Installation Script for Ubuntu/Debian
# This script installs Docker and Docker Compose if they're not available

set -e

echo "🐳 Docker Installation Script"
echo "============================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please run this script as a regular user, not root"
    echo "   The script will use sudo when needed"
    exit 1
fi

# Check if docker is already installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is already installed:"
    docker --version
else
    echo "📦 Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index again
    sudo apt-get update
    
    # Install Docker Engine
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed successfully!"
fi

# Check if docker compose is available
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose is available:"
    docker compose version
else
    echo "❌ Docker Compose plugin not found"
    echo "   Please restart your shell or log out/in to refresh group membership"
fi

echo ""
echo "🔧 Post-installation steps:"
echo "1. If this is a fresh Docker install, please log out and log back in"
echo "2. Or run: newgrp docker"
echo "3. Test with: docker run hello-world"
echo ""
echo "🚀 After Docker is working, you can start the services with:"
echo "   ./start-openwebui.sh"