#!/bin/bash

# Medical Assistant + Open WebUI Startup Script
echo "🏥 Starting Medical Assistant with Open WebUI..."

# Load environment variables
set -a
source .env.docker
set +a

# Create necessary directories if they don't exist
mkdir -p open_webui_config nginx/conf.d

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start the services
echo "🐳 Starting Docker services..."

if [ "$1" = "dev" ]; then
    echo "📝 Starting in DEVELOPMENT mode (with pgAdmin)..."
    docker-compose --profile dev up -d
elif [ "$1" = "prod" ]; then
    echo "🚀 Starting in PRODUCTION mode (with Nginx)..."
    docker-compose --profile production up -d
else
    echo "⚡ Starting BASIC services (Postgres + Open WebUI)..."
    docker-compose up -d postgres open-webui
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Medical Assistant + Open WebUI is starting up!"
echo ""
echo "📍 Service URLs:"
echo "   🏥 Medical Assistant Frontend: http://localhost:5173 (run 'npm run dev' in frontend/)"
echo "   🔬 Medical Assistant API: http://localhost:8000 (run backend separately)"
echo "   🤖 Open WebUI: http://localhost:3000"
echo "   📊 pgAdmin (dev mode): http://localhost:5050"
echo "   🌐 Nginx (prod mode): http://localhost"
echo ""
echo "📚 Quick Start:"
echo "   1. Start your FastAPI backend: cd backend && python -m app.main"
echo "   2. Start your React frontend: cd frontend && npm run dev"
echo "   3. Access Open WebUI at http://localhost:3000"
echo ""
echo "🔧 To stop: docker-compose down"