# Open WebUI v0.6.5 Integration Guide

This guide provides step-by-step instructions to integrate Open WebUI v0.6.5 with your existing FastAPI medical assistant chat application.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Open WebUI    │────│  FastAPI Backend │────│   PostgreSQL    │
│   (Port 3001)   │    │   (Port 8000)    │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │              ┌────────────────┐
         └──────────────│   Pipelines    │
                        │   - Medical    │
                        │   - PDF Tool   │
                        └────────────────┘
```

## 📁 New Files Added

```
/workspace/
├── pipelines/
│   ├── medical_assistant_pipeline.py    # Main medical assistant integration
│   ├── pdf_summarizer_pipeline.py       # PDF summarization tool
│   ├── pipelines.json                   # Pipeline configuration
│   └── requirements.txt                 # Pipeline dependencies
├── backend/
│   └── Dockerfile                       # Backend containerization
├── docker-compose.yml                   # Updated with all services
├── .env.openwebui                       # Open WebUI configuration
└── OPENWEBUI_INTEGRATION_GUIDE.md       # This guide
```

## 🚀 Quick Start

### 1. Prerequisites Check
```bash
# Ensure you have these installed
docker --version
docker-compose --version

# Ensure your environment variables are set
echo $OPENAI_API_KEY  # Should show your OpenAI API key
```

### 2. Start All Services
```bash
# From your workspace root
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access Open WebUI
- Open your browser to: http://localhost:3001
- Create an account (if WEBUI_AUTH=false, you can skip login)
- You should see "Medical Assistant Chat" interface

### 4. Test the Integration
1. **Test Medical Assistant**: Send a message like "What are the latest treatments for diabetes?"
2. **Test PDF Tool**: Send a message like "Can you help me summarize this PDF about cardiology?"
3. **Check Chat History**: Your conversations are automatically saved

## 🔧 Configuration

### Environment Variables (.env.openwebui)

```env
# Core Open WebUI Settings
WEBUI_SECRET_KEY=your-medical-assistant-secret-key-change-this-in-production
WEBUI_AUTH=false                    # Set to true for authentication
WEBUI_NAME=Medical Assistant Chat
DEFAULT_MODELS=medical-assistant

# Backend Integration
FASTAPI_BASE_URL=http://backend:8000
FASTAPI_WORKFLOW=pubmed_research    # Your default workflow

# Features
ENABLE_SIGNUP=true
ENABLE_MESSAGE_RATING=true
ENABLE_MODEL_FILTER=true
ENABLE_COMMUNITY_SHARING=false
```

### Docker Compose Services

| Service | Port | Purpose |
|---------|------|---------|
| `backend` | 8000 | Your FastAPI medical assistant |
| `postgres` | 5432 | Database for your backend |
| `open-webui` | 3001 | Enhanced chat interface |
| `pgadmin` | 5050 | Database management (dev profile) |

## 🔌 Pipeline Integration

### Medical Assistant Pipeline
- **File**: `pipelines/medical_assistant_pipeline.py`
- **Purpose**: Routes chat requests to your FastAPI `/api/v1/chat` endpoint
- **Features**:
  - Session management
  - Conversation history
  - Error handling
  - Timeout management

### PDF Summarizer Pipeline
- **File**: `pipelines/pdf_summarizer_pipeline.py`
- **Purpose**: Demonstrates tool integration for document processing
- **Activation**: Mention keywords like "PDF", "summarize", "document"

## 🔄 Data Flow

1. **User Input** → Open WebUI interface
2. **Pipeline Selection** → Based on message content/model
3. **Request Forwarding** → Pipeline → Your FastAPI backend
4. **Workflow Execution** → Your existing medical assistant workflow
5. **Response Processing** → Backend → Pipeline → Open WebUI
6. **Chat History** → Automatically saved by Open WebUI

## 🛠️ Troubleshooting

### Common Issues

#### 1. Open WebUI Can't Connect to Backend
```bash
# Check if backend is running
docker-compose logs backend

# Test backend directly
curl http://localhost:8000/health
```

