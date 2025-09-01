# 🏥 Medical Assistant Pro - Step-by-Step Demo Guide

## 🎯 **Overview**
This guide provides detailed step-by-step instructions to run your Medical Assistant Pro demo, which integrates OpenWebUI v0.6.5 with your FastAPI medical backend.

---

## 📋 **Prerequisites**

### **Required Software**
1. **Docker** (version 20.10+)
   - Download from: https://www.docker.com/get-started
   - Verify: `docker --version`

2. **Docker Compose** (v2.0+)
   - Usually comes with Docker Desktop
   - Verify: `docker compose version`

3. **Python 3** (version 3.8+)
   - Download from: https://www.python.org/downloads/
   - Verify: `python3 --version`

### **System Requirements**
- **RAM**: Minimum 4GB available
- **Storage**: 2GB free space
- **Ports**: 8000, 8080, 5432 must be available

---

## 🚀 **Method 1: One-Command Demo (Recommended)**

### **Step 1: Navigate to Project Directory**
```bash
cd /path/to/your/project
```

### **Step 2: Run the Demo**
```bash
./run_working_demo.sh
```

### **Step 3: Wait for Completion**
The script will automatically:
- ✅ Check prerequisites
- ✅ Create configuration files
- ✅ Start all services in correct order
- ✅ Wait for services to be healthy
- ✅ Display access URLs

### **Step 4: Access the Demo**
When you see this message:
```
🎉 Demo is Ready!
📱 Access Points:
  • OpenWebUI Interface: http://localhost:8080
```

Open your browser and go to: **http://localhost:8080**

---

## 🔧 **Method 2: Manual Step-by-Step**

### **Step 1: Prepare Environment**
```bash
# Check if ports are free
lsof -i :8000 :8080 :5432

# If ports are in use, stop conflicting services
lsof -ti :8000 | xargs kill -9  # Stop anything on port 8000
lsof -ti :8080 | xargs kill -9  # Stop anything on port 8080
```

### **Step 2: Create Configuration File**
```bash
# Create .env file
cat > .env << 'EOF'
# OpenWebUI Configuration
WEBUI_SECRET_KEY=medical-assistant-pro-demo-2024
OPENAI_API_KEY=your-openai-api-key-here

# Medical Assistant Configuration
MEDICAL_ASSISTANT_ENABLED=true
MEDICAL_WORKFLOW_URL=http://backend:8000
MEDICAL_API_ENDPOINT=http://backend:8000/api/v1/chat

# Database
DATABASE_URL=postgresql://chatapp:chatapp_password@postgres:5432/chatapp_db
EOF
```

### **Step 3: Start Database Service**
```bash
# Start PostgreSQL database
docker compose up -d postgres

# Wait for database to be ready (takes ~10-15 seconds)
echo "Waiting for database..."
sleep 15

# Verify database is ready
docker compose exec postgres pg_isready -U chatapp -d chatapp_db
```

### **Step 4: Start Backend Service**
```bash
# Build and start the FastAPI backend
docker compose up -d backend

# Wait for backend to start (takes ~20-30 seconds)
echo "Waiting for backend..."
sleep 30

# Verify backend is healthy
curl http://localhost:8000/health
```

### **Step 5: Start OpenWebUI Service**
```bash
# Start OpenWebUI interface
docker compose up -d open-webui

# Wait for OpenWebUI to start (takes ~30-45 seconds)
echo "Waiting for OpenWebUI..."
sleep 45

# Verify OpenWebUI is accessible
curl -I http://localhost:8080
```

### **Step 6: Start Nginx Proxy (Optional)**
```bash
# Start nginx reverse proxy
docker compose up -d nginx

# Verify all services are running
docker compose ps
```

### **Step 7: Verify Integration**
```bash
# Run integration tests
python3 test_working_integration.py
```

---

## 🌐 **Accessing the Demo**

### **Step 1: Open OpenWebUI**
1. Open your web browser
2. Navigate to: **http://localhost:8080**
3. You should see the OpenWebUI login page with "Medical Assistant Pro" branding

### **Step 2: Create Account**
1. Click **"Sign up"** (first user becomes admin)
2. Fill in your details:
   - **Name**: Your Name
   - **Email**: your.email@example.com
   - **Password**: Choose a secure password
3. Click **"Create Account"**

### **Step 3: First Login**
1. After account creation, you'll be automatically logged in
2. You should see the OpenWebUI dashboard with medical branding
3. Look for the "Medical Assistant Pro" title and medical color scheme

### **Step 4: Start Your First Chat**
1. Click **"New Chat"** or the **"+"** button
2. You should see a new chat interface
3. The interface should show medical branding and styling

---

## 💬 **Testing the Medical Integration**

### **Test 1: Basic Medical Query**
**Type this message:**
```
What are the latest treatments for diabetes?
```

**Expected Response:**
- The system should process your query (may take 10-30 seconds)
- You should receive a detailed response with medical information
- The response should include research citations from PubMed
- A medical disclaimer should be included at the end

### **Test 2: Research Paper Search**
**Type this message:**
```
Find recent research papers about COVID-19 vaccines
```

