#!/bin/bash

# Backend Diagnostic Script
echo "🔍 Medical Assistant Pro - Backend Diagnostics"
echo "=============================================="

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

# Check Docker services
print_header "🐳 Docker Services Status"
if command -v docker &> /dev/null; then
    if docker info > /dev/null 2>&1; then
        print_success "Docker is running"
        echo ""
        echo "Container Status:"
        docker compose ps
        echo ""
        echo "Container Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    else
        print_error "Docker is not running"
    fi
else
    print_error "Docker is not installed"
fi

# Check port availability
print_header "🔌 Port Status"
ports=(5432 8000 8080)
for port in "${ports[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        process=$(lsof -i :$port | tail -n 1 | awk '{print $1, $2}')
        print_success "Port $port: In use by $process"
    else
        print_warning "Port $port: Available (nothing running)"
    fi
done

# Check backend container specifically
print_header "🔧 Backend Container Details"
if docker compose ps backend | grep -q "Up"; then
    print_success "Backend container is running"
    
    echo ""
    echo "Backend Container Logs (last 20 lines):"
    echo "----------------------------------------"
    docker compose logs --tail=20 backend
    
    echo ""
    echo "Backend Container Health:"
    echo "------------------------"
    docker compose exec backend ps aux || print_error "Cannot execute commands in backend container"
    
else
    print_error "Backend container is not running"
    echo ""
    echo "All containers status:"
    docker compose ps
fi

# Test internal network connectivity
print_header "🌐 Network Connectivity"
if docker compose ps backend | grep -q "Up"; then
    print_status "Testing internal container connectivity..."
    
    # Test if backend can reach itself internally
    if docker compose exec backend curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend internal health check: OK"
    else
        print_error "Backend internal health check: FAILED"
    fi
    
    # Test database connectivity from backend
    if docker compose exec backend curl -s http://postgres:5432 > /dev/null 2>&1; then
        print_success "Backend to database connectivity: OK"
    else
        print_warning "Backend to database connectivity: Cannot test (expected for non-HTTP)"
    fi
else
    print_warning "Cannot test network connectivity - backend not running"
fi

# Test external connectivity
print_header "🔗 External Connectivity"
external_tests=(
    "http://localhost:8000/health:Backend Health"
    "http://localhost:8080:OpenWebUI"
    "http://localhost:5432:PostgreSQL"
)

for test in "${external_tests[@]}"; do
    url=$(echo $test | cut -d: -f1)
    name=$(echo $test | cut -d: -f2)
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        print_success "$name: Accessible"
    else
        print_error "$name: Not accessible"
    fi
done

# Check backend dependencies
print_header "🐍 Backend Dependencies"
if docker compose ps backend | grep -q "Up"; then
    print_status "Checking Python environment in backend..."
    docker compose exec backend python --version
    
    print_status "Checking if FastAPI is installed..."
    docker compose exec backend python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')" 2>/dev/null || print_error "FastAPI not found"
    
    print_status "Checking if uvicorn is running..."
    docker compose exec backend ps aux | grep uvicorn || print_error "Uvicorn process not found"
else
    print_warning "Cannot check dependencies - backend not running"
fi

# Recommendations
print_header "💡 Recommendations"
if ! docker compose ps backend | grep -q "Up"; then
    echo "1. Start the backend service:"
    echo "   docker compose up -d backend"
    echo ""
elif ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "1. Backend container is running but not responding. Try:"
    echo "   docker compose restart backend"
    echo ""
    echo "2. Check backend logs for errors:"
    echo "   docker compose logs backend"
    echo ""
    echo "3. Rebuild backend if needed:"
    echo "   docker compose build backend"
    echo "   docker compose up -d backend"
    echo ""
else
    print_success "Backend appears to be working correctly!"
fi

echo "4. Run the working demo script:"
echo "   ./run_working_demo.sh"
echo ""
echo "5. If issues persist, try a clean restart:"
echo "   docker compose down"
echo "   docker compose up -d"