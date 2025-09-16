# OpenWebUI Pipeline Troubleshooting Guide

## Issue: Pipelines Not Displaying in OpenWebUI Interface

### Root Causes Identified:

1. **Missing Pipelines Container** - OpenWebUI v0.6.5 requires a separate pipelines service
2. **Incorrect Pipeline Mount Path** - Wrong directory mapping in docker-compose.yml
3. **Pipeline Format Issues** - Incompatible with OpenWebUI v0.6.5
4. **Configuration Conflicts** - Multiple conflicting endpoint configurations

### ✅ Fixes Applied:

#### 1. Added Missing Pipelines Container
**Added to docker-compose.yml:**
```yaml
pipelines:
  image: ghcr.io/open-webui/pipelines:main
  container_name: chatapp_pipelines
  environment:
    - PIPELINES_API_KEY=medical-assistant-pipelines-key
  volumes:
    - ./pipelines:/app/pipelines:ro
  ports:
    - "9099:9099"
```

#### 2. Updated OpenWebUI Configuration
**Added pipelines connection:**
```yaml
- PIPELINES_API_BASE_URL=http://pipelines:9099
- PIPELINES_API_KEY=medical-assistant-pipelines-key
- OPENAI_API_BASE_URL=http://backend:8000/v1
```

#### 3. Fixed Pipeline Format
Updated pipeline files to match OpenWebUI pipelines service format:
- Simplified `pipe(body: dict)` function signature
- Added proper Field descriptions for Valves
- Removed obsolete async methods and complex message handling

#### 4. Removed Obsolete Configuration
- Deleted `pipelines.json` (not used in OpenWebUI v0.6.5)
- Removed conflicting BACKEND_URL environment variable
- Removed direct pipeline mounting to OpenWebUI container

---

## 🚀 Step-by-Step Solution:

### Step 1: Install Docker (if needed)
```bash
# Run the installation script
./install-docker.sh

# After installation, restart your shell or run:
newgrp docker

# Test Docker installation
docker run hello-world
```

### Step 2: Start Services
```bash
# Start all services
./start-openwebui.sh

# Or manually:
docker compose up -d
```

### Step 3: Verify Services
```bash
# Check service status
docker compose ps

# Check logs if needed
docker compose logs open-webui
docker compose logs pipelines
docker compose logs backend
```

### Step 4: Access OpenWebUI
1. Open browser to: http://localhost:3001
2. Create account or skip login (WEBUI_AUTH=false)
3. Check if models appear in the interface
4. Look for the pipelines in the functions/tools section

---

## 🔍 Verification Checklist:

### Backend Health Check:
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

curl http://localhost:8000/models
# Should return list of models: medical-assistant, pubmed-research
```

### OpenWebUI Health Check:
```bash
curl http://localhost:3001/health
# Should return OpenWebUI health status
```

### Pipeline Verification:
1. **In OpenWebUI Interface:**
   - Go to Settings → Functions
   - Should see "Medical Assistant Pipeline" and "PDF Summarizer Tool"
   - Both should show as "Active" or "Available"

2. **Test Pipeline Functionality:**
   - Send message: "What are the latest treatments for diabetes?"
   - Should route through Medical Assistant Pipeline
   - Send message: "Can you summarize this PDF about cardiology?"
   - Should activate PDF Summarizer Tool

---

## 🛠️ Common Issues & Solutions:

### Issue 1: "No models available"
**Cause:** Backend not accessible from OpenWebUI
**Solution:**
```bash
# Check if backend is running
docker compose logs backend

# Verify network connectivity
docker compose exec open-webui ping backend

# Check CORS settings in backend/app/main.py
```

### Issue 2: "Functions not loading"
**Cause:** Pipeline files not mounted correctly
**Solution:**
```bash
# Verify mount path
docker compose exec open-webui ls -la /app/backend/data/functions/

# Should show:
# medical_assistant_pipeline.py
# pdf_summarizer_pipeline.py
# requirements.txt
```

### Issue 3: "Pipeline errors in logs"
**Cause:** Missing dependencies or connection issues
**Solution:**
```bash
# Check pipeline logs
docker compose logs open-webui | grep -i pipeline

# Install missing dependencies
docker compose exec open-webui pip install -r /app/backend/data/functions/requirements.txt
```

### Issue 4: "Authentication errors"
**Cause:** API key or endpoint configuration
**Solution:**
Check docker-compose.yml settings:
- OPENAI_API_BASE_URL should point to backend
- OPENAI_API_KEY can be dummy value
- Ensure backend accepts requests without auth

---

## 📊 Expected Behavior:

### When Working Correctly:
1. **OpenWebUI Interface:**
   - Shows "Medical Assistant Chat" as title
   - Displays 2 models: medical-assistant, pubmed-research
   - Functions section shows 2 active pipelines

2. **Chat Functionality:**
   - Medical queries route to backend workflow
   - PDF-related queries activate summarizer tool
   - Conversation history is preserved
   - Responses include medical research data

3. **Logs Show:**
   ```
   open-webui | INFO: Loading function: medical_assistant_pipeline
   open-webui | INFO: Loading function: pdf_summarizer_pipeline
   backend    | INFO: Received chat request for workflow: pubmed_research
   ```

---

## 🔄 Restart Sequence:

If issues persist, try this restart sequence:

```bash
# Stop all services
docker compose down

# Remove containers and volumes (⚠️ will lose data)
docker compose down -v

# Rebuild and start
docker compose up -d --build

# Wait for services to initialize
sleep 30

# Check status
docker compose ps
```

---

## 📞 Getting Help:

### Useful Log Commands:
```bash
# All service logs
docker compose logs

# Specific service logs
docker compose logs open-webui
docker compose logs backend

# Follow logs in real-time
docker compose logs -f open-webui

# Last 50 lines
docker compose logs --tail=50 open-webui
```

### Configuration Files to Check:
- `/workspace/docker-compose.yml` - Service configuration
- `/workspace/pipelines/` - Pipeline files
- `/workspace/backend/app/main.py` - CORS and API endpoints

### Port Mappings:
- OpenWebUI: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (internal use)
- Redis: localhost:6379 (internal use)

---

**✅ After following these steps, your OpenWebUI should display both pipelines and allow you to chat with the medical assistant!**