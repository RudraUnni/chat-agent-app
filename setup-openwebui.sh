#!/bin/bash

# Setup Open WebUI Locally Script
echo "🌐 Setting up Open WebUI for Local Development..."

# Create openwebui directory if it doesn't exist
if [ ! -d "openwebui" ]; then
    echo "📁 Creating openwebui directory..."
    mkdir openwebui
fi

cd openwebui

# Check if Open WebUI is already cloned
if [ ! -d "open-webui" ]; then
    echo "📥 Cloning Open WebUI repository..."
    git clone https://github.com/open-webui/open-webui.git
    cd open-webui
else
    echo "📂 Open WebUI already exists, pulling latest changes..."
    cd open-webui
    git pull
fi

echo "📦 Installing Open WebUI dependencies..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "   Please install Node.js (version 18 or higher) from: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    exit 1
fi

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
npm install

# Create .env file for Open WebUI
echo "⚙️  Creating Open WebUI environment configuration..."
cat > .env << EOF
# Open WebUI Local Development Configuration

# Backend URL (your local FastAPI backend)
BACKEND_URL=http://localhost:8000

# Database (using your existing PostgreSQL)
DATABASE_URL=postgresql://chatapp:chatapp_password@localhost:5432/chatapp_db

# OpenAI Configuration (optional - can be set via UI)
OPENAI_API_KEY=your_openai_api_key_here

# Open WebUI Configuration
WEBUI_SECRET_KEY=your-medical-assistant-secret-key-change-this-$(openssl rand -hex 16)
WEBUI_AUTH=false
DEFAULT_MODELS=medical-assistant
ENABLE_SIGNUP=true
ENABLE_LOGIN_FORM=true
WEBUI_NAME=Medical Assistant Chat
ENABLE_COMMUNITY_SHARING=false
ENABLE_MESSAGE_RATING=true
ENABLE_MODEL_FILTER=true

# Disable Ollama (we're using OpenAI)
ENABLE_OLLAMA=false
OLLAMA_BASE_URL=
EOF

echo ""
echo "✅ Open WebUI setup completed!"
echo ""
echo "🚀 To start Open WebUI:"
echo "   cd openwebui/open-webui"
echo "   npm run dev"
echo ""
echo "   Then Open WebUI will be available at: http://localhost:5173"
echo ""
echo "⚠️  Important Notes:"
echo "   1. Make sure your backend is running on http://localhost:8000"
echo "   2. Make sure PostgreSQL is running (use ./start-database.sh)"
echo "   3. Update the OPENAI_API_KEY in openwebui/open-webui/.env with your actual key"
echo ""