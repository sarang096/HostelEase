import requests

# Test login endpoint
url = 'http://localhost:3000/api/login'

# Try logging in with a test user
test_credentials = [
    {'username': 'student3', 'password': 'test'},
    {'username': 'sarang', 'password': 'test'},
    {'username': 'shreehari', 'password': 'test'},
]

print("Testing login endpoint...\n")

for cred in test_credentials:
    print(f"Trying: {cred['username']} / {cred['password']}")
    try:
        response = requests.post(
            url,
            json=cred,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"  ✓ Login successful!")
            break
        else:
            print(f"  ✗ Login failed")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()

print("\nTo see what credentials exist in the database, run:")
print("  SELECT username, password, role FROM login;")
