#!/bin/bash

echo "🧪 Step 1: Testing Basic Open WebUI Setup"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting PostgreSQL and Open WebUI..."
docker-compose up -d postgres open-webui

echo "⏳ Waiting for services to start..."
sleep 15

echo "📊 Checking service status:"
docker-compose ps

echo ""
echo "🔍 Testing connections:"

# Test PostgreSQL
echo "📅 PostgreSQL:"
if docker exec chatapp_postgres pg_isready -U chatapp -d chatapp_db > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is ready"
else
    echo "   ❌ PostgreSQL is not ready"
fi

# Test Open WebUI
echo "🤖 Open WebUI:"
sleep 5  # Give Open WebUI a bit more time
if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Open WebUI is accessible at http://localhost:3000"
else
    echo "   ❌ Open WebUI is not accessible"
    echo "   🔍 Checking logs..."
    docker logs medical_open_webui --tail 10
fi

echo ""
echo "📋 Step 1 Results:"
echo "=================="
echo "🌐 Open WebUI: http://localhost:3000"
echo "📊 PostgreSQL: localhost:5432"
echo ""
echo "📝 Next Steps:"
echo "1. Visit http://localhost:3000 and create a test account"
echo "2. Verify Open WebUI loads correctly"
echo "3. If everything works, we'll move to Step 2"
echo ""
echo "🛑 To stop services: docker-compose down"