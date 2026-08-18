import requests

# First login
login_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'user', 'password': 'password'}
)
print(f"Login Status: {login_response.status_code}")

# Get the session cookie
cookies = login_response.cookies

# Test creating a board
try:
    create_response = requests.post(
        'http://localhost:8000/api/boards',
        json={'title': 'Test Board', 'template_name': 'default'},
        cookies=cookies
    )
    print(f"\nCreate Board Status: {create_response.status_code}")
    print(f"Response: {create_response.text}")
except Exception as e:
    print(f"Error: {e}")

# List boards
try:
    boards_response = requests.get(
        'http://localhost:8000/api/boards',
        cookies=cookies
    )
    print(f"\nList Boards Status: {boards_response.status_code}")
    print(f"Response: {boards_response.text}")
except Exception as e:
    print(f"Error: {e}")
