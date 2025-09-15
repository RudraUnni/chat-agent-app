#!/bin/bash

# Start OpenWebUI Frontend Only
echo "🌐 Starting OpenWebUI Frontend..."

# Check if Open WebUI is set up
if [ ! -d "openwebui/open-webui" ]; then
    echo "❌ Error: Open WebUI not found. Please run ./setup-local-dev.sh first"
    exit 1
fi

cd openwebui/open-webui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing OpenWebUI frontend dependencies..."
    npm install
fi

echo ""
echo "🚀 Starting OpenWebUI Frontend..."
echo "   Frontend will be available at: http://localhost:5173"
echo "   Make sure OpenWebUI backend is running at: http://localhost:8080"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start OpenWebUI Frontend
npm run dev
