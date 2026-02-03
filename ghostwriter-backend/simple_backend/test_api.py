# TEST YOUR NEW DATABASE API
import requests
import json

# API base URL
BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_signup():
    """Test user signup"""
    print("🔍 Testing user signup...")
    
    signup_data = {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_login():
    """Test user login"""
    print("🔍 Testing user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_story_generation(token):
    """Test story generation"""
    print("🔍 Testing story generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    story_data = {
        "plot": "A detective solves a mystery in Victorian London",
        "when_where": "Victorian London, 1888",
        "characters": "Detective Sherlock Holmes, Dr. Watson",
        "genre": "mystery",
        "writing_style": "Arthur Conan Doyle",
        "timeline": "1. Murder occurs 2. Investigation begins 3. Solution found",
        "title": "The Victorian Mystery",
        "author_name": "Test Author",
        "generate_cover": True
    }
    
    response = requests.post(f"{BASE_URL}/api/stories/generate", json=story_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Story ID: {data['id']}")
        print(f"Title: {data['title']}")
        print(f"Content length: {len(data['content'])} characters")
        return data['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_stories(token):
    """Test getting user stories"""
    print("🔍 Testing get user stories...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/users/me/stories", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_get_stats(token):
    """Test getting user stats"""
    print("🔍 Testing get user stats...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/users/me/stats", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Run all tests"""
    print("🚀 TESTING YOUR DATABASE API")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test signup
    token = test_signup()
    
    if not token:
        # Try login instead
        token = test_login()
    
    if token:
        print(f"✅ Got token: {token[:20]}...")
        print()
        
        # Test story generation
        story_id = test_story_generation(token)
        
        if story_id:
            print()
            # Test getting stories
            test_get_stories(token)
            print()
            # Test getting stats
            test_get_stats(token)
        
        print("🎉 ALL TESTS COMPLETED!")
    else:
        print("❌ Failed to get authentication token")

if __name__ == "__main__":
    main()
