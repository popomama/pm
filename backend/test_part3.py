import requests

print("Testing Part 3: Frontend Integration")
print("=" * 50)

base_url = "http://localhost:8000"

print("\n1. Testing GET / (Frontend)")
try:
    response = requests.get(f"{base_url}/")
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    assert response.status_code == 200
    assert "text/html" in response.headers.get('content-type', '')
    assert "Kanban Studio" in response.text
    print("   ✓ PASSED - Frontend is served")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n2. Testing GET /api/health (API still works)")
try:
    response = requests.get(f"{base_url}/api/health")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("   ✓ PASSED - API endpoints still functional")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n3. Testing GET /test (Test page still works)")
try:
    response = requests.get(f"{base_url}/test")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    assert "Hello World" in response.text
    print("   ✓ PASSED - Test endpoint still works")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 50)
print("Part 3 tests completed!")
