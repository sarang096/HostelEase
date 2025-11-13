import requests
import time

# Wait a moment for server to be ready
time.sleep(1)

# Test login endpoint
url = 'http://localhost:3000/api/login'
credentials = {'username': 'shreehari', 'password': 'pass123'}

print("Testing login with shreehari/pass123...")

try:
    response = requests.post(
        url,
        json=credentials,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ Login successful! The application is working correctly.")
    else:
        print("\n✗ Login failed")
except Exception as e:
    print(f"✗ Error: {e}")
