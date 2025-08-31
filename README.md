# 🏥 Medical Assistant Pro

**A plug-and-play medical chat assistant demo that runs via Docker, uses OpenWebUI, and integrates with FastAPI workflows.**

## 🚀 Quick Start

### One-Command Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd chat-agent-app

# Run the demo setup (this does everything!)
./demo_setup.sh
```

### Manual Setup
```bash
# 1. Start Open WebUI and PostgreSQL
docker compose up -d postgres open-webui

# 2. Start the medical backend
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## 📱 Access Your Medical Assistant

- **🌐 Open WebUI Interface**: http://localhost:8080
- **🔧 Medical Backend**: http://localhost:8001
- **💚 Health Check**: http://localhost:8001/health

## 🎯 What You Get

✅ **Professional Medical AI Interface** - Beautiful Open WebUI with medical branding  
✅ **Medical Workflows** - PubMed research, consultation, document analysis  
✅ **RAG Capabilities** - Upload and analyze medical documents  
✅ **Voice Features** - Speech-to-text and text-to-speech  
✅ **Chat Memory** - Persistent conversation history and context  
✅ **Docker Ready** - One-command deployment  

## 🧪 Demo Scenarios

### 1. Medical Research
Ask: *"What are the latest treatments for diabetes?"*

### 2. Document Analysis
Upload a medical research paper and ask questions about it

### 3. Medical Consultation
Describe symptoms and get AI-powered insights

## 🔧 Management

```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart everything
./demo_setup.sh

# Stop backend only
kill $(cat .backend_pid)
```

## 📚 Documentation

- **Demo Instructions**: `DEMO_INSTRUCTIONS.md` - Complete demo guide
- **Integration Guide**: `INTEGRATION_README.md` - Technical details
- **Deliverables**: `DELIVERABLES_SUMMARY.md` - What's been achieved

## 🎉 Deliverables Status

- ✅ **Deliverable 1**: OpenWebUI running side-by-side with backend
- ✅ **Deliverable 2**: Medical agent with chat memory and tools  
- ✅ **Deliverable 3**: Plug-and-play demo ready for presentation

## 🚀 Next Steps

1. **Customize Branding** - Update colors, logos, and themes
2. **Add Medical Tools** - Integrate more medical workflows
3. **Deploy to Production** - Scale for multiple users
4. **Mobile App** - Create mobile interface

---

**🏥 Your Medical Assistant Pro is ready for demonstration! 🏥**

*Built with Open WebUI v0.6.5, FastAPI, and PostgreSQL*