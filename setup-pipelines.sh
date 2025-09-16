#!/bin/bash

# Pipeline Setup Script
# This script copies pipeline files to the running pipelines container

set -e

echo "🔧 Setting up OpenWebUI Pipelines"
echo "=================================="

# Check if pipelines container is running
if ! docker ps | grep -q "chatapp_pipelines"; then
    echo "❌ Pipelines container is not running"
    echo "   Please start it first: docker compose up -d pipelines"
    exit 1
fi

echo "📁 Copying pipeline files to container..."

# Copy pipeline files to the container
docker cp pipelines/medical_assistant_pipeline.py chatapp_pipelines:/app/pipelines/
docker cp pipelines/pdf_summarizer_pipeline.py chatapp_pipelines:/app/pipelines/
docker cp pipelines/requirements.txt chatapp_pipelines:/app/pipelines/

echo "✅ Pipeline files copied successfully"

echo "🔄 Restarting pipelines container to load new files..."
docker compose restart pipelines

echo "⏳ Waiting for pipelines service to start..."
sleep 10

# Check if pipelines service is responding
echo "🔍 Testing pipelines service..."
if curl -f http://localhost:9099/health &> /dev/null; then
    echo "✅ Pipelines service is running and healthy"
    
    # List available pipelines
    echo ""
    echo "📋 Available pipelines:"
    curl -s http://localhost:9099/pipelines 2>/dev/null || echo "Could not retrieve pipeline list"
else
    echo "❌ Pipelines service is not responding"
    echo "   Check logs: docker compose logs pipelines"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Open OpenWebUI at http://localhost:3001"
echo "2. Go to Settings → Functions"
echo "3. You should see your pipelines listed"
echo ""
echo "If pipelines still don't appear, check the logs:"
echo "   docker compose logs pipelines"