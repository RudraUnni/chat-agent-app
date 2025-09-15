#!/bin/bash

# Start Open WebUI Locally Script
echo "🌐 Starting Open WebUI Locally..."

# Check if Open WebUI is set up
if [ ! -d "openwebui/open-webui" ]; then
    echo "❌ Error: Open WebUI not found. Please run ./setup-openwebui.sh first"
    exit 1
fi

cd openwebui/open-webui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔄 Starting Open WebUI development server..."
echo "   Open WebUI will be available at: http://localhost:5173"
echo ""
echo "   Make sure your backend is running at: http://localhost:8000"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev