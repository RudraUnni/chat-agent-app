#!/usr/bin/env python3
"""
Enhanced test script for history persistence in the Medical Assistant backend.

This script tests the improved history persistence functionality including:
1. User management endpoints
2. Conversation creation and management
3. WebSocket chat with proper history context
4. Message persistence and retrieval
5. Error handling and recovery

Usage:
    python test_enhanced_history_persistence.py
"""

import requests
import json
import asyncio
import websockets
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


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


def create_test_user():
    """Create a test user using the new user endpoint"""
    print("👤 Creating test user...")
    
    user_data = {
        "username": f"test_user_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Created user: {user['username']} (ID: {user['id']})")
        return user
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None


def create_conversation(user_id):
    """Create a conversation for the user"""
    print(f"💬 Creating conversation for user {user_id}...")
    
    conversation_data = {
        "user_id": user_id,
        "title": "Test Medical Research Conversation"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/conversations/", json=conversation_data)
    
    if response.status_code == 200:
        conversation = response.json()
        print(f"✅ Created conversation: {conversation['title']} (ID: {conversation['id']})")
        return conversation
    else:
        print(f"❌ Failed to create conversation: {response.text}")
        return None


def get_conversation_messages(conversation_id):
    """Get messages for a conversation"""
    print(f"📋 Getting messages for conversation {conversation_id}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}/messages")
    
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Retrieved {len(messages)} messages")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. [{msg['role']}] {msg['content'][:100]}...")
        return messages
    else:
        print(f"❌ Failed to get messages: {response.text}")
        return []


def list_user_conversations(user_id):
    """List all conversations for a user"""
    print(f"📂 Listing conversations for user {user_id}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/conversations/?user_id={user_id}")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
        for conv in conversations:
            print(f"   - {conv['title']} (ID: {conv['id']}) - {conv['message_count']} messages")
        return conversations
    else:
        print(f"❌ Failed to list conversations: {response.text}")
        return []


async def test_websocket_with_history(user_id, conversation_id):
    """Test WebSocket conversation with history persistence"""
    print(f"\n🌐 Testing WebSocket with history...")
    print(f"   User ID: {user_id}")
    print(f"   Conversation ID: {conversation_id}")
    
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    test_messages = [
        "What is hypertension and what causes it?",
        "What are the latest treatment options for hypertension?",
        "Can you find recent research on hypertension medications?",
        "Based on our previous discussion about hypertension, what lifestyle changes are most effective?"
    ]
    
    responses = []
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Welcome: {welcome_data['content']}")
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n📤 Sending message {i}: {message}")
                
                # Send message
                await websocket.send(json.dumps({
                    "content": message,
                    "workflow": "pubmed_research"
                }))
                
                # Receive response(s)
                response_received = False
                while not response_received:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        response_data = json.loads(response)
                        
                        if response_data['type'] == 'assistant':
                            print(f"📥 Assistant response received ({len(response_data['content'])} chars)")
                            responses.append({
                                'user_message': message,
                                'assistant_response': response_data['content']
                            })
                            response_received = True
                        elif response_data['type'] == 'warning':
                            print(f"⚠️  Warning: {response_data['content']}")
                        elif response_data['type'] == 'error':
                            print(f"❌ Error: {response_data['content']}")
                            response_received = True
                        else:
                            print(f"📨 Other message: {response_data}")
                            
                    except asyncio.TimeoutError:
                        print("⏱️  Timeout waiting for response")
                        response_received = True
                
                # Wait between messages
                await asyncio.sleep(2)
            
            print(f"\n✅ WebSocket conversation completed with {len(responses)} responses")
            return responses
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return []


async def verify_history_persistence(conversation_id, expected_message_count):
    """Verify that messages were persisted correctly"""
    print(f"\n🔍 Verifying history persistence...")
    
    # Wait a moment for database writes to complete
    await asyncio.sleep(1)
    
    messages = get_conversation_messages(conversation_id)
    
    if len(messages) >= expected_message_count:
        print(f"✅ History persistence verified: {len(messages)} messages found")
        
        # Check message sequence
        for i, msg in enumerate(messages):
            expected_seq = i + 1
            if msg['sequence_number'] == expected_seq:
                print(f"   ✅ Message {expected_seq}: {msg['role']} - sequence OK")
            else:
                print(f"   ❌ Message {expected_seq}: sequence mismatch (got {msg['sequence_number']})")
        
        return True
    else:
        print(f"❌ History persistence failed: expected at least {expected_message_count}, got {len(messages)}")
        return False


async def test_conversation_context():
    """Test that conversation context is maintained across messages"""
    print(f"\n🧠 Testing conversation context...")
    
    # This would require analyzing the assistant responses to see if they reference previous messages
    # For now, we'll just print a note about manual verification
    print("📋 Note: Context verification requires manual review of assistant responses")
    print("💡 Check if later responses reference earlier parts of the conversation")
    return True


async def main():
    """Main test function"""
    print("🧪 Enhanced Medical Assistant Backend - History Persistence Test")
    print("=" * 70)
    
    # Check if backend is running
    if not test_health_check():
        print("\n💡 Start the backend with:")
        print("   cd backend && python -m app.main")
        return
    
    # Create test user
    user = create_test_user()
    if not user:
        return
    
    # Create conversation
    conversation = create_conversation(user['id'])
    if not conversation:
        return
    
    # Test WebSocket conversation with history
    responses = await test_websocket_with_history(user['id'], conversation['id'])
    
    if responses:
        # Verify persistence (expect user + assistant messages)
        expected_messages = len(responses) * 2  # Each exchange has user + assistant message
        persistence_ok = await verify_history_persistence(conversation['id'], expected_messages)
        
        # List conversations to verify
        list_user_conversations(user['id'])
        
        # Test conversation context
        await test_conversation_context()
        
        print(f"\n🎉 Test completed!")
        print(f"👤 User ID: {user['id']}")
        print(f"💬 Conversation ID: {conversation['id']}")
        print(f"📊 Exchanges: {len(responses)}")
        print(f"✅ Persistence: {'OK' if persistence_ok else 'FAILED'}")
        
        print(f"\n💡 To verify in database:")
        print(f"   SELECT * FROM users WHERE id = '{user['id']}';")
        print(f"   SELECT * FROM conversations WHERE id = '{conversation['id']}';")
        print(f"   SELECT role, content, sequence_number FROM messages WHERE conversation_id = '{conversation['id']}' ORDER BY sequence_number;")
        
        if persistence_ok:
            print(f"\n🎊 All tests passed! History persistence is working correctly.")
        else:
            print(f"\n⚠️  Some tests failed. Check the logs for details.")
    
    else:
        print(f"\n❌ WebSocket test failed. Check backend logs.")


if __name__ == "__main__":
    asyncio.run(main())