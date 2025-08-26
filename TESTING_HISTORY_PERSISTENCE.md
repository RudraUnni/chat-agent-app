# Testing History Persistence

## Summary

**Yes, you need to create a dummy user to test history persistence** because:

1. The `Conversation` model has a **non-nullable foreign key** to `User`
2. PostgreSQL enforces this constraint and will reject conversation creation without a valid user
3. The current WebSocket implementation has been updated to handle user authentication properly

## Database Schema Requirements

```sql
-- Conversations REQUIRE a valid user_id
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),  -- ← NOT NULL constraint!
    title VARCHAR(200),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Quick Test Setup

### 1. Start the Backend
```bash
cd backend
python -m app.main
```

### 2. Create a Dummy User
```bash
# Create a dummy user via API
curl -X POST http://localhost:8000/api/v1/users/dummy

# Or create a custom user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'
```

### 3. Run the Automated Test
```bash
python test_history_persistence.py
```

This will:
- ✅ Create a dummy user
- ✅ Start a WebSocket conversation with that user
- ✅ Send multiple medical research questions
- ✅ Verify the conversation persists in the database

### 4. Manual WebSocket Test

Connect to WebSocket with user_id:
```
ws://localhost:8000/ws/chat/{conversation_id}?user_id={user_id}
```

Example with real IDs:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/123e4567-e89b-12d3-a456-426614174000?user_id=987fcdeb-51a2-43d1-9f4e-123456789abc');
```

## Verification

### Check Database Directly
```sql
-- List all users
SELECT id, username, email, created_at FROM users;

-- List conversations for a user
SELECT id, user_id, title, created_at FROM conversations WHERE user_id = 'your-user-id';

-- List messages in a conversation
SELECT role, content, sequence_number, created_at 
FROM messages 
WHERE conversation_id = 'your-conversation-id'
ORDER BY sequence_number;
```

### Check via API
```bash
# List all users
curl http://localhost:8000/api/v1/users/

# List active sessions
curl http://localhost:8000/api/v1/chat/sessions
```

## Updated WebSocket Endpoints

The WebSocket implementation now supports:

1. **Basic chat**: `ws://localhost:8000/ws/chat?user_id={user_id}`
2. **Specific conversation**: `ws://localhost:8000/ws/chat/{conversation_id}?user_id={user_id}`

Both require a valid `user_id` for history persistence to work.

## Error Handling

If you try to chat without a valid user_id:
- ❌ Conversation creation will fail
- ⚠️ Chat will continue in memory-only mode (no persistence)
- 📝 Logs will show: "Cannot create conversation without user_id"

## Implementation Changes Made

1. **Added user management endpoints** (`/api/v1/users/`)
2. **Updated WebSocket to accept user_id parameter**
3. **Added proper UUID conversion** for user_id and conversation_id
4. **Enhanced error handling** when user_id is missing
5. **Created automated test script** for easy verification

The backend now properly enforces the database schema while providing clear feedback when persistence requirements aren't met.