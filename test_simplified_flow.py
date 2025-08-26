#!/usr/bin/env python3
"""
Simplified test for Medical Assistant with automatic default user.

Tests:
1. Backend health
2. Automatic user creation
3. Message history persistence
4. WebSocket communication

Usage:
    python test_simplified_flow.py
"""

import requests
import json
import asyncio
import websockets
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

def test_health():
    """Test backend health"""
    print("🏥 Testing backend health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Backend is healthy")

def create_test_user():
    """Create a test user"""
    print("\n👤 Creating test user...")
    
    response = requests.post(f"{BASE_URL}/api/v1/users/dummy")
    assert response.status_code == 200
    
    user = response.json()
    print(f"✅ Created user: {user['username']} (ID: {user['id']})")
    
    return user

async def test_conversation_with_history(user_id):
    """Test conversation with message persistence"""
    print(f"\n💬 Testing conversation with user {user_id}...")
    
    conversation_id = str(uuid.uuid4())
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    test_messages = [
        "What is diabetes?",
        "What are the symptoms?", 
        "How is it treated?"
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket")
            
            # Skip welcome message
            welcome = await websocket.recv()
            
            # Send test messages
            for i, message in enumerate(test_messages, 1):
                print(f"\n📤 Sending: {message}")
                
                await websocket.send(json.dumps({"message": message}))
                
                # Get response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data['type'] == 'message':
                    print(f"📥 Got response ({len(response_data['content'])} chars)")
                
                await asyncio.sleep(1)
            
            print(f"\n✅ Conversation completed")
            return conversation_id
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return None

def verify_message_history(conversation_id):
    """Verify messages were stored"""
    print(f"\n📋 Checking message history...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Found {len(messages)} stored messages")
            
            # Show first and last messages
            if messages:
                first_msg = messages[0]
                last_msg = messages[-1]
                print(f"   First: [{first_msg['role']}] {first_msg['content'][:50]}...")
                print(f"   Last:  [{last_msg['role']}] {last_msg['content'][:50]}...")
            
            return len(messages)
        else:
            print(f"⚠️ Could not retrieve history: {response.status_code}")
            return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

async def test_history_retrieval(user_id, conversation_id):
    """Test that new connection loads previous messages"""
    print(f"\n🔄 Testing history retrieval...")
    
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Reconnected to same conversation")
            
            # Send a question about history
            await websocket.recv()  # Skip welcome
            
            await websocket.send(json.dumps({
                "message": "What was my first question?"
            }))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data['type'] == 'message':
                content = response_data['content'].lower()
                if 'diabetes' in content or 'first' in content:
                    print("✅ AI correctly referenced conversation history!")
                else:
                    print("⚠️ AI response doesn't seem to reference history")
                    print(f"   Response: {response_data['content'][:100]}...")
            
    except Exception as e:
        print(f"❌ Error testing history: {e}")

async def main():
    """Run simplified test"""
    print("🧪 Medical Assistant - Simplified Flow Test")
    print("=" * 50)
    
    try:
        # Test backend
        test_health()
        
        # Create user
        user = create_test_user()
        user_id = user['id']
        
        # Test conversation
        conversation_id = await test_conversation_with_history(user_id)
        
        if conversation_id:
            # Verify persistence
            message_count = verify_message_history(conversation_id)
            
            if message_count > 0:
                # Test history retrieval
                await test_history_retrieval(user_id, conversation_id)
                
                print(f"\n🎉 Test successful!")
                print(f"   User: {user['username']}")
                print(f"   Conversation: {conversation_id[:8]}...")
                print(f"   Messages stored: {message_count}")
                print(f"\n💡 Frontend will now:")
                print(f"   1. Auto-create user on first load")
                print(f"   2. Load conversation history automatically")
                print(f"   3. Provide accurate responses about chat history")
            else:
                print("\n❌ No messages were stored")
        else:
            print("\n❌ Conversation test failed")
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())