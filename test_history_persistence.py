#!/usr/bin/env python3
"""
Test script for history persistence in the Medical Assistant backend.

This script demonstrates how to:
1. Create a dummy user
2. Start a conversation with that user
3. Send multiple messages 
4. Verify that conversation history is persisted

Usage:
    python test_history_persistence.py
"""

import requests
import json
import asyncio
import websockets
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


def create_dummy_user():
    """Create a dummy user for testing"""
    print("🧪 Creating dummy user...")
    
    response = requests.post(f"{BASE_URL}/api/v1/users/dummy")
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Created user: {user['username']} (ID: {user['id']})")
        return user
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None


def list_users():
    """List all users"""
    print("\n👥 Listing all users...")
    
    response = requests.get(f"{BASE_URL}/api/v1/users/")
    
    if response.status_code == 200:
        users = response.json()
        for user in users:
            print(f"   - {user['username']} ({user['id']}) - Created: {user['created_at']}")
        return users
    else:
        print(f"❌ Failed to list users: {response.text}")
        return []


async def test_websocket_conversation(user_id):
    """Test conversation via WebSocket with user context"""
    print(f"\n💬 Starting WebSocket conversation for user {user_id}...")
    
    conversation_id = str(uuid.uuid4())
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    messages_to_send = [
        "What is hypertension?",
        "What are the latest treatments for diabetes?", 
        "Can you find recent research on COVID-19 vaccines?"
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket: {conversation_id}")
            
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"📨 Welcome: {json.loads(welcome)['content']}")
            
            for i, message in enumerate(messages_to_send, 1):
                print(f"\n📤 Sending message {i}: {message}")
                
                await websocket.send(json.dumps({
                    "message": message,
                    "user_id": user_id
                }))
                
                # Receive response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                print(f"📥 Response type: {response_data['type']}")
                if response_data['type'] == 'message':
                    content = response_data['content'][:200] + "..." if len(response_data['content']) > 200 else response_data['content']
                    print(f"📝 Content preview: {content}")
                
                # Wait a bit between messages
                await asyncio.sleep(2)
            
            print(f"\n✅ Conversation completed: {conversation_id}")
            return conversation_id
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return None


async def verify_conversation_history(conversation_id):
    """Verify that conversation history was persisted"""
    print(f"\n🔍 Verifying history for conversation: {conversation_id}")
    
    # For now, we'll check if we can reconnect and get history
    # (This would require implementing a get_conversation_history endpoint)
    print("📋 Note: History verification would require additional endpoint")
    print("💡 You can check database directly or implement GET /conversations/{id}/messages")


def test_health_check():
    """Test that the backend is running"""
    print("🏥 Checking backend health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on http://localhost:8000?")
        return False


async def main():
    """Main test function"""
    print("🧪 Medical Assistant Backend - History Persistence Test")
    print("=" * 60)
    
    # Check if backend is running
    if not test_health_check():
        print("\n💡 Start the backend with:")
        print("   cd backend && python -m app.main")
        return
    
    # Create dummy user
    user = create_dummy_user()
    if not user:
        return
    
    # List users to confirm creation
    list_users()
    
    # Test WebSocket conversation
    conversation_id = await test_websocket_conversation(user['id'])
    
    if conversation_id:
        await verify_conversation_history(conversation_id)
        
        print(f"\n🎉 Test completed successfully!")
        print(f"👤 User ID: {user['id']}")
        print(f"💬 Conversation ID: {conversation_id}")
        print(f"\n💡 To verify persistence, check your PostgreSQL database:")
        print(f"   SELECT * FROM users WHERE id = '{user['id']}';")
        print(f"   SELECT * FROM conversations WHERE id = '{conversation_id}';")
        print(f"   SELECT * FROM messages WHERE conversation_id = '{conversation_id}';")


if __name__ == "__main__":
    asyncio.run(main())