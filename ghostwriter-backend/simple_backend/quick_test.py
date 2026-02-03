# QUICK TEST - CREATE NEW USER AND LOGIN
import requests
import json

BASE_URL = "http://localhost:8001"

# Create a new user with different email
signup_data = {
    "email": "newuser@example.com",
    "password": "TestPass123!",
    "full_name": "New Test User"
}

print("Creating new user...")
response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
print(f"Signup Status: {response.status_code}")
print(f"Signup Response: {response.json()}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Got token: {token[:30]}...")
    
    # Test story generation
    print("\nTesting story generation...")
    headers = {"Authorization": f"Bearer {token}"}
    
    story_data = {
        "plot": "A space adventure to Mars",
        "when_where": "Mars colony, 2150",
        "characters": "Commander Sarah, robot assistant",
        "genre": "scifi",
        "writing_style": "Arthur C. Clarke",
        "timeline": "1. Launch 2. Journey 3. Arrival",
        "title": "Mars Adventure"
    }
    
    response = requests.post(f"{BASE_URL}/api/stories/generate", json=story_data, headers=headers)
    print(f"Story Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Story created! ID: {data['id']}")
        print(f"Title: {data['title']}")
        print(f"Content preview: {data['content'][:100]}...")
    else:
        print(f"❌ Story generation failed: {response.json()}")
else:
    print("❌ Signup failed")
