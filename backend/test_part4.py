import requests

print("Testing Part 4: User Authentication")
print("=" * 50)

base_url = "http://localhost:8000"

print("\n1. Testing GET / without authentication (should redirect)")
try:
    response = requests.get(f"{base_url}/", allow_redirects=False)
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 302
    assert response.headers.get('location') == '/login'
    print("   ✓ PASSED - Redirects to login when not authenticated")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n2. Testing GET /login (login page)")
try:
    response = requests.get(f"{base_url}/login")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text
    assert "Sign in" in response.text
    print("   ✓ PASSED - Login page displays")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n3. Testing POST /api/auth/login with invalid credentials")
try:
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "wrong", "password": "wrong"}
    )
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False
    print("   ✓ PASSED - Invalid credentials rejected")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n4. Testing POST /api/auth/login with correct credentials")
try:
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "user", "password": "password"}
    )
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["username"] == "user"
    assert "session_token" in response.cookies
    session_token = response.cookies["session_token"]
    print("   ✓ PASSED - Login successful with session token")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    session_token = None

if session_token:
    print("\n5. Testing GET /api/auth/session with valid session")
    try:
        response = requests.get(
            f"{base_url}/api/auth/session",
            cookies={"session_token": session_token}
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] == True
        assert data["username"] == "user"
        print("   ✓ PASSED - Session is valid")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print("\n6. Testing GET / with valid session (should show Kanban)")
    try:
        response = requests.get(
            f"{base_url}/",
            cookies={"session_token": session_token}
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        assert "Kanban Studio" in response.text
        print("   ✓ PASSED - Kanban board accessible when authenticated")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print("\n7. Testing POST /api/auth/logout")
    try:
        response = requests.post(
            f"{base_url}/api/auth/logout",
            cookies={"session_token": session_token}
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("   ✓ PASSED - Logout successful")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print("\n8. Testing GET /api/auth/session after logout")
    try:
        response = requests.get(
            f"{base_url}/api/auth/session",
            cookies={"session_token": session_token}
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 401
        data = response.json()
        assert data["authenticated"] == False
        print("   ✓ PASSED - Session invalidated after logout")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

print("\n9. Testing GET /api/auth/session without session token")
try:
    response = requests.get(f"{base_url}/api/auth/session")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 401
    print("   ✓ PASSED - Unauthenticated request returns 401")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 50)
print("Part 4 tests completed!")
