# Minimalistic Working Main - History Persistence

## 🎯 What You Have

Your backend **main.py** is now a **minimalistic working example** that demonstrates history persistence with a default user. No separate test files needed!

## 🚀 How to Run

1. **Start PostgreSQL:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Start the minimalistic backend:**
   ```bash
   cd backend
   python -m app.main
   ```

3. **See the magic happen:**
   ```
   🚀 STARTING MINIMALISTIC HISTORY PERSISTENCE BACKEND
   =======================================================
   📋 Default user: test_user
   📧 Default email: test@example.com
   🗃️ Database: chatapp_db
   =======================================================
   🌱 Database seeding completed. Default user ID: abc123...
   ✅ Database initialized with default user
   🎯 Ready for history persistence testing!
   💡 Test: curl http://localhost:8000/api/v1/users/default
   
   🔗 MINIMALISTIC HISTORY PERSISTENCE ENDPOINTS:
      GET  /                         - Root - shows backend info
      GET  /api/v1/users/default     - Get default test user
      GET  /api/v1/users/            - List all users
      POST /api/v1/users/dummy       - Create dummy user
      WS   /ws/chat                  - WebSocket chat with history
   🎯 Start testing with: curl http://localhost:8000/api/v1/users/default
   ```

## 🧪 Test the Working Main

1. **Root endpoint shows everything:**
   ```bash
   curl http://localhost:8000/
   ```
   
   Response:
   ```json
   {
     "message": "Minimalistic History Persistence Backend",
     "default_user": "test_user",
     "features": ["user_management", "history_persistence", "websocket_chat"],
     "endpoints": {
       "default_user": "/api/v1/users/default",
       "list_users": "/api/v1/users/",
       "websocket": "/ws/chat?user_id=<user_id>"
     }
   }
   ```

2. **Get the default user (created automatically):**
   ```bash
   curl http://localhost:8000/api/v1/users/default
   ```

3. **Use WebSocket with default user:**
   ```bash
   # Get user ID first
   USER_ID=$(curl -s http://localhost:8000/api/v1/users/default | jq -r '.id')
   
   # Connect to WebSocket
   # ws://localhost:8000/ws/chat?user_id=$USER_ID
   ```

## ✨ What Makes It Minimalistic

- **No separate test files** - main.py demonstrates everything
- **Automatic setup** - Default user created on startup
- **Clear feedback** - Shows exactly what's happening
- **Working endpoints** - Ready for immediate testing
- **One command start** - `python -m app.main` does everything

## 🗃️ History Persistence Features

- ✅ **Default user** created automatically (`test_user`)
- ✅ **Full database schema** (users → conversations → messages)
- ✅ **WebSocket chat** with persistent history
- ✅ **User management API** for testing
- ✅ **Error handling** and logging

## 🔧 Configuration

The minimalistic main uses these defaults:
- **Username:** `test_user`
- **Email:** `test@example.com`
- **Database:** `chatapp_db`
- **Auto-create:** `true`

Change via environment variables or `backend/app/core/config.py`.

---

**Your backend main.py is now a complete, minimalistic working example!** 🎉

Just run `python -m app.main` and you have a fully functional history persistence system with a default user, ready for testing.