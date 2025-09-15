# 🏥 Medical Assistant + OpenWebUI Local Development Setup

This guide helps you set up the Medical Assistant chat application with OpenWebUI for local development.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the complete setup script
./setup-local-dev.sh
```

### Option 2: Manual Setup
Follow the steps below if you prefer manual control.

## 📋 Prerequisites

- **Docker** - For PostgreSQL database
- **Python 3.8+** - For FastAPI backend
- **Node.js 18+** - For OpenWebUI frontend
- **Git** - For cloning repositories

## 🔧 Manual Setup Steps

### Step 1: Setup OpenWebUI
```bash
# Clone OpenWebUI repository
mkdir -p openwebui
cd openwebui
git clone https://github.com/open-webui/open-webui.git
cd ..
```

### Step 2: Setup Backend Environment
```bash
# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

### Step 3: Setup Configuration Files
```bash
# Copy configuration templates
cp backend-config.env backend/.env
cp openwebui-config.env openwebui/open-webui/backend/.env

# IMPORTANT: Edit backend/.env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_openai_api_key_here
```

### Step 4: Setup Pipeline Integration
```bash
# Create pipeline symlink in OpenWebUI
cd openwebui/open-webui
ln -s /Users/rudra/Desktop/chat-agent-app/pipelines ./pipelines
cd ../..

# Install OpenWebUI dependencies
cd openwebui/open-webui
npm install
cd ../..
```

### Step 5: Start Services
```bash
# Start database
docker-compose up -d postgres

# Start your medical assistant backend (in new terminal)
./start-backend.sh

# Start OpenWebUI backend (in new terminal)
./start-openwebui-backend.sh

# Start OpenWebUI frontend (in new terminal)
./start-openwebui-frontend.sh
```

**Alternative: Start OpenWebUI together**
```bash
# Start OpenWebUI backend + frontend together
./start-openwebui-local.sh
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **OpenWebUI Frontend** | http://localhost:5173 | Enhanced chat interface |
| **OpenWebUI Backend** | http://localhost:8080 | OpenWebUI API |
| **Medical Assistant Backend** | http://localhost:8000 | Your medical assistant API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **PostgreSQL** | localhost:5432 | Database |

## 🔧 Available Models

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

## 📁 Project Structure

```
/workspace/
├── backend/                    # FastAPI medical assistant
│   ├── .env                   # Backend configuration (create from template)
│   ├── app/                   # Application code
│   └── venv/                  # Python virtual environment
├── openwebui/
│   └── open-webui/            # OpenWebUI repository
│       ├── backend/.env       # OpenWebUI configuration (create from template)
│       └── pipelines/         # Symlink to your pipelines
├── pipelines/                 # Your custom pipelines
│   ├── medical_assistant_pipeline.py
│   ├── pdf_summarizer_pipeline.py
│   └── pipelines.json
├── docker-compose.yml         # Database services only
├── backend-config.env         # Backend config template
├── openwebui-config.env       # OpenWebUI config template
└── start-*.sh                # Startup scripts
```

## 🔄 Development Workflow

### Starting Development
```bash
# Start everything
./setup-local-dev.sh  # First time only

# Terminal 1: Start database
docker-compose up -d postgres

# Terminal 2: Start your medical assistant backend
./start-backend.sh

# Terminal 3: Start OpenWebUI backend
./start-openwebui-backend.sh

# Terminal 4: Start OpenWebUI frontend
./start-openwebui-frontend.sh
```

**Alternative: Start OpenWebUI together**
```bash
# Terminal 3: Start OpenWebUI backend + frontend together
./start-openwebui-local.sh
```

### Stopping Services
```bash
# Stop database
docker-compose down

# Stop backend (Ctrl+C in terminal)
# Stop OpenWebUI (Ctrl+C in terminal)
```

### Making Changes
- **Backend changes**: Restart backend script
- **Pipeline changes**: Restart OpenWebUI script
- **Frontend changes**: OpenWebUI auto-reloads

## 🐛 Troubleshooting

### Backend Won't Start
1. Check if port 8000 is in use: `lsof -i :8000`
2. Verify PostgreSQL is running: `docker ps`
3. Check backend logs for errors
4. Ensure `.env` file exists in `backend/` directory

### OpenWebUI Won't Start
1. Check if port 5173 is in use: `lsof -i :5173`
2. Verify Node.js is installed: `node --version`
3. Check if `node_modules` exists: `ls openwebui/open-webui/node_modules`
4. Try reinstalling: `cd openwebui/open-webui && npm install`

### Pipeline Issues
1. Check pipeline symlink: `ls -la openwebui/open-webui/pipelines`
2. Verify pipeline files exist: `ls pipelines/`
3. Check OpenWebUI logs for pipeline errors

### Database Connection Issues
1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Test connection: `psql -h localhost -U chatapp -d chatapp_db`
3. Check Docker logs: `docker-compose logs postgres`

## 🔧 Configuration

### Backend Configuration (`backend/.env`)
```env
# Required: Add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here

# Database (already configured)
DATABASE_URL=postgresql+asyncpg://chatapp:chatapp_password@localhost:5432/chatapp_db

# Other settings are pre-configured
```

### OpenWebUI Configuration (`openwebui/open-webui/backend/.env`)
```env
# Backend connection
BACKEND_URL=http://localhost:8000
FASTAPI_BASE_URL=http://localhost:8000

# Pipeline configuration
PIPELINES_DIR=/Users/rudra/Desktop/chat-agent-app/pipelines
ENABLE_PIPELINES=true
```

## 🧪 Testing the Integration

### Test Medical Assistant
1. Open http://localhost:5173
2. Select "medical-assistant" model
3. Send: "What are the latest treatments for diabetes?"
4. Should receive PubMed research response

### Test PDF Tool
1. Send: "Can you help summarize this PDF about cardiology?"
2. Should activate PDF summarizer tool
3. Should provide guidance on PDF processing

### Test Chat History
1. Send multiple messages
2. Refresh the page
3. Check if conversation persists

## 📚 Next Steps

1. **Add your OpenAI API key** to `backend/.env`
2. **Test the setup** by accessing http://localhost:5173
3. **Customize pipelines** in the `pipelines/` directory
4. **Develop and iterate** with fast local development!

## 💡 Benefits of This Setup

- **⚡ Faster Development**: No Docker rebuilds for code changes
- **🔧 Easy Debugging**: Direct access to backend and frontend processes
- **🔍 Better Logging**: Real-time logs in your terminal
- **⚙️ Environment Control**: Easy environment variable management
- **🚀 Quick Iteration**: Instant restarts for testing changes

Happy coding! 🎉
