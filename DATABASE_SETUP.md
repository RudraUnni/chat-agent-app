# Minimal PostgreSQL Database Setup

## Overview
Simple PostgreSQL database implementation for the chat application with three core tables:
- **users**: Basic user management
- **conversations**: Chat conversation containers  
- **messages**: Individual chat messages

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Quick Start

### 1. Start PostgreSQL Container
```bash
# Start PostgreSQL only
docker-compose up postgres -d

# Or start with pgAdmin for database management
docker-compose --profile dev up -d
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
# Start the backend - it will create tables automatically
uvicorn app.main:app --reload
```

### 4. Access Database
- **PostgreSQL**: localhost:5432
  - Database: `chatapp_db`
  - User: `chatapp`
  - Password: `chatapp_password`

- **pgAdmin** (optional): http://localhost:5050
  - Email: `admin@chatapp.local`
  - Password: `admin_password`

## File Structure
```
backend/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   └── connection.py    # Database connection
│   ├── core/
│   │   └── config.py        # Configuration
│   └── main.py             # Updated with database lifecycle
├── requirements.txt         # Updated with database dependencies
└── .env                    # Database configuration

docker-compose.yml          # PostgreSQL + pgAdmin containers
```

## Usage Example

```python
from app.database.connection import get_db
from app.database.models import User, Conversation, Message

# Create user
async with get_db() as db:
    user = User(username="john_doe", email="john@example.com")
    db.add(user)
    await db.commit()
```