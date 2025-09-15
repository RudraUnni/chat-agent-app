#!/bin/bash

# Complete Local Development Setup for Medical Assistant + OpenWebUI
echo "🏥 Setting up Medical Assistant with OpenWebUI for Local Development"
echo "=================================================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Step 1: Setup OpenWebUI
echo ""
echo "📦 Step 1: Setting up OpenWebUI..."

if [ ! -d "openwebui/open-webui" ]; then
    echo "   Cloning OpenWebUI repository..."
    mkdir -p openwebui
    cd openwebui
    git clone https://github.com/open-webui/open-webui.git
    cd ..
    echo "   ✅ OpenWebUI cloned"
else
    echo "   ⚠️  OpenWebUI already exists, skipping clone..."
fi

# Step 2: Setup Backend Environment
echo ""
echo "🐍 Step 2: Setting up Backend Environment..."

if [ ! -d "backend/venv" ]; then
    echo "   Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo "   ✅ Backend environment created"
else
    echo "   ⚠️  Backend virtual environment already exists, skipping..."
fi

# Step 3: Setup Configuration Files
echo ""
echo "⚙️  Step 3: Setting up Configuration Files..."

# Copy backend config
if [ ! -f "backend/.env" ]; then
    echo "   Creating backend configuration..."
    cp backend-config.env backend/.env
    echo "   ✅ Backend config created"
    echo "   ⚠️  IMPORTANT: Please edit backend/.env and add your OpenAI API key!"
else
    echo "   ⚠️  Backend config already exists, skipping..."
fi

# Copy OpenWebUI config
if [ ! -f "openwebui/open-webui/backend/.env" ]; then
    echo "   Creating OpenWebUI configuration..."
    cp openwebui-config.env openwebui/open-webui/backend/.env
    echo "   ✅ OpenWebUI config created"
else
    echo "   ⚠️  OpenWebUI config already exists, skipping..."
fi

# Step 4: Setup Pipeline Integration
echo ""
echo "🔗 Step 4: Setting up Pipeline Integration..."

cd openwebui/open-webui

# Create pipeline symlink
PIPELINE_SOURCE="/Users/rudra/Desktop/chat-agent-app/pipelines"
PIPELINE_TARGET="./pipelines"

if [ ! -L "$PIPELINE_TARGET" ] && [ ! -d "$PIPELINE_TARGET" ]; then
    ln -s "$PIPELINE_SOURCE" "$PIPELINE_TARGET"
    echo "   ✅ Pipeline symlink created"
else
    echo "   ⚠️  Pipeline directory already exists, skipping..."
fi

# Install OpenWebUI dependencies
if [ ! -d "node_modules" ]; then
    echo "   Installing OpenWebUI dependencies..."
    npm install
    echo "   ✅ OpenWebUI dependencies installed"
else
    echo "   ⚠️  OpenWebUI dependencies already installed, skipping..."
fi

cd ../..

# Step 5: Start Database
echo ""
echo "🐘 Step 5: Starting PostgreSQL Database..."

# Start database
docker-compose up -d postgres

# Wait for database to be ready
echo "   Waiting for database to be ready..."
sleep 5

# Check if database is ready
if docker-compose exec postgres pg_isready -U chatapp -d chatapp_db > /dev/null 2>&1; then
    echo "   ✅ Database is ready"
else
    echo "   ⚠️  Database might not be ready yet, but continuing..."
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start the backend: ./start-backend.sh"
echo "3. Start OpenWebUI: ./start-openwebui-local.sh"
echo ""
echo "🌐 Access Points:"
echo "   - OpenWebUI: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Database: localhost:5432"
echo ""
echo "🔧 Available Models:"
echo "   - medical-assistant (PubMed Research)"
echo "   - pubmed-research (Direct PubMed)"
echo ""
echo "🛠️  Pipeline Tools:"
echo "   - Medical Assistant: General medical queries"
echo "   - PDF Summarizer: Mention 'PDF', 'summarize', 'document'"
echo ""
echo "Happy coding! 🚀"
