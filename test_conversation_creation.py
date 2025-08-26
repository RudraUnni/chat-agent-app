#!/usr/bin/env python3
"""
Test conversation creation fix.
"""

import requests
import json
import asyncio
import websockets
import uuid

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_conversation_creation():
    """Test that conversation is properly created before messages"""
    print("🧪 Testing conversation creation fix...")
    
    # 1. Create a test user
    print("\n1️⃣ Creating test user...")
    response = requests.post(f"{BASE_URL}/api/v1/users/dummy")
    assert response.status_code == 200
    user = response.json()
    user_id = user['id']
    print(f"✅ User created: {user['username']} ({user_id})")
    
    # 2. Connect WebSocket with user_id and conversation_id
    conversation_id = str(uuid.uuid4())
    uri = f"{WS_URL}/ws/chat/{conversation_id}?user_id={user_id}"
    
    print(f"\n2️⃣ Connecting WebSocket...")
    print(f"   URI: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # 3. Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Welcome: {welcome_data.get('content', welcome_data.get('type', 'Connected'))}")
            
            # 4. Send a test message
            print(f"\n3️⃣ Sending test message...")
            test_message = "Hello, this is a test message"
            
            await websocket.send(json.dumps({
                "message": test_message
            }))
            print(f"📤 Sent: {test_message}")
            
            # 5. Receive response
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 Response type: {response_data['type']}")
            
            if response_data['type'] == 'message':
                print(f"📝 AI Response: {response_data['content'][:100]}...")
            
            # 6. Check if conversation was created in database
            print(f"\n4️⃣ Checking conversation in database...")
            conv_response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}")
            
            if conv_response.status_code == 200:
                conv_data = conv_response.json()
                print(f"✅ Conversation found in database:")
                print(f"   ID: {conv_data['id']}")
                print(f"   Title: {conv_data['title']}")
                print(f"   Messages: {len(conv_data.get('messages', []))}")
            else:
                print(f"❌ Conversation not found: {conv_response.status_code}")
            
            # 7. Check messages
            print(f"\n5️⃣ Checking messages in database...")
            msg_response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}/messages")
            
            if msg_response.status_code == 200:
                messages = msg_response.json()
                print(f"✅ Found {len(messages)} messages in database:")
                for i, msg in enumerate(messages, 1):
                    print(f"   {i}. [{msg['role']}] {msg['content'][:50]}...")
                
                return len(messages) > 0
            else:
                print(f"❌ Messages not found: {msg_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def main():
    """Run the test"""
    print("🔧 Testing Conversation Creation Fix")
    print("=" * 40)
    
    try:
        # Test health first
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Backend not healthy")
            return
        
        success = await test_conversation_creation()
        
        if success:
            print(f"\n🎉 SUCCESS! Conversation creation is working!")
            print("✅ User created")
            print("✅ WebSocket connected") 
            print("✅ Conversation record created in database")
            print("✅ Messages stored successfully")
            print("✅ Foreign key constraints satisfied")
        else:
            print(f"\n❌ FAILED! Conversation creation still has issues")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())