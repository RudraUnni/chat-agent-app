# 🏥 Medical Assistant Pro - No Docker Setup Guide

## 🎯 **Running Without Docker**

If Docker is not available in your environment, you can still run and test the Medical Assistant Pro backend using Python directly.

---

## 🚀 **Quick Start (No Docker)**

### **Method 1: One-Command Setup**
```bash
# Run the no-docker demo
./run_demo_no_docker.sh
```

### **Method 2: Manual Setup**
```bash
# 1. Start the backend
python3 run_backend_standalone.py

# 2. In another terminal, test it
python3 test_standalone_integration.py
```

---

## 📋 **Prerequisites**

### **Required**
- **Python 3.8+** - `python3 --version`
- **pip** - Python package installer
- **curl** - For testing (usually pre-installed)

### **Python Packages** (auto-installed by scripts)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `pydantic` - Data validation
- `python-multipart` - Form data support

---

## 🔧 **What the No-Docker Solution Does**

### **Backend Modifications**
1. **Mock Database**: Creates an in-memory mock database instead of PostgreSQL
2. **Simplified Dependencies**: Removes Docker-specific configurations
3. **CORS Updates**: Allows all origins for testing
4. **Standalone Mode**: Runs directly with Python/uvicorn

### **Integration Testing**
1. **Health Checks**: Verifies backend is responding
2. **API Testing**: Tests medical workflow endpoints
3. **CORS Validation**: Ensures cross-origin requests work
4. **Error Handling**: Provides clear error messages

---

## 🧪 **Testing Your Setup**

### **Automated Testing**
```bash
# Run comprehensive tests
python3 test_standalone_integration.py
```

### **Manual Testing**
```bash
# 1. Check backend health
curl http://localhost:8000/health

# 2. Test root endpoint
curl http://localhost:8000/

# 3. Test medical workflow
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are treatments for diabetes?", "workflow": "pubmed_research"}'

# 4. View API documentation
open http://localhost:8000/docs
```

### **Expected Results**
- ✅ Health check returns: `{"status": "healthy"}`
- ✅ Root endpoint returns: `{"message": "Chat Agent API is running!"}`
- ✅ Medical workflow returns JSON with medical response
- ✅ API docs show interactive OpenAPI documentation

---

## 🌐 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | Main API endpoint |
| **Health Check** | http://localhost:8000/health | Service health status |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Medical Chat** | http://localhost:8000/api/v1/chat | Medical workflow endpoint |

---

## 🔍 **Troubleshooting**

### **Backend Won't Start**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process if needed
lsof -ti :8000 | xargs kill -9

# Check Python and dependencies
python3 --version
python3 -c "import fastapi; print('FastAPI installed')"
```

### **Dependencies Missing**
```bash
# Install manually if auto-install fails
pip install --break-system-packages fastapi uvicorn requests pydantic python-multipart

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests pydantic python-multipart
```

### **Connection Errors**
```bash
# Check if backend is running
curl -I http://localhost:8000

# Check backend logs
# (Look at terminal where backend is running)

# Restart backend
pkill -f uvicorn
python3 run_backend_standalone.py
```

### **Medical Workflow Errors**
```bash
# Test with simple query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "workflow": "pubmed_research"}'

# Check if OpenAI API key is needed
# (Some functions may require actual API key)
```

---

## 🎯 **What Works Without Docker**

### ✅ **Fully Functional**
- FastAPI backend server
- Medical workflow endpoints
- Health checks and monitoring
- API documentation
- CORS configuration
- Basic medical query processing
- Session management
- Error handling

### ⚠️ **Limited Functionality**
- **No PostgreSQL**: Uses mock database (conversations not persisted)
- **No OpenWebUI**: Frontend interface not available
- **No PubMed API**: May not work without proper API keys
- **No Docker Services**: No nginx, no service orchestration

### ❌ **Not Available**
- OpenWebUI interface (requires Docker or separate installation)
- Persistent database storage
- Multi-service orchestration
- Production-ready deployment

---

## 🔗 **Connecting to OpenWebUI (Advanced)**

If you want to use OpenWebUI with the standalone backend:

### **Option 1: Install OpenWebUI Separately**
```bash
# Install OpenWebUI using pip
pip install open-webui

# Run OpenWebUI pointing to your backend
open-webui serve --backend-url http://localhost:8000
```

### **Option 2: Use OpenWebUI Docker (if Docker available)**
```bash
# Run only OpenWebUI in Docker
docker run -d -p 8080:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/api/v1 \
  ghcr.io/open-webui/open-webui:v0.6.5
```

---

## 📊 **Performance Expectations**

### **Startup Time**
- Backend: ~5-10 seconds
- First request: ~2-5 seconds (dependency loading)
- Subsequent requests: ~1-3 seconds

### **Resource Usage**
- Memory: ~100-200MB
- CPU: Low (spikes during medical queries)
- Network: Depends on external API calls

### **Limitations**
- Single-threaded (development server)
- No database persistence
- Limited concurrent requests
- Not production-ready

---

## 🎉 **Success Criteria**

Your no-Docker setup is successful when:

### ✅ **Backend Tests Pass**
```bash
python3 test_standalone_integration.py
# Should show: ✅ Passed: 4/4
```

### ✅ **API Responds Correctly**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### ✅ **Medical Workflow Works**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "workflow": "pubmed_research"}'
# Should return JSON with medical response
```

---

## 🔄 **Next Steps**

### **For Development**
1. **Add Features**: Extend medical workflows
2. **Improve Testing**: Add more comprehensive tests
3. **Database**: Connect to real database if needed
4. **API Keys**: Add proper OpenAI/PubMed API keys

### **For Production**
1. **Install Docker**: Use full Docker setup for production
2. **Database Setup**: Configure PostgreSQL
3. **Frontend**: Deploy OpenWebUI or custom frontend
4. **Security**: Add authentication and HTTPS

### **For Integration**
1. **Connect Frontend**: Build or connect a frontend application
2. **API Integration**: Use the backend API from other applications
3. **Extend Workflows**: Add more medical tools and capabilities

---

## 📞 **Support**

If you encounter issues with the no-Docker setup:

### **Diagnostic Steps**
1. Run: `python3 test_standalone_integration.py`
2. Check: `curl http://localhost:8000/health`
3. View: Backend terminal output for errors
4. Verify: Python version and dependencies

### **Common Solutions**
- **Port conflicts**: Use `lsof -i :8000` to check
- **Dependencies**: Reinstall with `pip install --force-reinstall`
- **Permissions**: Try with `sudo` if needed
- **Python path**: Ensure you're in the project root directory

---

## 🎯 **Summary**

The no-Docker setup provides:
- ✅ **Working backend API** for testing and development
- ✅ **Medical workflow functionality** with basic features
- ✅ **Easy setup and testing** without Docker complexity
- ✅ **Good for development** and API testing

**Perfect for**: Development, testing, API integration, environments without Docker
**Not suitable for**: Production deployment, full-featured demo, multi-user scenarios

**Start your no-Docker demo**: `./run_demo_no_docker.sh`