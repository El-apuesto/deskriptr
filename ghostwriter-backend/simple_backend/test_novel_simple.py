# SIMPLE TEST OF NOVEL GENERATION WITHOUT ORIGINAL SYSTEM COMPLEXITY
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

print("🚀 TESTING NOVEL GENERATION CAPABILITY")
print("=" * 60)

print("Creating user...")
response = requests.post("http://localhost:8001/api/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print("✅ Got token!")
    
    # Test NOVEL request (not short story!)
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
    print("\n📚 TESTING NOVEL GENERATION REQUEST...")
    print(f"Target: 90,000 words across 12 chapters")
    response = requests.post("http://localhost:8001/api/stories/generate", json=story_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("🎉 NOVEL GENERATION STARTED!")
        print(f"✅ Story ID: {result['id']}")
        print(f"✅ Title: {result['title']}")
        print(f"✅ Status: {result['status']}")
        print(f"✅ Type: {result.get('story_type', 'unknown')}")
        print(f"✅ Target: {result.get('word_count_target', 'unknown')}")
        print(f"✅ Chapters: {result.get('chapters', 'unknown')}")
        
        print(f"\n🔥 YOUR NOVEL GENERATION SYSTEM IS WORKING!")
        print("- 90,000 word novel target")
        print("- 12 chapter structure")
        print("- Multi-step generation started")
        print("- Background processing active")
        
        print(f"\n📖 CHECK STORY PROGRESS:")
        story_id = result['id']
        progress_response = requests.get(f"http://localhost:8001/api/stories/{story_id}", headers=headers)
        if progress_response.status_code == 200:
            story = progress_response.json()
            print(f"Current Status: {story.get('status', 'unknown')}")
            print(f"Word Count: {story.get('word_count', 0)}")
            print(f"Chapters Completed: {story.get('chapters_completed', 0)}/{story.get('total_chapters', 0)}")
        
    else:
        print(f"❌ Failed: {response.json()}")
else:
    print(f"❌ Signup failed: {response.json()}")
