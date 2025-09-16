#!/usr/bin/env python3
"""
Quick integration test script for OpenWebUI + FastAPI + OpenRouter setup
"""
import asyncio
import httpx
import json

async def test_backend_health():
    """Test backend health endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            print(f"✅ Backend Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Backend Health: {e}")

async def test_models_endpoint():
    """Test OpenAI-compatible models endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/v1/models")
            models = response.json()
            print(f"✅ Models Endpoint: {response.status_code}")
            for model in models.get('data', []):
                print(f"   - {model['id']}")
    except Exception as e:
        print(f"❌ Models Endpoint: {e}")

async def test_chat_completions():
    """Test OpenAI-compatible chat completions"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": "What is diabetes?"}
                ],
                "max_tokens": 50
            }
            response = await client.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                timeout=30.0
            )
            print(f"✅ Chat Completions: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"   Response: {content[:100]}...")
            else:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat Completions: {e}")

async def main():
    print("🧪 Testing OpenWebUI + FastAPI + OpenRouter Integration")
    print("=" * 60)
    
    await test_backend_health()
    await test_models_endpoint()
    await test_chat_completions()
    
    print("\n🎯 Next Steps:")
    print("1. Start services: docker-compose up -d")
    print("2. Access OpenWebUI: http://localhost:3001")
    print("3. Test with a medical question!")

if __name__ == "__main__":
    asyncio.run(main())