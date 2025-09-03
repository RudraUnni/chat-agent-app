# Open WebUI Integration - Quick Reference

## 🚀 Getting Started
```bash
# Quick start (recommended)
./start-openwebui.sh

# Manual start
docker-compose up -d

# Check status
docker-compose ps
```

## 🌐 Access Points
| Service | URL | Purpose |
|---------|-----|---------|
| **Open WebUI** | http://localhost:3001 | Enhanced chat interface |
| **FastAPI Backend** | http://localhost:8000 | Medical assistant API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **pgAdmin** | http://localhost:5050 | Database management |

## 🔧 Key Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart Open WebUI only
docker-compose restart open-webui

# View logs
docker-compose logs open-webui
docker-compose logs backend
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Open WebUI health
curl http://localhost:3001/health

# Available models
curl http://localhost:8000/api/v1/chat/models
```

## 🛠️ Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration |
| `.env.openwebui` | Open WebUI configuration |
| `pipelines/medical_assistant_pipeline.py` | Main integration |
| `pipelines/pdf_summarizer_pipeline.py` | PDF tool |

## 📊 Testing

### Test Medical Assistant
```
Message: "What are the latest treatments for diabetes?"
Expected: Response from your PubMed research workflow
```

### Test PDF Tool
```
Message: "Can you help summarize this PDF about cardiology?"
Expected: PDF tool activation with guidance
```

### Test Chat History
```
1. Send a message
2. Refresh the page
3. Check if conversation persists
```

## 🔍 Troubleshooting

### Open WebUI Won't Start
```bash
# Check logs
docker-compose logs open-webui

# Check if backend is accessible
docker-compose exec open-webui ping backend
```

### Backend Connection Issues
```bash
# Check backend logs
docker-compose logs backend

# Test backend directly
curl http://localhost:8000/api/v1/chat/workflows
```

### Pipeline Issues
```bash
# Check pipeline files
ls -la pipelines/

# Check Open WebUI pipeline logs
docker-compose logs open-webui | grep -i pipeline
```

## 📁 File Structure
```
/workspace/
├── pipelines/                          # Open WebUI pipelines
│   ├── medical_assistant_pipeline.py   # Main integration
│   ├── pdf_summarizer_pipeline.py      # PDF tool
│   └── pipelines.json                  # Configuration
├── backend/
│   ├── Dockerfile                      # Backend container
│   └── app/                           # Your existing FastAPI app
├── docker-compose.yml                  # Updated with Open WebUI
├── .env.openwebui                      # Open WebUI config
├── start-openwebui.sh                  # Quick start script
└── OPENWEBUI_INTEGRATION_GUIDE.md      # Full documentation
```



