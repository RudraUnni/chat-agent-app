#!/bin/bash

# Start All Services Script
echo "🚀 Starting Complete Medical Assistant Development Environment..."
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start service in background
start_service() {
    local script=$1
    local service_name=$2
    local log_file=$3
    
    echo "🔄 Starting $service_name..."
    nohup ./$script > $log_file 2>&1 &
    local pid=$!
    echo "   PID: $pid (logs: $log_file)"
    sleep 2
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "   Please install Node.js (version 18 or higher) from: https://nodejs.org/"
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Create logs directory
mkdir -p logs

# Step 1: Start Database
echo "1️⃣ Starting PostgreSQL Database..."
docker-compose up -d postgres
sleep 5

if check_port 5432; then
    echo "✅ PostgreSQL is running on port 5432"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
fi

# Step 2: Start Backend
echo ""
echo "2️⃣ Starting Backend API..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Skipping backend startup."
else
    start_service "start-backend.sh" "Backend API" "logs/backend.log"
    sleep 10
    
    if check_port 8000; then
        echo "✅ Backend API is running on port 8000"
    else
        echo "❌ Failed to start Backend API. Check logs/backend.log"
        exit 1
    fi
fi

# Step 3: Setup Open WebUI (if not already done)
echo ""
echo "3️⃣ Checking Open WebUI setup..."
if [ ! -d "openwebui/open-webui" ]; then
    echo "   Setting up Open WebUI for the first time..."
    ./setup-openwebui.sh
fi

# Step 4: Start Open WebUI
echo ""
echo "4️⃣ Starting Open WebUI..."
if check_port 5173; then
    echo "⚠️  Port 5173 is already in use. Skipping Open WebUI startup."
else
    start_service "start-openwebui.sh" "Open WebUI" "logs/openwebui.log"
    sleep 15
    
    if check_port 5173; then
        echo "✅ Open WebUI is running on port 5173"
    else
        echo "❌ Failed to start Open WebUI. Check logs/openwebui.log"
        exit 1
    fi
fi

echo ""
echo "🎉 All services are running!"
echo ""
echo "📊 Service URLs:"
echo "   🌐 Open WebUI:    http://localhost:5173"
echo "   🔧 Backend API:   http://localhost:8000"
echo "   📖 API Docs:      http://localhost:8000/docs"
echo "   🐘 PostgreSQL:    localhost:5432"
echo ""
echo "📝 Logs are available in the 'logs/' directory"
echo ""
echo "⚠️  Important:"
echo "   - Make sure to set your OPENAI_API_KEY in backend/.env"
echo "   - You can also set it in openwebui/open-webui/.env"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down  # Stop PostgreSQL"
echo "   pkill -f uvicorn     # Stop Backend"
echo "   pkill -f vite        # Stop Open WebUI"
echo ""
echo "Press Ctrl+C to exit this script (services will continue running)"

# Keep script running to show status
while true; do
    sleep 30
    echo "📊 Status check - $(date)"
    echo "   PostgreSQL: $(check_port 5432 && echo "✅ Running" || echo "❌ Stopped")"
    echo "   Backend:    $(check_port 8000 && echo "✅ Running" || echo "❌ Stopped")"
    echo "   Open WebUI: $(check_port 5173 && echo "✅ Running" || echo "❌ Stopped")"
    echo ""
done