#### 2. Pipeline Not Loading
```bash
# Check Open WebUI logs
docker-compose logs open-webui

# Verify pipeline files
ls -la pipelines/
```

#### 3. Models Not Appearing
- Check that your backend `/api/v1/chat/models` endpoint is accessible
- Verify CORS settings in your FastAPI backend

### Debug Commands

```bash
# View all service logs
docker-compose logs

# Check specific service
docker-compose logs open-webui
docker-compose logs backend

# Restart specific service
docker-compose restart open-webui

# Check network connectivity
docker-compose exec open-webui ping backend
```

## 📊 Monitoring & Health Checks

### Service Health
```bash
# Check all services
docker-compose ps

# Health check endpoints
curl http://localhost:8000/health    # Backend
curl http://localhost:3001/health    # Open WebUI
```

### Chat History Location
- **Open WebUI**: `/var/lib/docker/volumes/workspace_open-webui-data/_data/`
- **Your Backend**: PostgreSQL database as configured

## 🔒 Security Considerations

### Production Deployment
1. **Change Secret Keys**:
   ```env
   WEBUI_SECRET_KEY=generate-a-strong-secret-key
   ```

2. **Enable Authentication**:
   ```env
   WEBUI_AUTH=true
   ENABLE_SIGNUP=false  # Control user registration
   ```

3. **API Security**:
   - Add API key authentication to your FastAPI backend
   - Configure the pipeline with your API key

4. **Network Security**:
   - Use internal Docker networks
   - Don't expose unnecessary ports in production

## 🎯 Advanced Configuration

### Custom Model Configuration
Edit `pipelines/medical_assistant_pipeline.py`:
```python
class Valves(BaseModel):
    FASTAPI_BASE_URL: str = "http://backend:8000"
    WORKFLOW: str = "your_custom_workflow"  # Change this
    API_KEY: str = "your-api-key"          # Add authentication
```

### Multiple Workflows
You can create additional pipelines for different medical specialties:
- `cardiology_pipeline.py`
- `radiology_pipeline.py`
- `emergency_medicine_pipeline.py`

### Custom Tools
Add more tools by creating new pipeline files:
- Drug interaction checker
- Medical calculator
- Clinical decision support

## 📈 Performance Optimization

### Backend Optimization
- Enable connection pooling in PostgreSQL
- Use Redis for session caching
- Implement response caching for common queries

### Open WebUI Optimization
- Use persistent volumes for faster startup
- Configure resource limits in docker-compose
- Enable compression in nginx (if using reverse proxy)

## 🔄 Updates & Maintenance

### Updating Open WebUI
```bash
docker-compose pull open-webui
docker-compose up -d open-webui
```

### Backup Chat History
```bash
# Backup Open WebUI data
docker run --rm -v workspace_open-webui-data:/data -v $(pwd):/backup alpine tar czf /backup/openwebui-backup.tar.gz -C /data .
```

### Pipeline Updates
- Modify pipeline files in the `pipelines/` directory
- Restart Open WebUI: `docker-compose restart open-webui`

## 🆘 Support

### Logs to Check
1. **Open WebUI**: `docker-compose logs open-webui`
2. **Backend**: `docker-compose logs backend`
3. **Database**: `docker-compose logs postgres`

### Configuration Files
- Pipeline configuration: `pipelines/pipelines.json`
- Environment: `.env.openwebui`
- Docker: `docker-compose.yml`

---

## ✅ Integration Checklist

- [ ] All services start successfully
- [ ] Open WebUI accessible at http://localhost:3001
- [ ] Medical assistant responds to queries
- [ ] Chat history is preserved
- [ ] PDF tool activates with keywords
- [ ] Backend health endpoint accessible
- [ ] CORS configured for Open WebUI domain
- [ ] Pipeline files mounted correctly
- [ ] Models appear in Open WebUI interface

**🎉 Your Open WebUI integration is complete!**

For additional support or customization, refer to:
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Your existing backend documentation