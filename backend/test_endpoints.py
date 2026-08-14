import requests

print("Testing Kanban Studio Backend Endpoints")
print("=" * 50)

base_url = "http://localhost:8000"

print("\n1. Testing GET /api/health")
try:
    response = requests.get(f"{base_url}/api/health")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("   ✓ PASSED")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n2. Testing GET /test")
try:
    response = requests.get(f"{base_url}/test")
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    assert response.status_code == 200
    assert "text/html" in response.headers.get('content-type', '')
    assert "Hello World" in response.text
    print("   ✓ PASSED")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 50)
print("All tests completed!")
