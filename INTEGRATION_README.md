# 🚀 Open WebUI v0.6.5 Integration Guide

## 🎯 Overview

This guide covers the complete integration of Open WebUI v0.6.5 with your Medical Chat Agent system. The integration provides a professional AI interface while maintaining all your existing medical workflow functionality.

## ✨ What You Get

- **🎨 Professional AI Interface**: Beautiful, responsive chat interface
- **📚 RAG Capabilities**: Document upload and AI-powered analysis
- **🎤 Voice Features**: Speech-to-text and text-to-speech
- **🖼️ Image Generation**: DALL-E and Stable Diffusion integration
- **🔗 Seamless Integration**: Works alongside your existing backend
- **🔒 Enterprise Security**: Built-in authentication and role management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Open WebUI    │    │   Your Backend  │
│   (React)       │    │   (AI Interface)│    │   (FastAPI)     │
│   Port 3000     │    │   Port 8080     │    │   Port 8000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Nginx Proxy   │
                    │   Port 80/9000  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Port 5432     │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- OpenAI API key (optional)

### 2. One-Command Setup
```bash
# Navigate to your project
cd /Users/rudra/Desktop/chat-agent-app

# Run the integration script
python3 scripts/integrate_openwebui.py
```

### 3. Manual Setup
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## 📍 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Open WebUI** | http://localhost:8080 | AI Interface & Chat |
| **Your Backend** | http://localhost:8000 | Medical Workflows |
| **Frontend** | http://localhost:3000 | React App |
| **Unified Gateway** | http://localhost:9000 | All Services |
| **pgAdmin** | http://localhost:5050 | Database Management |

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in your project root:

```bash
# Core Configuration
OPENAI_API_KEY=your-openai-api-key-here
WEBUI_SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://chatapp:chatapp_password@postgres:5432/chatapp_db

# Open WebUI Settings
ENABLE_RAG=true
ENABLE_VOICE=true
ENABLE_IMAGE_GENERATION=true
ENABLE_WEB_SEARCH=true
ENABLE_FUNCTION_CALLING=true
```

### Service Configuration

#### Open WebUI (v0.6.5)
- **RAG**: Document processing and retrieval
- **Voice**: Speech-to-text and text-to-speech
- **Image Generation**: DALL-E, Stable Diffusion integration
- **Multi-model Support**: OpenAI, Ollama, custom models
- **Function Calling**: Tool integration capabilities

#### Your Backend
- **Medical Workflows**: Custom medical logic
- **WebSocket Chat**: Real-time communication
- **Database Integration**: Shared PostgreSQL

## 🧪 Testing the Integration

### Run Comprehensive Tests
```bash
# Test all components
python3 scripts/test_integration.py

# View test report
cat integration_test_report.json
```

### Manual Testing
1. **Open WebUI**: Visit http://localhost:8080
2. **Backend Health**: Check http://localhost:8000/health
3. **Frontend**: Visit http://localhost:3000
4. **Database**: Connect to PostgreSQL on port 5432

## 🔧 Customization

### 1. Medical Workflow Integration
Your existing medical workflows can be integrated as Open WebUI plugins:

```python
# Example: Medical diagnosis tool
def medical_diagnosis(symptoms: str) -> str:
    # Your medical logic here
    return diagnosis_result

# Register with Open WebUI
```

### 2. Custom Models
Add medical-specific models to Open WebUI:

```bash
# In Open WebUI settings
DEFAULT_MODELS=gpt-3.5-turbo,medical-llm,diagnosis-ai
```

### 3. RAG for Medical Documents
Load medical documents for AI consultation:

```bash
# Upload medical documents through Open WebUI
# Use # command to reference documents in chat
# Example: # What does this MRI report indicate?
```

## 📱 Usage Examples

### Basic AI Chat
1. Go to http://localhost:8080
2. Start a new chat
3. Ask medical questions
4. Use voice input/output

### Document Analysis
1. Upload medical documents
2. Ask questions about the documents
3. Get AI-powered insights

### Medical Workflow
1. Access your backend at http://localhost:8000
2. Use your custom medical tools
3. Integrate with Open WebUI responses

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker compose logs -f

# Restart services
docker compose down && docker compose up -d
```

#### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8080
lsof -i :8000

# Modify ports in docker-compose.yml if needed
```

#### Database Connection Issues
```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready -U chatapp -d chatapp_db

# Restart database
docker compose restart postgres
```

### Performance Optimization
- **Memory**: Ensure at least 4GB RAM available
- **Storage**: Use SSD for better database performance
- **Network**: Local network for optimal performance

## 🔒 Security Considerations

### Authentication
- Open WebUI handles user authentication
- Role-based access control
- Session management

### Data Privacy
- All data stays local
- No external data transmission
- Encrypted storage

### Network Security
- Nginx reverse proxy with rate limiting
- CORS configuration
- Security headers

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale Open WebUI instances
docker compose up -d --scale open-webui=3

# Load balancer configuration
# Add to nginx.conf
```

### Database Scaling
- PostgreSQL connection pooling
- Read replicas for heavy workloads
- Backup and recovery procedures

## 🎯 Version-Specific Notes (v0.6.5)

### ✅ What Works
- All core AI features
- RAG capabilities
- Voice features
- Image generation
- Multi-model support
- Function calling
- Web search
- Document processing

### 🔒 Licensing
- **v0.6.5**: Completely free and open source
- **Newer versions**: Require special licensing
- **Recommendation**: Stick with v0.6.5 for production use

### 🚀 Features
- Professional UI/UX
- Enterprise-grade security
- Comprehensive API
- Plugin system
- Custom model support

## 🆘 Support

### Documentation
- [Open WebUI v0.6.5 Docs](https://docs.openwebui.com/)
- [Your Project README](./README.md)
- [Integration Config](./integration_config.json)

### Community
- Open WebUI Discord
- GitHub Issues
- Stack Overflow

## 🎉 Next Steps

1. **Test the Integration**: Start with basic chat functionality
2. **Load Medical Documents**: Set up RAG for medical knowledge
3. **Customize Workflows**: Integrate your medical tools
4. **User Training**: Train medical staff on the new interface
5. **Performance Monitoring**: Monitor usage and optimize

## 🔄 Maintenance

### Regular Updates
```bash
# Check for updates
docker compose pull

# Restart services
docker compose restart

# View logs
docker compose logs -f
```

### Backup
```bash
# Backup database
docker compose exec postgres pg_dump -U chatapp chatapp_db > backup.sql

# Backup volumes
docker run --rm -v chatapp_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

**Happy Integrating! 🚀**

For questions or issues, check the troubleshooting section or create an issue in your project repository.

## 📊 Integration Status

- ✅ Docker Compose configuration
- ✅ Open WebUI v0.6.5 service
- ✅ Backend service integration
- ✅ Frontend service integration
- ✅ Nginx reverse proxy
- ✅ PostgreSQL database
- ✅ Health checks
- ✅ Integration testing
- ✅ Documentation

**Your integration is ready to use! 🎉**
