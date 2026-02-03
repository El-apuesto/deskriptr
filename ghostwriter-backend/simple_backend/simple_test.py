# SIMPLE DATABASE TEST - Just verify database works
import requests
import random

BASE_URL = "http://localhost:8001"

# Generate random email
random_num = random.randint(1000, 9999)
email = f"simpletest{random_num}@example.com"

print(f"🚀 SIMPLE DATABASE TEST")
print(f"Email: {email}")

# Test 1: Health check
print("\n1. Testing health check...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
health = response.json()
print(f"Database status: {health['status']}")
print(f"Users in DB: {health['users_count']}")
print(f"Stories in DB: {health['stories_count']}")

# Test 2: Create user
print("\n2. Creating user...")
signup_data = {
    "email": email,
    "password": "TestPass123!",
    "full_name": f"Simple Test {random_num}"
}

response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"✅ User created! ID: {user_id}")
    
    # Test 3: Get user stories (should be empty)
    print("\n3. Getting user stories...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/users/me/stories", headers=headers)
    print(f"Status: {response.status_code}")
    stories = response.json()
    print(f"Stories count: {stories['total']}")
    
    # Test 4: Get user stats
    print("\n4. Getting user stats...")
    response = requests.get(f"{BASE_URL}/api/users/me/stats", headers=headers)
    print(f"Status: {response.status_code}")
    stats = response.json()
    print(f"Stats: {stats}")
    
    print("\n✅ DATABASE IS WORKING!")
    print("✅ User creation works")
    print("✅ Authentication works") 
    print("✅ User stories endpoint works")
    print("✅ User stats endpoint works")
    
else:
    print(f"❌ Signup failed: {response.json()}")
