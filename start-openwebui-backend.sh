#!/bin/bash

# Start OpenWebUI Backend Only
echo "🐍 Starting OpenWebUI Backend..."

# Check if Open WebUI is set up
if [ ! -d "openwebui/open-webui" ]; then
    echo "❌ Error: Open WebUI not found. Please run ./setup-local-dev.sh first"
    exit 1
fi

cd openwebui/open-webui

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up OpenWebUI backend environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo "   ✅ OpenWebUI backend environment created"
else
    echo "   ⚠️  OpenWebUI backend environment already exists, skipping..."
fi

# Create pipeline symlink for local development
echo "🔗 Setting up pipeline integration..."
PIPELINE_SOURCE="/Users/rudra/Desktop/chat-agent-app/pipelines"
PIPELINE_TARGET="./pipelines"

if [ ! -L "$PIPELINE_TARGET" ] && [ ! -d "$PIPELINE_TARGET" ]; then
    ln -s "$PIPELINE_SOURCE" "$PIPELINE_TARGET"
    echo "   ✅ Pipeline symlink created"
else
    echo "   ⚠️  Pipeline directory already exists, skipping..."
fi

echo ""
echo "🚀 Starting OpenWebUI Backend..."
echo "   Backend API will be available at: http://localhost:8080"
echo "   API Documentation: http://localhost:8080/docs"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start OpenWebUI Backend
cd backend
source venv/bin/activate
export CORS_ALLOW_ORIGIN="http://localhost:5173"
export PORT=8080
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
