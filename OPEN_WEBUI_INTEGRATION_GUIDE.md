# Open WebUI Integration Guide
## Medical Assistant + Open WebUI v0.6.5

### 🏥 Overview

This guide provides complete instructions for integrating Open WebUI v0.6.5 with your Medical Assistant application. The integration provides:

- **Enhanced AI Interface**: Modern Open WebUI interface alongside your existing medical assistant
- **Multiple AI Models**: Medical-specific models with PubMed integration
- **Unified Authentication**: Shared authentication between both systems
- **Security Hardening**: Mitigations for Open WebUI v0.6.5 vulnerabilities
- **Medical Templates**: Pre-configured templates for medical consultations

### ⚠️ Security Notice

**Open WebUI v0.6.5 has known security vulnerabilities:**
- CVE-2025-46571: Stored XSS vulnerability
- SSRF vulnerabilities

This integration includes security measures to mitigate these risks, but use caution in production environments.

---

## 🚀 Quick Start

### 1. Start the Integrated System

```bash
# Make the startup script executable (first time only)
chmod +x start-medical-ai.sh

# Start all services
./start-medical-ai.sh

# Alternative: Start with development tools
./start-medical-ai.sh dev

# Alternative: Start with production security
./start-medical-ai.sh prod
```

### 2. Start Backend Services

```bash
# Terminal 1: Start Medical Assistant API
cd backend
pip install -r requirements.txt
python -m app.main

# Terminal 2: Start React Frontend  
cd frontend
npm install
npm run dev
```

### 3. Access the Applications

- **Medical Assistant**: http://localhost:5173
- **Open WebUI**: http://localhost:3000
- **Integrated AI Interface**: http://localhost:5173/ai
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Configuration

### Medical Models Configuration

Open WebUI is pre-configured with three medical models:

1. **Medical Assistant** (`medical-assistant`)
   - PubMed integration enabled
   - Evidence-based responses
   - General medical consultation

2. **PubMed Research** (`pubmed-research`)
   - Specialized literature search
   - Research analysis
   - Citation support

3. **Medical Analysis** (`medical-analysis`)
   - Case analysis
   - Diagnostic support
   - Treatment planning

### Authentication

Default demo users:
- **Username**: `demo_admin` / **Password**: `demo_password` (Admin role)
- **Username**: `demo_doctor` / **Password**: `demo_password` (Doctor role)

Create demo users:
```bash
curl -X POST http://localhost:8000/api/v1/auth/create_demo_users
```

### Environment Variables

Key configuration in `.env.docker`:
```bash
# Security
WEBUI_SECRET_KEY=medical_assistant_secret_key_change_this_in_production
ENABLE_SIGNUP=false

# Database
POSTGRES_DB=chatapp_db
POSTGRES_USER=chatapp
POSTGRES_PASSWORD=chatapp_password
```

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Open WebUI    │    │   FastAPI       │
│ (localhost:5173)│◄──►│ (localhost:3000)│◄──►│ (localhost:8000)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │ (localhost:5432)│
                    └─────────────────┘
```

### Integration Points

1. **API Bridge**: FastAPI endpoints provide OpenAI-compatible API for Open WebUI
2. **Authentication Sync**: Unified JWT-based authentication
3. **Database Sharing**: Both systems use the same PostgreSQL database
4. **Security Layer**: Input validation and rate limiting
5. **Medical Templates**: Pre-configured medical consultation templates

---

## 🔒 Security Measures

### Implemented Protections

1. **Input Validation**
   - HTML sanitization with medical content preservation
   - XSS prevention
   - Input length limits

2. **Rate Limiting**
   - 60 requests per minute per IP
   - Configurable limits

3. **CORS Configuration**
   - Restricted origins
   - Secure headers

4. **Authentication**
   - JWT tokens with expiration
   - Disabled public signup
   - Role-based access

5. **HTTP Security Headers**
   - Content Security Policy
   - XSS Protection
   - Frame Options
   - CSRF protection

### Configuration Files

- `security_config/security_headers.conf`: Nginx security headers
- `security_config/input_validation.py`: Input sanitization
- `nginx/conf.d/default.conf`: Reverse proxy with security

---

## 📚 Medical Templates

### Available Templates

1. **Clinical Consultation**: Structured clinical case analysis
2. **Literature Review**: Comprehensive research requests
3. **Drug Interaction Analysis**: Medication safety checking
4. **Diagnostic Workup**: Diagnostic planning assistance
5. **Treatment Guidelines**: Evidence-based treatment review
6. **Case Presentation**: Medical case presentation format
7. **Patient Education**: Patient-friendly content creation
8. **Research Proposal**: Research development assistance

### Using Templates

1. Access Open WebUI at http://localhost:3000
2. Login with demo credentials
3. Select a medical model
4. Use template prompts from `open_webui_config/medical_prompts.json`

---

## 🐛 Troubleshooting

### Common Issues

**Open WebUI not accessible:**
```bash
# Check if container is running
docker ps | grep open-webui

