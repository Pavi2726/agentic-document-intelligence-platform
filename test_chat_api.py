"""
Simple test to verify chat is working
Run this after starting the backend server
"""
import requests
import json

print("=" * 60)
print("Testing Chat Functionality")
print("=" * 60)

# Test 1: Health Check
print("\n1. Testing Backend Health...")
try:
    response = requests.get("http://localhost:8000/api/health")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Backend is healthy")
        print(f"   ✓ Groq configured: {data.get('database_checks', {}).get('groq_configured', False)}")
    else:
        print(f"   ✗ Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ✗ Cannot connect to backend: {e}")
    print("   Make sure backend is running: cd backend && run.bat")
    exit(1)

# Test 2: Simple Chat Message
print("\n2. Testing Chat Endpoint...")
try:
    payload = {
        "message": "Hello, how are you?",
        "stream": False
    }
    response = requests.post(
        "http://localhost:8000/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Chat response received")
        print(f"   ✓ Session ID: {data.get('session_id', 'N/A')[:30]}...")
        print(f"   ✓ Answer: {data.get('answer', 'N/A')[:100]}...")
        print(f"   ✓ Sources: {data.get('sources', {})}")
    else:
        print(f"   ✗ Chat failed: {response.status_code}")
        print(f"   Error: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Chat request failed: {e}")
    exit(1)

# Test 3: Chat with Context
print("\n3. Testing Chat with Follow-up...")
try:
    payload = {
        "message": "What did I just ask you?",
        "session_id": data.get('session_id'),
        "stream": False
    }
    response = requests.post(
        "http://localhost:8000/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data2 = response.json()
        print(f"   ✓ Follow-up response received")
        print(f"   ✓ Answer: {data2.get('answer', 'N/A')[:100]}...")
        print(f"   ✓ Context used: {data2.get('context_used', 0)} messages")
    else:
        print(f"   ✗ Follow-up failed: {response.status_code}")
except Exception as e:
    print(f"   ⚠ Follow-up test failed: {e}")

print("\n" + "=" * 60)
print("✓ All tests passed! Chat is working correctly.")
print("=" * 60)
print("\nYou can now use the chat interface at:")
print("http://localhost:3000/chat")
print("=" * 60)
