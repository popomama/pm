import requests

r = requests.post('http://localhost:8000/api/auth/login', json={'username': 'user', 'password': 'password'})
print(f"Status: {r.status_code}")
print(f"JSON: {r.json()}")
print(f"\nAll headers:")
for key, value in r.headers.items():
    print(f"  {key}: {value}")
print(f"\nCookies object: {r.cookies}")
print(f"Cookies dict: {dict(r.cookies)}")
print(f"\nRaw cookies: {r.cookies._cookies}")
