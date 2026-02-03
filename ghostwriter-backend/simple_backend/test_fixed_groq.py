# TEST FIXED GROQ INTEGRATION
import os
from dotenv import load_dotenv
from groq_to_grok import ai_manager

# Load environment variables
load_dotenv()

def test_story_generation():
    """Test the fixed story generation"""
    print("🧪 TESTING FIXED STORY GENERATION")
    print("=" * 50)
    
    # Test story data
    story_data = {
        "plot": "A detective discovers a mysterious portal to another dimension in Victorian London",
        "when_where": "Victorian London, 1888, during a foggy night",
        "characters": "Detective Sherlock Holmes, Dr. Watson, mysterious stranger from another world",
        "genre": "mystery",
        "writing_style": "Arthur Conan Doyle",
        "timeline": "1. Strange discovery 2. Portal opens 3. Other world revealed 4. Mystery solved",
        "story_length": "short",
        "mood": "mysterious and suspenseful",
        "themes": "mystery, adventure, discovery",
        "point_of_view": "third person",
        "target_audience": "adults",
        "additional_notes": "Make it clever with a good twist"
    }
    
    print("Generating story with fixed AI manager...")
    
    try:
        content = ai_manager.generate_story(story_data)
        
        if content:
            print("✅ STORY GENERATION SUCCESS!")
            print(f"Content length: {len(content)} characters")
            print(f"Word count: {len(content.split())} words")
            print("\nGenerated Story:")
            print("-" * 60)
            print(content)
            print("-" * 60)
            
            # Check if it's fallback content
            if "Once upon a time" in content and "The end." in content:
                print("⚠️  Used fallback content (AI services failed)")
                return False
            else:
                print("🎉 Used real AI-generated content!")
                return True
        else:
            print("❌ No content generated")
            return False
            
    except Exception as e:
        print(f"❌ Story generation failed: {str(e)}")
        return False

def test_multiple_stories():
    """Test multiple story generations"""
    print("\n🔄 TESTING MULTIPLE STORIES")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    for i in range(total_tests):
        print(f"\n--- Test {i+1}/{total_tests} ---")
        
        story_data = {
            "plot": f"Test story {i+1} about a magical adventure",
            "when_where": "Fantasy world",
            "characters": "Hero, wizard, dragon",
            "genre": "fantasy",
            "writing_style": "J.R.R. Tolkien",
            "timeline": "Beginning, middle, end",
            "story_length": "short",
            "mood": "adventurous",
            "themes": "magic, courage",
            "point_of_view": "third person",
            "target_audience": "general",
            "additional_notes": f"Test number {i+1}"
        }
        
        try:
            content = ai_manager.generate_story(story_data)
            if content and len(content) > 100:
                success_count += 1
                print(f"✅ Success ({len(content)} chars)")
            else:
                print(f"❌ Failed or too short")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n📊 RESULTS: {success_count}/{total_tests} stories generated successfully")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Production ready!")
    elif success_count > 0:
        print("⚠️  Partial success - Some rate limiting may occur")
    else:
        print("❌ All failed - Need xAI Grok fallback")
    
    return success_count

if __name__ == "__main__":
    # Test single story
    single_success = test_story_generation()
    
    # Test multiple stories
    multiple_success = test_multiple_stories()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT:")
    
    if single_success and multiple_success > 0:
        print("✅ GROQ API IS WORKING - Production ready!")
        print("💡 Rate limits may apply, consider xAI Grok for higher limits")
    elif single_success:
        print("⚠️  Single story works, but rate limits detected")
        print("💡 Add xAI Grok for production use")
    else:
        print("❌ GROQ API issues confirmed")
        print("🚨 IMPLEMENT XAI GROK FALLBACK IMMEDIATELY")
    
    print("=" * 60)
