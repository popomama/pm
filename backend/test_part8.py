import requests
import time

print("Testing Part 8: AI Connectivity Setup")
print("=" * 50)

base_url = "http://localhost:8000"
session = requests.Session()

print("\n1. Login to get session")
try:
    login_response = session.post(
        f"{base_url}/api/auth/login",
        json={"username": "user", "password": "password"}
    )
    assert login_response.status_code == 200
    print(f"   ✓ PASSED - Logged in successfully")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

print("\n2. Testing POST /api/ai/test (AI connectivity)")
try:
    start_time = time.time()
    response = session.post(f"{base_url}/api/ai/test")
    elapsed_time = time.time() - start_time
    
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Model: {data.get('model')}")
    print(f"   Question: {data.get('question')}")
    print(f"   Response: {data.get('response')[:100]}..." if len(data.get('response', '')) > 100 else f"   Response: {data.get('response')}")
    print(f"   Response time: {elapsed_time:.2f} seconds")
    
    assert data.get('success') == True
    assert data.get('model') == 'gpt-oss-120b'
    assert data.get('question') == 'What is 2+2?'
    assert data.get('response') is not None
    assert len(data.get('response')) > 0
    assert elapsed_time < 10  # Should respond within 10 seconds
    
    print(f"   ✓ PASSED - AI connectivity working")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    if response.status_code != 200:
        print(f"   Error details: {response.text}")

print("\n3. Testing POST /api/ai/test without authentication")
try:
    response = requests.post(f"{base_url}/api/ai/test")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 401
    print(f"   ✓ PASSED - Unauthorized access blocked")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 50)
print("Part 8 tests completed!")
print("\nAI Integration Summary:")
print("  - AI client connects to gpt-oss-120b model")
print("  - Authentication headers included")
print("  - Test query returns valid response")
print("  - Response time is reasonable")
print("  - Endpoint requires authentication")