**Expected Response:**
- The system should search PubMed database
- You should receive a list of relevant research papers
- Each paper should include: PMID, title, authors, journal, date
- Papers should be recent and relevant to your query

### **Test 3: Specific Paper Analysis**
**Type this message (use an actual PMID):**
```
Tell me about PMID 34634718
```

**Expected Response:**
- The system should retrieve the specific paper details
- You should get a comprehensive summary including methodology and findings
- The response should include journal information and publication details

### **Test 4: Conversational Context**
**Have this conversation:**
```
User: What is hypertension?
Assistant: [Response about hypertension]

User: What are the treatment options?
Assistant: [Should reference previous question about hypertension]

User: Are there any recent studies on this topic?
Assistant: [Should provide recent research on hypertension treatments]
```

**Expected Behavior:**
- Each response should build on previous context
- The assistant should remember what you're discussing
- Responses should be relevant to the ongoing conversation

---

## 🔍 **Troubleshooting**

### **Problem: Services Won't Start**

**Check Docker:**
```bash
# Verify Docker is running
docker info

# Check if containers are running
docker compose ps

# View service logs
docker compose logs
```

**Solution:**
```bash
# Restart Docker service
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop on Mac/Windows

# Clean restart
docker compose down --remove-orphans
./run_working_demo.sh
```

### **Problem: Port Conflicts**

**Check what's using ports:**
```bash
lsof -i :8000  # FastAPI backend
lsof -i :8080  # OpenWebUI
lsof -i :5432  # PostgreSQL
```

**Solution:**
```bash
# Kill processes using required ports
lsof -ti :8000 | xargs kill -9
lsof -ti :8080 | xargs kill -9
lsof -ti :5432 | xargs kill -9

# Restart demo
./run_working_demo.sh
```

### **Problem: OpenWebUI Shows Connection Error**

**Check backend connectivity:**
```bash
# Test backend health
curl http://localhost:8000/health

# Test medical workflow
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "workflow": "pubmed_research"}'
```

**Solution:**
```bash
# Restart backend service
docker compose restart backend

# Check backend logs
docker compose logs backend
```

### **Problem: Medical Queries Don't Work**

**Check integration:**
```bash
# Run integration tests
python3 test_working_integration.py

# Check OpenWebUI logs
docker compose logs open-webui
```

**Solution:**
```bash
# Restart OpenWebUI service
docker compose restart open-webui

# Verify function files exist
ls -la openwebui_functions/
```

### **Problem: Slow Response Times**

**Check system resources:**
```bash
# Check Docker resource usage
docker stats

# Check available memory
free -h
```

**Solution:**
- Ensure at least 4GB RAM is available
- Close unnecessary applications
- Consider increasing Docker memory limits

---

## 📊 **Verification Checklist**

After starting the demo, verify these items:

### **✅ Services Running**
- [ ] PostgreSQL database is healthy
- [ ] FastAPI backend responds to health checks
- [ ] OpenWebUI interface is accessible
- [ ] Nginx proxy is running (optional)

### **✅ Integration Working**
- [ ] OpenWebUI loads with medical branding
- [ ] Chat interface is responsive
- [ ] Medical queries return research-based responses
- [ ] Conversation history is maintained
- [ ] Medical disclaimers are included

### **✅ Features Functional**
- [ ] PubMed research integration works
- [ ] Paper lookup by PMID works
- [ ] Conversation context is preserved
- [ ] Error handling works gracefully

---

## 🎯 **Demo Scenarios**

### **Scenario 1: Medical Research Consultation**
1. Ask: "What are the latest treatments for Type 2 diabetes?"
2. Follow up: "What are the side effects of metformin?"
3. Continue: "Are there any natural alternatives?"

### **Scenario 2: Research Paper Analysis**
1. Ask: "Find papers about machine learning in medical diagnosis"
2. Pick a PMID from the results
3. Ask: "Summarize PMID [number] in detail"

### **Scenario 3: Clinical Decision Support**
1. Ask: "What are the diagnostic criteria for depression?"
2. Follow up: "What are the first-line treatments?"
3. Continue: "How do you monitor treatment effectiveness?"

---

## 🛑 **Stopping the Demo**

### **Clean Shutdown**
```bash
# Stop all services
docker compose down

# Remove volumes (optional - will delete data)
docker compose down --volumes
```

### **Quick Stop**
```bash
# Stop containers but keep data
docker compose stop
```

### **Restart Demo**
```bash
# Start again
./run_working_demo.sh
```

---

## 📞 **Support**

If you encounter issues:

1. **Check Logs**: `docker compose logs`
2. **Run Tests**: `python3 test_working_integration.py`
3. **Clean Restart**: `docker compose down && ./run_working_demo.sh`
4. **Verify Ports**: `lsof -i :8000,8080,5432`

---

## 🎉 **Success!**

When everything is working, you should have:
- ✅ Professional medical AI interface at http://localhost:8080
- ✅ Integrated PubMed research capabilities
- ✅ Conversation memory and context
- ✅ Medical disclaimers and safety features
- ✅ Responsive and branded user interface

**Enjoy your Medical Assistant Pro demo!** 🏥✨