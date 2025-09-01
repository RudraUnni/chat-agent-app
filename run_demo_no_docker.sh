#!/bin/bash
set -e

# Medical Assistant Pro - No Docker Demo Script
echo "🏥 Medical Assistant Pro - No Docker Demo"
echo "========================================"

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

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3."
    exit 1
fi
print_success "Python 3 is available: $(python3 --version)"

# Check if backend exists
if [ ! -d "backend" ]; then
    print_error "Backend directory not found. Please ensure you're in the project root."
    exit 1
fi
print_success "Backend directory found"

# Check if backend is already running
print_header "🔍 Checking Backend Status"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is already running at http://localhost:8000"
    BACKEND_RUNNING=true
else
    print_status "Backend is not running. Will start it now."
    BACKEND_RUNNING=false
fi

# Start backend if needed
if [ "$BACKEND_RUNNING" = false ]; then
    print_header "🚀 Starting Backend"
    print_status "Starting FastAPI backend in background..."
    
    # Kill any existing process on port 8000
    if lsof -i :8000 > /dev/null 2>&1; then
        print_warning "Port 8000 is in use. Stopping existing process..."
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start backend using the standalone runner
    print_status "Launching backend with standalone runner..."
    python3 run_backend_standalone.py &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    timeout=30
    counter=0
    while ! curl -s http://localhost:8000/health > /dev/null 2>&1; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -gt $timeout ]; then
            print_error "Backend failed to start within $timeout seconds"
            if kill -0 $BACKEND_PID 2>/dev/null; then
                print_status "Backend process is still running. Checking logs..."
                sleep 5
                if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                    print_success "Backend started successfully (took longer than expected)"
                    break
                else
                    print_error "Backend process running but not responding"
                    kill $BACKEND_PID 2>/dev/null || true
                    exit 1
                fi
            else
                print_error "Backend process died. Check for errors above."
                exit 1
            fi
        fi
        echo -n "."
    done
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend started successfully!"
    fi
fi

# Test the integration
print_header "🧪 Testing Integration"
print_status "Running integration tests..."
python3 test_standalone_integration.py

# Show access information
print_header "🎉 Demo Ready!"
echo ""
print_success "Medical Assistant Pro Backend is running!"
echo ""
echo "📱 Access Points:"
echo "  • Backend API: http://localhost:8000"
echo "  • Health Check: http://localhost:8000/health"
echo "  • API Documentation: http://localhost:8000/docs"
echo ""
echo "🧪 Test the Medical Assistant:"
echo "  • Run tests: python3 test_standalone_integration.py"
echo "  • Manual test: curl http://localhost:8000/health"
echo ""
echo "💬 Example API Usage:"
echo "  curl -X POST http://localhost:8000/api/v1/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"What are treatments for diabetes?\", \"workflow\": \"pubmed_research\"}'"
echo ""
echo "🔧 Management:"
echo "  • View logs: Check terminal output"
echo "  • Stop backend: Ctrl+C or kill the process"
echo "  • Restart: ./run_demo_no_docker.sh"

if [ "$BACKEND_RUNNING" = false ]; then
    echo ""
    print_warning "Backend is running in background (PID: $BACKEND_PID)"
    echo "Press Ctrl+C to stop the demo and backend"
    
    # Wait for user interrupt
    trap 'print_status "Stopping backend..."; kill $BACKEND_PID 2>/dev/null || true; print_success "Demo stopped"; exit 0' INT
    
    # Keep script running
    while kill -0 $BACKEND_PID 2>/dev/null; do
        sleep 5
    done
    
    print_error "Backend process stopped unexpectedly"
else
    echo ""
    print_status "Backend was already running. Demo is ready to use!"
fi