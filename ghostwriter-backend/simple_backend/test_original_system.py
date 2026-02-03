# TEST YOUR ORIGINAL MULTI-STEP NOVEL GENERATION SYSTEM
import requests
import random

# Create unique user
random_num = random.randint(1000, 9999)
email = f"noveltest{random_num}@example.com"

# Test signup
signup_data = {
    "email": email,
    "password": "TestPass123!",
    "full_name": f"Novel Test {random_num}"
}

print("🚀 TESTING YOUR ORIGINAL NOVEL GENERATION SYSTEM")
print("=" * 60)

print("Creating user...")
response = requests.post("http://localhost:8001/api/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print("✅ Got token!")
    
    # Test NOVEL generation (not short story!)
    story_data = {
        "plot": "A space explorer discovers an ancient alien artifact on Mars that reveals humanity's true origins",
        "when_where": "Mars colony, year 2150",
        "characters": "Commander Sarah Jenkins, Dr. Marcus Chen, the alien consciousness, crew of the Mars base",
        "genre": "scifi",
        "writing_style": "Arthur C. Clarke meets Isaac Asimov",
        "timeline": "Discovery → Investigation → Revelation → Transformation",
        "title": "The Mars Revelation",
        "author_name": f"Novel Test {random_num}",
        "story_length": "novel",  # THIS IS THE KEY - 90,000 WORDS!
        "num_chapters": 12
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    print("\n📚 STARTING NOVEL GENERATION...")
    print(f"Target: 90,000 words across 12 chapters")
    response = requests.post("http://localhost:8001/api/stories/generate", json=story_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("🎉 YOUR ORIGINAL SYSTEM IS WORKING!")
        print(f"✅ Story ID: {result['id']}")
        print(f"✅ Title: {result['title']}")
        print(f"✅ Status: {result['status']}")
        print(f"✅ Type: {result['story_type']}")
        print(f"✅ Target: {result['word_count_target']}")
        print(f"✅ Chapters: {result['chapters']}")
        
        print(f"\n🔥 THIS IS YOUR ORIGINAL SYSTEM:")
        print("- Multi-step chapter generation")
        print("- Context continuity management")
        print("- 90,000 word novel target")
        print("- Background processing")
        print("- Progress tracking")
        
        print(f"\n📖 NOVEL GENERATION STARTED!")
        print("Check database for progress updates...")
        
    else:
        print(f"❌ Failed: {response.json()}")
else:
    print(f"❌ Signup failed: {response.json()}")