# Check logs
docker logs medical_open_webui

# Restart service
docker-compose restart open-webui
```

**API connection errors:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check Open WebUI health
curl http://localhost:3000/health

# Check API bridge
curl http://localhost:8000/api/v1/openwebui/models
```

**Authentication issues:**
```bash
# Create demo users
curl -X POST http://localhost:8000/api/v1/auth/create_demo_users

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_admin", "password": "demo_password"}'
```

### Log Locations

- **Open WebUI**: `docker logs medical_open_webui`
- **FastAPI**: Backend console output
- **Nginx**: `docker logs medical_nginx` (production mode)
- **PostgreSQL**: `docker logs chatapp_postgres`

---

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes**: Modify files in `backend/app/api/v1/openwebui.py`
2. **Frontend Changes**: Update `frontend/src/pages/AIInterface.tsx`
3. **Security Updates**: Modify `security_config/` files
4. **Templates**: Edit `open_webui_config/medical_*.json`

### Testing Integration

```bash
# Test API bridge
python -m pytest backend/tests/test_openwebui_integration.py

# Test frontend integration
cd frontend && npm test

# Test security measures
python -m pytest security_config/test_validation.py
```

### Hot Reloading

- **FastAPI**: Automatically reloads on file changes
- **React**: Hot reloading with Vite
- **Open WebUI**: Restart container for config changes

---

## 📈 Production Deployment

### Security Checklist

- [ ] Change default secret keys
- [ ] Use strong database passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up proper firewall rules
- [ ] Configure backup strategies
- [ ] Monitor security logs
- [ ] Regular security updates

### Performance Optimization

- [ ] Use production Docker images
- [ ] Configure database connection pooling
- [ ] Set up Redis for session management
- [ ] Enable gzip compression
- [ ] Configure CDN for static assets

### Monitoring

- [ ] Set up health check endpoints
- [ ] Configure log aggregation
- [ ] Monitor API response times
- [ ] Track authentication failures
- [ ] Alert on security events

---

## 🤝 Support

### Getting Help

1. **Documentation**: Check this guide and `README.md`
2. **API Docs**: http://localhost:8000/docs
3. **Logs**: Check service logs for error details
4. **Issues**: Report integration issues with detailed logs

### Contributing

1. Fork the repository
2. Create feature branch
3. Test integration thoroughly
4. Submit pull request with documentation updates

---

## 📋 Appendix

### Service URLs

| Service | Development | Production |
|---------|-------------|------------|
| React Frontend | http://localhost:5173 | http://localhost |
| Open WebUI | http://localhost:3000 | http://localhost/webui |
| FastAPI Backend | http://localhost:8000 | http://localhost/api |
| PostgreSQL | localhost:5432 | localhost:5432 |
| pgAdmin | http://localhost:5050 | N/A |

### Default Ports

- React (Vite): 5173
- Open WebUI: 3000
- FastAPI: 8000
- PostgreSQL: 5432
- pgAdmin: 5050
- Nginx: 80, 443

### File Structure

```
workspace/
├── backend/
│   └── app/api/v1/
│       ├── openwebui.py         # Open WebUI integration
│       └── auth_bridge.py       # Authentication bridge
├── frontend/src/pages/
│   └── AIInterface.tsx          # React integration
├── open_webui_config/           # Open WebUI configurations
├── security_config/             # Security measures
├── nginx/                       # Reverse proxy config
├── docker-compose.yml           # Service orchestration
└── start-medical-ai.sh         # Startup script
```