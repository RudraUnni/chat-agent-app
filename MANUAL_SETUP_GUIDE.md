# 🏥 Medical Assistant + OpenWebUI Manual Setup Guide

This guide provides step-by-step instructions to manually set up and run your Medical Assistant chat application with OpenWebUI integration.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenWebUI     │────│  Your Backend    │────│   PostgreSQL    │
│   Frontend      │    │  (FastAPI)       │    │   Database      │
│   (Port 5173)   │    │  (Port 8000)     │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │              ┌────────────────┐
         └──────────────│   Pipelines    │
                        │   - Medical    │
                        │   - PDF Tool   │
                        └────────────────┘
```

## 📋 Prerequisites

- **Docker** - For PostgreSQL database
- **Python 3.8+** - For FastAPI backends
- **Node.js 18+** - For OpenWebUI frontend
- **Git** - For cloning repositories

## 🚀 Complete Manual Setup

### Step 1: Start PostgreSQL Database

```bash
# Start PostgreSQL in Docker
docker-compose up -d postgres

# Verify it's running
docker ps | grep postgres

# Check database connection
psql -h localhost -U chatapp -d chatapp_db
# Password: chatapp_password
```

### Step 2: Setup Your Medical Assistant Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template
cp ../backend-config.env .env

# Edit .env file and add your OpenAI API key
nano .env
# Add: OPENAI_API_KEY=your_actual_openai_api_key_here

# Start your backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Step 3: Setup OpenWebUI Backend

```bash
# Navigate to OpenWebUI backend directory
cd openwebui/open-webui/backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template
cp ../../../openwebui-config.env .env

# Start OpenWebUI backend
export CORS_ALLOW_ORIGIN="http://localhost:5173"
export PORT=8080
uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' --reload
```

**OpenWebUI Backend will be available at:**
- API: http://localhost:8080
- Health: http://localhost:8080/health

### Step 4: Setup OpenWebUI Frontend

```bash
# Navigate to OpenWebUI frontend directory
cd openwebui/open-webui

# Install dependencies (if not done)
npm install

# Create pipeline symlink for local development
ln -s /Users/rudra/Desktop/chat-agent-app/pipelines ./pipelines

# Start OpenWebUI frontend
npm run dev
```

**OpenWebUI Frontend will be available at:**
- UI: http://localhost:5173

## 🔗 Pipeline Integration

### How Pipelines Work

1. **Pipeline Files** are located in `/pipelines/` directory
2. **OpenWebUI** loads these pipelines via symlink
3. **Pipeline Selection** happens based on model selection in UI
4. **Request Forwarding** sends requests to your FastAPI backend

### Pipeline Configuration

```python
# In medical_assistant_pipeline.py
class Valves(BaseModel):
    FASTAPI_BASE_URL: str = "http://localhost:8000"  # Your backend
    API_ENDPOINT: str = "/api/v1/chat"
    WORKFLOW: str = "pubmed_research"
```

### Available Pipelines

1. **Medical Assistant Pipeline** (`medical_assistant_pipeline.py`)
   - Routes requests to your FastAPI backend
   - Uses `pubmed_research` workflow
   - Handles conversation history and session management

2. **PDF Summarizer Pipeline** (`pdf_summarizer_pipeline.py`)
   - Medical document summarization tool
   - Activates with PDF-related keywords
   - Uses your medical assistant workflow for analysis

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **OpenWebUI Frontend** | http://localhost:5173 | Chat interface |
| **OpenWebUI Backend** | http://localhost:8080 | OpenWebUI API |
| **Your Backend** | http://localhost:8000 | Medical assistant API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **PostgreSQL** | localhost:5432 | Database |

## 🧪 Testing the Integration

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Test 2: Available Models
```bash
curl http://localhost:8000/api/v1/chat/models
# Expected: List of your medical assistant models
```

### Test 3: OpenWebUI Backend
```bash
curl http://localhost:8080/health
# Expected: OpenWebUI health status
```

### Test 4: Full Integration
1. Open http://localhost:5173
2. Select "medical-assistant" model
3. Send: "What are the latest treatments for diabetes?"
4. Should receive PubMed research response

### Test 5: PDF Tool
1. Send: "Can you help summarize this PDF about cardiology?"
2. Should activate PDF summarizer tool
3. Should provide guidance on PDF processing

## ⚙️ Configuration Files

### Your Backend Configuration (`backend/.env`)
```env
# Required: Add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://chatapp:chatapp_password@localhost:5432/chatapp_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chatapp_db
DATABASE_USER=chatapp
DATABASE_PASSWORD=chatapp_password

# Application Settings
ENVIRONMENT=development
DEBUG=true
APP_NAME=Medical Assistant API
APP_VERSION=1.0.0

# CORS Settings for OpenWebUI
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001", "http://127.0.0.1:3001"]

# LLM Configuration
DEFAULT_LLM_MODEL=gpt-4o-mini
DEFAULT_LLM_PROVIDER=openai

# PubMed Configuration
PUBMED_MAX_RESULTS=5
PUBMED_TIMEOUT=15
```

### OpenWebUI Backend Configuration (`openwebui/open-webui/backend/.env`)
```env
# Core OpenWebUI Settings
WEBUI_SECRET_KEY=medical-assistant-local-dev-key-change-in-production
WEBUI_AUTH=false
WEBUI_NAME=Medical Assistant Chat
DEFAULT_MODELS=medical-assistant,pubmed-research

