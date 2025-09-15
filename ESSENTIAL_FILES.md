# 📁 Essential Files for Medical Assistant + OpenWebUI

## 🚀 **Startup Scripts (Essential)**
- `setup-local-dev.sh` - Complete setup script (run once)
- `start-database.sh` - Start PostgreSQL database
- `start-backend.sh` - Start your medical assistant backend
- `start-openwebui-local.sh` - Start OpenWebUI (backend + frontend together)
- `start-openwebui-backend.sh` - Start OpenWebUI backend only
- `start-openwebui-frontend.sh` - Start OpenWebUI frontend only

## ⚙️ **Configuration Files (Essential)**
- `backend-config.env` - Backend configuration template
- `openwebui-config.env` - OpenWebUI configuration template
- `docker-compose.yml` - Database services

## 🔧 **Pipeline Files (Essential)**
- `pipelines/medical_assistant_pipeline.py` - Main medical assistant integration
- `pipelines/pdf_summarizer_pipeline.py` - PDF summarization tool
- `pipelines/pipelines.json` - Pipeline configuration

## 📚 **Documentation (Useful)**
- `LOCAL_OPENWEBUI_SETUP.md` - Complete setup and usage guide
- `README.md` - Project overview
- `QUICK_REFERENCE.md` - Quick commands reference

## 🗑️ **Files Removed (Redundant)**
- `start-openwebui.sh` - Replaced by `start-openwebui-local.sh`
- `start-all.sh` - Replaced by individual startup scripts

## 🎯 **Quick Start Commands**
```bash
# First time setup
./setup-local-dev.sh

# Start services
./start-database.sh
./start-backend.sh
./start-openwebui-local.sh
```

## 📋 **File Purposes**
- **Setup**: `setup-local-dev.sh` - One-time setup
- **Database**: `start-database.sh` - PostgreSQL
- **Backend**: `start-backend.sh` - Your medical assistant API
- **OpenWebUI**: `start-openwebui-local.sh` - Complete OpenWebUI
- **Configs**: `*-config.env` - Configuration templates
- **Pipelines**: `pipelines/*.py` - OpenWebUI integration
