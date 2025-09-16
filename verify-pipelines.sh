#!/bin/bash

# Pipeline Verification Script
# This script helps verify that the pipeline setup is correct

set -e

echo "🔍 OpenWebUI Pipeline Verification"
echo "=================================="

# Check if docker-compose.yml has the pipelines service
echo "1. Checking docker-compose.yml configuration..."
if grep -q "pipelines:" docker-compose.yml; then
    echo "✅ Pipelines service found in docker-compose.yml"
else
    echo "❌ Pipelines service missing in docker-compose.yml"
    echo "   Please add the pipelines service to docker-compose.yml"
    exit 1
fi

# Check if pipeline files exist
echo ""
echo "2. Checking pipeline files..."
if [ -f "pipelines/medical_assistant_pipeline.py" ]; then
    echo "✅ Medical Assistant pipeline file exists"
else
    echo "❌ Medical Assistant pipeline file missing"
fi

if [ -f "pipelines/pdf_summarizer_pipeline.py" ]; then
    echo "✅ PDF Summarizer pipeline file exists"
else
    echo "❌ PDF Summarizer pipeline file missing"
fi

# Check pipeline file format
echo ""
echo "3. Checking pipeline file format..."

# Check Medical Assistant pipeline
if grep -q "def pipe(self, body: dict)" pipelines/medical_assistant_pipeline.py; then
    echo "✅ Medical Assistant pipeline has correct format"
else
    echo "❌ Medical Assistant pipeline format needs updating"
fi

# Check PDF Summarizer pipeline
if grep -q "def pipe(self, body: dict)" pipelines/pdf_summarizer_pipeline.py; then
    echo "✅ PDF Summarizer pipeline has correct format"
else
    echo "❌ PDF Summarizer pipeline format needs updating"
fi

# Check if services are running (if docker is available)
echo ""
echo "4. Checking running services..."

if command -v docker &> /dev/null; then
    if docker compose ps &> /dev/null; then
        echo "Services status:"
        docker compose ps | grep -E "(pipelines|open-webui|backend)" || echo "No services running"
        
        echo ""
        echo "5. Testing service endpoints..."
        
        # Test pipelines service
        if curl -f http://localhost:9099/health &> /dev/null; then
            echo "✅ Pipelines service responding on port 9099"
        else
            echo "❌ Pipelines service not responding on port 9099"
        fi
        
        # Test OpenWebUI
        if curl -f http://localhost:3001/health &> /dev/null; then
            echo "✅ OpenWebUI responding on port 3001"
        else
            echo "❌ OpenWebUI not responding on port 3001"
        fi
        
        # Test backend
        if curl -f http://localhost:8000/health &> /dev/null; then
            echo "✅ Backend responding on port 8000"
        else
            echo "❌ Backend not responding on port 8000"
        fi
        
        echo ""
        echo "6. Checking pipeline registration..."
        
        # Try to list pipelines from the pipelines service
        if curl -s http://localhost:9099/pipelines 2>/dev/null | grep -q "medical"; then
            echo "✅ Pipelines are registered with the pipelines service"
        else
            echo "❌ Pipelines not registered with the pipelines service"
            echo "   Check pipelines service logs: docker compose logs pipelines"
        fi
        
    else
        echo "⚠️  Docker Compose not available or services not running"
        echo "   Start services with: docker compose up -d"
    fi
else
    echo "⚠️  Docker not available in this environment"
fi

echo ""
echo "7. Configuration Summary:"
echo "   - Pipelines service should run on port 9099"
echo "   - OpenWebUI should run on port 3001"
echo "   - Backend should run on port 8000"
echo "   - Pipeline files should be mounted to pipelines container"

echo ""
echo "📋 Next Steps:"
echo "1. If services aren't running: docker compose up -d"
echo "2. Wait 30 seconds for services to initialize"
echo "3. Open browser to http://localhost:3001"
echo "4. Go to Settings → Functions to see pipelines"
echo "5. Check logs if issues persist: docker compose logs pipelines"

echo ""
echo "🎯 Expected Result:"
echo "In OpenWebUI Settings → Functions, you should see:"
echo "   - Medical Assistant (Active)"
echo "   - PDF Summarizer (Active)"