# 🚀 Local Development Setup Guide

Your setup has been updated to run the backend and Open WebUI locally while keeping only PostgreSQL (and optionally pgAdmin) in Docker containers.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker & Docker Compose** - For PostgreSQL database
- **Python 3.8+** - For the FastAPI backend
- **Node.js 18+** - For Open WebUI frontend
- **Git** - For cloning Open WebUI repository

## 🔧 What Changed

### ✅ Updated Docker Compose
- **Removed**: `backend` and `open-webui` services
- **Kept**: `postgres` and `pgadmin` services only
- PostgreSQL runs on `localhost:5432`
- pgAdmin (optional) runs on `localhost:5050`

### ✅ Environment Configuration
- Created `.env` files for local development
- Updated CORS settings for local connections
- Configured database connections to use `localhost`

### ✅ Startup Scripts
- `start-database.sh` - Start PostgreSQL (and optionally pgAdmin)
- `start-backend.sh` - Start your FastAPI backend locally
- `setup-openwebui.sh` - One-time Open WebUI setup
- `start-openwebui.sh` - Start Open WebUI locally
- `start-all.sh` - Start everything with one command

## 🚀 Quick Start (Recommended)

### Option 1: Start Everything at Once
```bash
./start-all.sh
```

This will:
1. Start PostgreSQL in Docker
2. Start your backend locally on port 8000
3. Set up Open WebUI (if first time)
4. Start Open WebUI locally on port 5173

### Option 2: Start Services Individually

#### 1. Start Database
```bash
./start-database.sh
```

#### 2. Start Backend
```bash
./start-backend.sh
```

#### 3. Setup Open WebUI (first time only)
```bash
./setup-openwebui.sh
```

#### 4. Start Open WebUI
```bash
./start-openwebui.sh
```

## 🔗 Service URLs

After everything is running:

- **🌐 Open WebUI**: http://localhost:5173
- **🔧 Backend API**: http://localhost:8000
- **📖 API Documentation**: http://localhost:8000/docs
- **🐘 PostgreSQL**: localhost:5432
- **📊 pgAdmin** (optional): http://localhost:5050

## ⚙️ Configuration

### Backend Environment Variables

Update `/workspace/backend/.env` with your actual values:

```env
# Required: Add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here

# Database (already configured for Docker PostgreSQL)
DATABASE_URL=postgresql+asyncpg://chatapp:chatapp_password@localhost:5432/chatapp_db

# Other settings are pre-configured
ENVIRONMENT=development
DEBUG=true
```

### Open WebUI Configuration

After running `setup-openwebui.sh`, update `openwebui/open-webui/.env`:

```env
# Add your OpenAI API key here too (optional, can be set via UI)
OPENAI_API_KEY=your_actual_openai_api_key_here

# Backend connection (pre-configured)
BACKEND_URL=http://localhost:8000
```

## 🐘 Database Access

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: chatapp_db
- **Username**: chatapp
- **Password**: chatapp_password

### pgAdmin Access (if enabled)
- **URL**: http://localhost:5050
- **Email**: admin@chatapp.local
- **Password**: admin_password

To connect pgAdmin to PostgreSQL:
1. Create new server in pgAdmin
2. Use `localhost` as host (or `host.docker.internal` on some systems)
3. Use the connection details above

## 🔄 Development Workflow

### Starting Development
```bash
# Start everything
./start-all.sh

# Or start individually:
./start-database.sh    # Start PostgreSQL
./start-backend.sh     # Start backend (in new terminal)
./start-openwebui.sh   # Start Open WebUI (in new terminal)
```

### Stopping Services
```bash
# Stop Docker services
docker-compose down

# Stop backend (if running)
# Press Ctrl+C in the backend terminal, or:
pkill -f uvicorn

# Stop Open WebUI (if running)
# Press Ctrl+C in the Open WebUI terminal, or:
pkill -f vite
```

### Restarting Services
```bash
# Restart backend only (for code changes)
# Press Ctrl+C and run again:
./start-backend.sh

# Restart Open WebUI (for frontend changes)
# Press Ctrl+C and run again:
./start-openwebui.sh
```

## 📁 Project Structure

```
/workspace/
├── backend/                 # Your FastAPI backend
│   ├── app/                # Application code
│   ├── .env               # Backend environment variables
│   ├── requirements.txt   # Python dependencies
│   └── venv/              # Python virtual environment (created automatically)
├── openwebui/             # Open WebUI (created by setup script)
│   └── open-webui/        # Cloned Open WebUI repository
├── pipelines/             # Your custom pipelines
├── docker-compose.yml     # Database services only
├── .env                   # Root environment variables
└── start-*.sh            # Startup scripts
```

## 🐛 Troubleshooting

### Backend Won't Start
1. Check if port 8000 is already in use: `lsof -i :8000`
2. Verify PostgreSQL is running: `docker ps`
3. Check backend logs: `tail -f logs/backend.log`
4. Ensure `.env` file exists in `backend/` directory

### Open WebUI Won't Start
1. Check if port 5173 is already in use: `lsof -i :5173`
2. Verify Node.js is installed: `node --version`
3. Check Open WebUI logs: `tail -f logs/openwebui.log`
4. Try reinstalling dependencies: `cd openwebui/open-webui && npm install`

### Database Connection Issues
1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Test connection: `psql -h localhost -U chatapp -d chatapp_db`
3. Check Docker logs: `docker-compose logs postgres`

### CORS Issues
1. Verify backend CORS settings include Open WebUI URL
2. Check browser console for CORS errors
3. Ensure backend is accessible at http://localhost:8000

## 🔧 Advanced Configuration

### Custom Ports
To use different ports, update these files:
- `docker-compose.yml` - Database ports
- `backend/app/main.py` - Backend port and CORS origins
- `start-*.sh` scripts - Port references
- `openwebui/open-webui/.env` - Backend URL

### Additional Environment Variables
Add any custom environment variables to:
- `backend/.env` - For backend configuration
- `openwebui/open-webui/.env` - For Open WebUI configuration

## 📚 Next Steps

1. **Set your OpenAI API key** in `backend/.env`
2. **Test the setup** by accessing http://localhost:5173
3. **Customize Open WebUI** settings through the web interface
4. **Add your custom pipelines** to the `pipelines/` directory
5. **Develop and iterate** with fast local development!

## 💡 Benefits of This Setup

- **⚡ Faster Development**: No Docker rebuilds for code changes
- **🔧 Easy Debugging**: Direct access to backend and frontend processes
- **🔍 Better Logging**: Real-time logs in your terminal
- **⚙️ Environment Control**: Easy environment variable management
- **🚀 Quick Iteration**: Instant restarts for testing changes

Happy coding! 🎉