# Backend Integration
BACKEND_URL=http://localhost:8000
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_WORKFLOW=pubmed_research

# Features
ENABLE_SIGNUP=true
ENABLE_MESSAGE_RATING=true
ENABLE_MODEL_FILTER=true
ENABLE_COMMUNITY_SHARING=false

# Pipeline Configuration
PIPELINES_DIR=/Users/rudra/Desktop/chat-agent-app/pipelines
ENABLE_PIPELINES=true

# Development Settings
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./openwebui.db
```

## 🔄 Complete Startup Sequence

### Terminal 1: PostgreSQL Database
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Verify it's running
docker ps | grep postgres
```

### Terminal 2: Your Medical Assistant Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: OpenWebUI Backend
```bash
cd openwebui/open-webui/backend
source venv/bin/activate
export CORS_ALLOW_ORIGIN="http://localhost:5173"
uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' --reload
```

### Terminal 4: OpenWebUI Frontend
```bash
cd openwebui/open-webui
npm run dev
```

## 🛑 Stopping Services

### Stop PostgreSQL
```bash
docker-compose down
```

### Stop Backend Services
```bash
# Find and kill backend processes
pkill -f uvicorn

# Or kill specific ports
lsof -ti:8000 | xargs kill -9  # Your backend
lsof -ti:8080 | xargs kill -9  # OpenWebUI backend
lsof -ti:5173 | xargs kill -9  # OpenWebUI frontend
```

## 🐛 Troubleshooting

### Backend Won't Start
1. **Check port availability:**
   ```bash
   lsof -i :8000
   ```

2. **Check database connection:**
   ```bash
   docker ps | grep postgres
   psql -h localhost -U chatapp -d chatapp_db
   ```

3. **Check backend logs:**
   ```bash
   # Look for error messages in terminal
   ```

### OpenWebUI Won't Start
1. **Check port availability:**
   ```bash
   lsof -i :8080  # Backend
   lsof -i :5173  # Frontend
   ```

2. **Check dependencies:**
   ```bash
   cd openwebui/open-webui
   npm install
   ```

3. **Check pipeline symlink:**
   ```bash
   ls -la openwebui/open-webui/pipelines
   ```

### Pipeline Issues
1. **Check pipeline files:**
   ```bash
   ls -la pipelines/
   ```

2. **Check symlink:**
   ```bash
   ls -la openwebui/open-webui/pipelines
   ```

3. **Test pipeline connectivity:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test", "workflow": "pubmed_research"}'
   ```

## 📚 Available Models

- **medical-assistant** - PubMed Research workflow
- **pubmed-research** - Direct PubMed search

## 🛠️ Pipeline Tools

### Medical Assistant Pipeline
- **Activation**: Select "medical-assistant" model
- **Features**: PubMed research, medical analysis, conversation history
- **Use Case**: General medical queries and research

### PDF Summarizer Pipeline
- **Activation**: Mention keywords like "PDF", "summarize", "document", "paper"
- **Features**: Medical document analysis and summarization
- **Use Case**: Research paper summaries, clinical guidelines

## 🔧 Development Workflow

### Making Changes
- **Backend changes**: Restart backend terminal
- **Pipeline changes**: Restart OpenWebUI backend terminal
- **Frontend changes**: OpenWebUI auto-reloads

### Debugging
- **Backend logs**: Check terminal output
- **OpenWebUI logs**: Check terminal output
- **Database logs**: `docker-compose logs postgres`

## 📁 Project Structure

```
/workspace/
├── backend/                    # Your FastAPI medical assistant
│   ├── .env                   # Backend configuration
│   ├── app/                   # Application code
│   └── venv/                  # Python virtual environment
├── openwebui/
│   └── open-webui/            # OpenWebUI repository
│       ├── backend/.env       # OpenWebUI configuration
│       ├── backend/venv/      # OpenWebUI backend environment
│       └── pipelines/         # Symlink to your pipelines
├── pipelines/                 # Your custom pipelines
│   ├── medical_assistant_pipeline.py
│   ├── pdf_summarizer_pipeline.py
│   └── pipelines.json
├── docker-compose.yml         # Database services
├── backend-config.env         # Backend config template
├── openwebui-config.env       # OpenWebUI config template
└── MANUAL_SETUP_GUIDE.md      # This guide
```

## 🎯 Quick Reference

### Essential Commands
```bash
# Start database
docker-compose up -d postgres

# Start your backend
cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start OpenWebUI backend
cd openwebui/open-webui/backend && source venv/bin/activate && uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' --reload

# Start OpenWebUI frontend
cd openwebui/open-webui && npm run dev
```

### Health Checks
```bash
curl http://localhost:8000/health    # Your backend
curl http://localhost:8080/health    # OpenWebUI backend
curl http://localhost:5173           # OpenWebUI frontend
```

### Stop Everything
```bash
docker-compose down
pkill -f uvicorn
pkill -f vite
```

---

**🎉 You're all set! Your Medical Assistant + OpenWebUI integration is ready for development.**
