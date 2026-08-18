import requests
import json

try:
    response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'username': 'user', 'password': 'password'},
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Headers: {dict(response.headers)}")
except Exception as e:
    print(f"Error: {e}")
