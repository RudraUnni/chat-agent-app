#!/bin/bash

# Open WebUI Integration Quick Start Script
# This script helps you start the integrated medical assistant chat application

set -e

echo "🏥 Medical Assistant with Open WebUI - Quick Start"
echo "=================================================="

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📋 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration (especially OPENAI_API_KEY)"
    else
        echo "⚠️  No .env file found. Please create one with your configuration."
    fi
fi

# Check if backend .env exists
if [ ! -f backend/.env ]; then
    if [ -f backend/.env.example ]; then
        echo "📋 Creating backend/.env file from backend/.env.example..."
        cp backend/.env.example backend/.env
        echo "⚠️  Please edit backend/.env file with your database and API configuration"
    fi
fi

echo ""
echo "🚀 Starting services..."
echo "----------------------"

# Start the services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "------------------"
docker-compose ps

# Check if services are healthy
echo ""
echo "🔍 Health Checks:"
echo "------------------"

# Check backend health
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend (FastAPI) - Healthy"
else
    echo "❌ Backend (FastAPI) - Not responding"
fi

# Check Open WebUI health
if curl -f http://localhost:3001/health &> /dev/null; then
    echo "✅ Open WebUI - Healthy"
else
    echo "❌ Open WebUI - Not responding"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U chatapp -d chatapp_db &> /dev/null; then
    echo "✅ PostgreSQL - Healthy"
else
    echo "❌ PostgreSQL - Not responding"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🌐 Access your applications:"
echo "   • Open WebUI (Enhanced Chat): http://localhost:3001"
echo "   • FastAPI Backend: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Optional services:"
echo "   • pgAdmin (Database): http://localhost:5050 (run with --profile dev)"
echo ""
echo "📚 Documentation:"
echo "   • Integration Guide: ./OPENWEBUI_INTEGRATION_GUIDE.md"
echo "   • Setup Guide: ./SETUP_GUIDE.md"
echo ""
echo "🛠️  Quick Commands:"
echo "   • View logs: docker-compose logs"
echo "   • Stop services: docker-compose down"
echo "   • Restart: docker-compose restart"
echo ""
echo "💡 First Steps:"
echo "   1. Open http://localhost:3001 in your browser"
echo "   2. Create an account (or skip if auth is disabled)"
echo "   3. Try asking: 'What are the latest treatments for diabetes?'"
echo "   4. Test PDF tool: 'Can you summarize this medical PDF?'"
echo ""

# Check if there are any failed services
FAILED_SERVICES=$(docker-compose ps --services --filter "status=exited")
if [ ! -z "$FAILED_SERVICES" ]; then
    echo "⚠️  Some services failed to start:"
    echo "$FAILED_SERVICES"
    echo ""
    echo "Check logs with: docker-compose logs [service-name]"
fi

echo "Happy chatting! 🚀"