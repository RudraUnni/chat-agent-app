#!/bin/bash

# Start Open WebUI Locally with Pipeline Integration (Backend + Frontend)
echo "🌐 Starting Open WebUI with Medical Assistant Pipelines..."

# Check if Open WebUI is set up
if [ ! -d "openwebui/open-webui" ]; then
    echo "❌ Error: Open WebUI not found. Please run ./setup-local-dev.sh first"
    exit 1
fi

# Copy configuration files
echo "📋 Setting up configuration files..."

# Copy OpenWebUI config
if [ ! -f "openwebui/open-webui/backend/.env" ]; then
    echo "   Creating OpenWebUI configuration..."
    cp openwebui-config.env openwebui/open-webui/backend/.env
    echo "   ✅ OpenWebUI config created"
else
    echo "   ⚠️  OpenWebUI config already exists, skipping..."
fi

# Copy backend config
if [ ! -f "backend/.env" ]; then
    echo "   Creating backend configuration..."
    cp backend-config.env backend/.env
    echo "   ✅ Backend config created"
    echo "   ⚠️  Please edit backend/.env and add your OpenAI API key!"
else
    echo "   ⚠️  Backend config already exists, skipping..."
fi

cd openwebui/open-webui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing OpenWebUI frontend dependencies..."
    npm install
fi

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
echo "🚀 Starting Open WebUI (Backend + Frontend)..."
echo "   Open WebUI will be available at: http://localhost:5173"
echo "   Open WebUI Backend API at: http://localhost:8080"
echo "   Your Medical Assistant Backend at: http://localhost:8000"
echo ""
echo "📋 Available Models:"
echo "   - medical-assistant (PubMed Research)"
echo "   - pubmed-research (Direct PubMed)"
echo ""
echo "🔧 Pipeline Tools:"
echo "   - Medical Assistant: General medical queries"
echo "   - PDF Summarizer: Mention 'PDF', 'summarize', 'document'"
echo ""
echo "⚠️  Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping Open WebUI servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start OpenWebUI Backend
echo "🐍 Starting OpenWebUI Backend..."
cd backend
source venv/bin/activate
export CORS_ALLOW_ORIGIN="http://localhost:5173"
export PORT=8080
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start OpenWebUI Frontend
echo "🌐 Starting OpenWebUI Frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait
