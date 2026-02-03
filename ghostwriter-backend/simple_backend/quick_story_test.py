import requests

# Test signup
signup_data = {
    "email": "fixtest@example.com",
    "password": "TestPass123!",
    "full_name": "Fix Test"
}

print("Creating user...")
response = requests.post("http://localhost:8001/api/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print("✅ Got token!")
    
    # Test story generation
    story_data = {
        "plot": "A detective solves a mystery",
        "when_where": "Victorian London",
        "characters": "Sherlock Holmes",
        "genre": "mystery",
        "writing_style": "Arthur Conan Doyle",
        "timeline": "Beginning, middle, end",
        "title": "The Mystery",
        "author_name": "Fix Test"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    print("\nGenerating story...")
    response = requests.post("http://localhost:8001/api/stories/generate", json=story_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        story = response.json()
        print("✅ STORY GENERATION WORKS!")
        print(f"Title: {story['title']}")
        print(f"Length: {len(story['content'])} chars")
    else:
        print(f"❌ Failed: {response.json()}")
