# FINAL TEST - Verify everything works
import requests
import random

BASE_URL = "http://localhost:8001"

# Generate random email
random_num = random.randint(1000, 9999)
email = f"testuser{random_num}@example.com"

print(f"🚀 TESTING WITH EMAIL: {email}")

# Create new user
signup_data = {
    "email": email,
    "password": "TestPass123!",
    "full_name": f"Test User {random_num}"
}

print("\n1. Creating user...")
response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ User created successfully!")
    print(f"User ID: {response.json()['user']['id']}")
    
    # Test story generation
    print("\n2. Testing story generation...")
    headers = {"Authorization": f"Bearer {token}"}
    
    story_data = {
        "plot": "A wizard discovers a magical portal to another dimension",
        "when_where": "Ancient library, midnight",
        "characters": "Wizard Merlin, apprentice Arthur",
        "genre": "fantasy",
        "writing_style": "J.K. Rowling",
        "timeline": "1. Discovery 2. Portal opens 3. Adventure begins",
        "title": "The Portal Discovery",
        "author_name": f"Test User {random_num}"
    }
    
    response = requests.post(f"{BASE_URL}/api/stories/generate", json=story_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Story generated successfully!")
        print(f"Story ID: {data['id']}")
        print(f"Title: {data['title']}")
        print(f"Content length: {len(data['content'])} characters")
        print(f"Content preview: {data['content'][:200]}...")
        
        # Test getting user stories
        print("\n3. Testing get user stories...")
        response = requests.get(f"{BASE_URL}/api/users/me/stories", headers=headers)
        print(f"Status: {response.status_code}")
        stories = response.json()
        print(f"✅ Found {stories['total']} stories")
        
        # Test getting user stats
        print("\n4. Testing user stats...")
        response = requests.get(f"{BASE_URL}/api/users/me/stats", headers=headers)
        print(f"Status: {response.status_code}")
        stats = response.json()
        print(f"✅ User stats:")
        print(f"   Stories: {stats.get('stories_count', 0)}")
        print(f"   Words: {stats.get('total_words', 0)}")
        print(f"   Tier: {stats.get('subscription_tier', 'free')}")
        
        print("\n🎉 ALL TESTS PASSED! YOUR DATABASE IS WORKING!")
        
    else:
        print(f"❌ Story generation failed: {response.json()}")
else:
    print(f"❌ Signup failed: {response.json()}")
