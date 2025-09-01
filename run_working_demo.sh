#!/bin/bash
set -e

# Medical Assistant Pro - Working Demo Script
# This script starts the complete OpenWebUI + FastAPI integration

echo "🏥 Medical Assistant Pro - Working Demo"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}$1${NC}"
    echo "$(echo "$1" | sed 's/./=/g')"
}

# Check prerequisites
print_header "🔍 Checking Prerequisites"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose v2 is not available. Please install it."
    exit 1
fi
print_success "Docker Compose is available"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3."
    exit 1
fi
print_success "Python 3 is available"

# Create .env file if it doesn't exist
print_header "⚙️ Setting up Configuration"

if [ ! -f .env ]; then
    print_status "Creating .env file with default configuration..."
    cat > .env << 'EOF'
# OpenWebUI Configuration
WEBUI_SECRET_KEY=medical-assistant-pro-demo-2024
OPENAI_API_KEY=your-openai-api-key-here

# Medical Assistant Configuration
MEDICAL_ASSISTANT_ENABLED=true
MEDICAL_WORKFLOW_URL=http://backend:8000
MEDICAL_API_ENDPOINT=http://backend:8000/api/v1/chat

# Database
DATABASE_URL=postgresql://chatapp:chatapp_password@postgres:5432/chatapp_db
EOF
    print_warning "⚠️  .env file created with default values."
    print_warning "⚠️  IMPORTANT: Update OPENAI_API_KEY with your actual API key before running the demo."
    echo ""
    print_status "Please edit .env file and set your OpenAI API key, then run this script again."
    exit 1
else
    # Check if API key is set
    if grep -q "your-openai-api-key-here" .env; then
        print_error "❌ OPENAI_API_KEY is not set in .env file"
        print_status "Please edit .env file and set your OpenAI API key, then run this script again."
        exit 1
    fi
    print_success ".env file exists and API key is configured"
fi

# Stop any existing services
print_header "🛑 Stopping Existing Services"
print_status "Stopping any running containers..."
docker compose down --remove-orphans 2>/dev/null || true

# Kill processes on ports we need
for port in 8000 8080; do
    if lsof -i :$port > /dev/null 2>&1; then
        print_warning "Port $port is in use. Stopping existing processes..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
done

# Start database first
print_header "🐘 Starting Database"
print_status "Starting PostgreSQL database..."
docker compose up -d postgres

# Wait for database to be ready
print_status "Waiting for database to be ready..."
timeout=30
counter=0
while ! docker compose exec postgres pg_isready -U chatapp -d chatapp_db > /dev/null 2>&1; do
    sleep 1
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        print_error "Database failed to start within $timeout seconds"
        exit 1
    fi
done
print_success "Database is ready"

# Build and start backend
print_header "🔧 Starting Medical Backend"
print_status "Building and starting FastAPI backend..."
docker compose up -d backend

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
timeout=60
counter=0
while ! curl -s http://localhost:8000/health > /dev/null 2>&1; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -gt $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        print_status "Checking backend logs..."
        docker compose logs backend
        exit 1
    fi
done
print_success "Medical backend is running and healthy"

# Start OpenWebUI
print_header "🎨 Starting OpenWebUI"
print_status "Starting OpenWebUI interface..."
docker compose up -d open-webui

# Wait for OpenWebUI to be ready
print_status "Waiting for OpenWebUI to be ready..."
timeout=60
counter=0
while ! curl -s http://localhost:8080 > /dev/null 2>&1; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -gt $timeout ]; then
        print_error "OpenWebUI failed to start within $timeout seconds"
        print_status "Checking OpenWebUI logs..."
        docker compose logs open-webui
        exit 1
    fi
done
print_success "OpenWebUI is running and accessible"

# Start nginx proxy
print_header "🌐 Starting Nginx Proxy"
print_status "Starting nginx reverse proxy..."
docker compose up -d nginx
print_success "Nginx proxy is running"

# Final status check
print_header "✅ Integration Status Check"

services=("postgres" "backend" "open-webui" "nginx")
all_healthy=true

for service in "${services[@]}"; do
    if docker compose ps $service --format "table {{.Status}}" | grep -q "Up"; then
        print_success "$service: Running"
    else
        print_error "$service: Not running"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    print_header "🎉 Demo is Ready!"
    echo ""
    echo "🏥 Medical Assistant Pro is now running successfully!"
    echo ""
    echo "📱 Access Points:"
    echo "  • OpenWebUI Interface: http://localhost:8080"
    echo "  • Medical Backend API: http://localhost:8000"
    echo "  • Backend Health Check: http://localhost:8000/health"
    echo "  • Unified Gateway: http://localhost (via nginx)"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View all logs: docker compose logs -f"
    echo "  • View backend logs: docker compose logs -f backend"
    echo "  • View OpenWebUI logs: docker compose logs -f open-webui"
    echo "  • Stop all services: docker compose down"
    echo "  • Restart demo: ./run_working_demo.sh"
    echo ""
    echo "💡 Getting Started:"
    echo "  1. Open http://localhost:8080 in your browser"
    echo "  2. Create an account or sign in"
    echo "  3. Start a new chat"
    echo "  4. Ask medical questions like:"
    echo "     - 'What are the latest treatments for diabetes?'"
    echo "     - 'Find research papers about COVID-19 vaccines'"
    echo "     - 'Summarize recent studies on heart disease'"
    echo ""
    echo "🎯 Demo Scenarios:"
    echo "  • Medical Research: Ask about specific conditions"
    echo "  • Paper Lookup: Request papers by PMID"
    echo "  • Treatment Info: Ask about treatment options"
    echo "  • Drug Information: Query about medications"
    echo ""
    print_success "All systems operational! 🚀"
else
    print_error "Some services failed to start. Check the logs above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  • Check logs: docker compose logs"
    echo "  • Restart services: docker compose restart"
    echo "  • Full reset: docker compose down && ./run_working_demo.sh"
    exit 1
fi