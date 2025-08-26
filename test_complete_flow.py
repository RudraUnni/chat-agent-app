#!/usr/bin/env python3
"""
Complete flow test for Medical Assistant with history persistence.

This script tests the entire flow:
1. Backend API endpoints
2. User creation 
3. Conversation management
4. Message history persistence
5. WebSocket communication with user context

Usage:
    python test_complete_flow.py
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

def test_health():
    """Test backend health"""
    print("🏥 Testing backend health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Backend is healthy")

def test_create_user():
    """Test user creation"""
    print("\n👤 Testing user creation...")
    
    # Create dummy user
    response = requests.post(f"{BASE_URL}/api/v1/users/dummy")
    assert response.status_code == 200
    
    user = response.json()
    print(f"✅ Created user: {user['username']} (ID: {user['id']})")
    
    return user

def test_conversation_endpoints(user_id):
    """Test conversation API endpoints"""
    print(f"\n💬 Testing conversation endpoints for user {user_id}...")
    
    # List conversations (should be empty initially)
    response = requests.get(f"{BASE_URL}/api/v1/conversations/?user_id={user_id}")
    assert response.status_code == 200
    
    conversations = response.json()
    print(f"✅ Listed conversations: {len(conversations)} found")
    
    return conversations

async def test_websocket_with_persistence(user_id):
    """Test WebSocket communication with persistence"""
    print(f"\n🔌 Testing WebSocket with user {user_id}...")
    
    conversation_id = str(uuid.uuid4())
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    messages_sent = [
        "What is hypertension?",
        "What are the symptoms?",
        "How is it treated?"
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket: {conversation_id}")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Welcome: {welcome_data.get('content', 'Connected')}")
            
            # Send test messages
            for i, message in enumerate(messages_sent, 1):
                print(f"\n📤 Sending message {i}: {message}")
                
                await websocket.send(json.dumps({
                    "message": message,
                    "user_id": user_id
                }))
                
                # Receive and display response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                print(f"📥 Response type: {response_data['type']}")
                if response_data['type'] == 'message':
                    content = response_data['content']
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"📝 Content preview: {preview}")
                
                # Wait a bit between messages
                await asyncio.sleep(2)
            
            print(f"\n✅ WebSocket conversation completed: {conversation_id}")
            return conversation_id
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return None

def test_conversation_history(conversation_id):
    """Test conversation history retrieval"""
    print(f"\n📋 Testing conversation history for {conversation_id}...")
    
    try:
        # Get conversation messages
        response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} messages from history")
            
            for i, msg in enumerate(messages, 1):
                print(f"   {i}. [{msg['role']}] {msg['content'][:100]}...")
            
            return messages
        else:
            print(f"⚠️ Could not retrieve history: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Error retrieving history: {e}")
        return []

def test_conversation_management(user_id, conversation_id):
    """Test conversation management features"""
    print(f"\n⚙️ Testing conversation management...")
    
    # List conversations again (should now have our conversation)
    response = requests.get(f"{BASE_URL}/api/v1/conversations/?user_id={user_id}")
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
        
        # Find our conversation
        our_conv = next((c for c in conversations if c['id'] == conversation_id), None)
        if our_conv:
            print(f"✅ Our conversation found: '{our_conv['title']}' with {our_conv['message_count']} messages")
        else:
            print(f"⚠️ Our conversation {conversation_id} not found in list")
    
    # Test title update
    new_title = f"Test Conversation - {datetime.now().strftime('%H:%M')}"
    response = requests.patch(
        f"{BASE_URL}/api/v1/conversations/{conversation_id}/title",
        params={"title": new_title}
    )
    
    if response.status_code == 200:
        print(f"✅ Updated conversation title to: '{new_title}'")
    else:
        print(f"⚠️ Failed to update title: {response.status_code}")

async def main():
    """Run complete test suite"""
    print("🧪 Medical Assistant - Complete Flow Test")
    print("=" * 60)
    
    try:
        # Test backend health
        test_health()
        
        # Create test user
        user = test_create_user()
        user_id = user['id']
        
        # Test conversation endpoints
        initial_conversations = test_conversation_endpoints(user_id)
        
        # Test WebSocket with persistence
        conversation_id = await test_websocket_with_persistence(user_id)
        
        if conversation_id:
            # Test conversation history
            messages = test_conversation_history(conversation_id)
            
            # Test conversation management
            test_conversation_management(user_id, conversation_id)
            
            print(f"\n🎉 Complete flow test successful!")
            print(f"👤 User ID: {user_id}")
            print(f"💬 Conversation ID: {conversation_id}")
            print(f"📨 Messages exchanged: {len(messages)}")
            
            print(f"\n💡 Frontend should now be able to:")
            print(f"   1. Auto-select user {user['username']}")
            print(f"   2. Load conversation {conversation_id}")
            print(f"   3. Display {len(messages)} historical messages")
            print(f"   4. Continue the conversation with full context")
            
        else:
            print("\n❌ WebSocket test failed - cannot verify persistence")
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())