import requests

# First login
login_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'user', 'password': 'password'}
)
print(f"Login Status: {login_response.status_code}")

# Get the session cookie
cookies = login_response.cookies

# Test /api/boards
try:
    boards_response = requests.get(
        'http://localhost:8000/api/boards?include_archived=false',
        cookies=cookies
    )
    print(f"\n/api/boards Status: {boards_response.status_code}")
    print(f"Response: {boards_response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test /api/board
try:
    board_response = requests.get(
        'http://localhost:8000/api/board',
        cookies=cookies
    )
    print(f"\n/api/board Status: {board_response.status_code}")
    print(f"Response: {board_response.text}")
except Exception as e:
    print(f"Error: {e}")
