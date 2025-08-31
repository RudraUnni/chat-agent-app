#!/bin/bash
set -e

# Open WebUI v0.6.5 Integration Startup Script
# This script starts the Open WebUI integration with your Medical Chat Agent

echo "🚀 Starting Open WebUI v0.6.5 Integration..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Check if Docker Compose is available
print_status "Checking Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose (v2) is not available. Please install it first."
    exit 1
fi
print_success "Docker Compose is available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Open WebUI v0.6.5 Integration Environment Variables
OPENAI_API_KEY=your-api-key-here
WEBUI_SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://chatapp:chatapp_password@postgres:5432/chatapp_db

# Open WebUI Settings
ENABLE_RAG=true
ENABLE_VOICE=true
ENABLE_IMAGE_GENERATION=true
ENABLE_WEB_SEARCH=true
ENABLE_FUNCTION_CALLING=true
WEBUI_NAME=Medical Chat Agent
WEBUI_DESCRIPTION=AI-powered medical consultation platform
EOF
    print_warning "⚠️  .env file created with default values."
    print_warning "Please update .env file with your actual API keys before continuing."
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
fi

# Stop any existing services
print_status "Stopping existing services..."
docker compose down --remove-orphans

# Start all services
print_status "Starting Open WebUI integration services..."
docker compose up -d

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
until docker compose exec -T postgres pg_isready -U chatapp -d chatapp_db > /dev/null 2>&1; do
    sleep 2
done
print_success "PostgreSQL is ready"

# Wait for services to start
print_status "Waiting for services to start..."
sleep 20

# Check service health
print_status "Checking service health..."

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local description=$3
    
    if curl -s "$url" > /dev/null; then
        print_success "$service_name: $description"
        return 0
    else
        print_error "$service_name: $description"
        return 1
    fi
}

# Check each service
services_healthy=true

if check_service "PostgreSQL" "http://localhost:5432" "Database accessible"; then
    print_success "PostgreSQL: Running on port 5432"
else
    print_error "PostgreSQL: Not accessible"
    services_healthy=false
fi

if check_service "FastAPI Backend" "http://localhost:8000/health" "Health check passed"; then
    print_success "FastAPI Backend: Running on port 8000"
else
    print_error "FastAPI Backend: Not accessible"
    services_healthy=false
fi

if check_service "Open WebUI" "http://localhost:8080" "Main interface accessible"; then
    print_success "Open WebUI: Running on port 8080"
else
    print_error "Open WebUI: Not accessible"
    services_healthy=false
fi

if check_service "Frontend" "http://localhost:3000" "React app accessible"; then
    print_success "Frontend: Running on port 3000"
else
    print_error "Frontend: Not accessible"
    services_healthy=false
fi

if check_service "Nginx Proxy" "http://localhost:80" "Reverse proxy accessible"; then
    print_success "Nginx Proxy: Running on port 80"
else
    print_error "Nginx Proxy: Not accessible"
    services_healthy=false
fi

echo ""
echo "=============================================="

if [ "$services_healthy" = true ]; then
    print_success "🎉 All services are running successfully!"
    echo ""
    echo "📋 Access Points:"
    echo "  • Open WebUI (AI Interface): http://localhost:8080"
    echo "  • Your Backend (Medical Workflows): http://localhost:8000"
    echo "  • Frontend (React App): http://localhost:3000"
    echo "  • Unified Gateway: http://localhost:9000"
    echo "  • pgAdmin (Database): http://localhost:5050"
    echo ""
    echo "🧪 Run integration tests:"
    echo "  python3 scripts/test_integration.py"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs: docker compose logs -f"
    echo "  • Stop services: docker compose down"
    echo "  • Restart services: docker compose restart"
    echo "  • Check status: docker compose ps"
    echo ""
    print_success "Your Open WebUI v0.6.5 integration is ready! 🚀"
else
    print_error "⚠️  Some services failed to start properly."
    echo ""
    echo "🔍 Troubleshooting:"
    echo "  • Check logs: docker compose logs -f"
    echo "  • Restart services: docker compose restart"
    echo "  • Check port conflicts: lsof -i :8080, lsof -i :8000"
    echo "  • Verify Docker resources (RAM, CPU)"
    echo ""
    print_warning "Please check the logs above and resolve any issues."
fi

echo ""
echo "📚 For more information, see:"
echo "  • INTEGRATION_README.md"
echo "  • OPENWEBUI_INTEGRATION_GUIDE.md"
echo "  • scripts/test_integration.py"
