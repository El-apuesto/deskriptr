# TEST GROQ API ONLY - Verify it's working with rate limits
import os
from dotenv import load_dotenv
from groq import Groq
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_groq_api():
    """Test Groq API with your actual key"""
    print("🧪 TESTING GROQ API")
    print("=" * 50)
    
    try:
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        print(f"API Key found: {bool(api_key)}")
        print(f"API Key length: {len(api_key) if api_key else 0}")
        
        client = Groq(api_key=api_key)
        
        # Test prompt
        prompt = """
        Write a short mystery story (200-300 words) about a detective who finds a mysterious clue in Victorian London.
        Make it engaging and well-written.
        """
        
        print("Sending request to Groq...")
        
        # Generate story with updated model
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Updated to current model
            messages=[
                {
                    "role": "system", 
                    "content": "You are a talented story writer who creates engaging, well-written stories."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        content = completion.choices[0].message.content
        
        print("✅ GROQ API SUCCESS!")
        print(f"Content length: {len(content)} characters")
        print(f"Word count: {len(content.split())} words")
        print("\nGenerated Story:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ GROQ API FAILED: {str(e)}")
        
        # Check for rate limit specific errors
        error_str = str(e).lower()
        if "rate limit" in error_str:
            print("🚨 RATE LIMIT DETECTED - This confirms your theory!")
            print("💡 Solution: Switch to xAI Grok or implement rate limiting")
        elif "quota" in error_str:
            print("🚨 QUOTA EXCEEDED - API limit reached")
        elif "authentication" in error_str or "unauthorized" in error_str:
            print("🚨 AUTHENTICATION ERROR - Check API key")
        
        return False

def test_multiple_requests():
    """Test multiple requests to check rate limits"""
    print("\n🔄 TESTING MULTIPLE REQUESTS")
    print("=" * 50)
    
    success_count = 0
    total_requests = 3
    
    for i in range(total_requests):
        print(f"\nRequest {i+1}/{total_requests}:")
        if test_groq_api():
            success_count += 1
        else:
            break  # Stop if we hit an error
    
    print(f"\n📊 RESULTS: {success_count}/{total_requests} requests successful")
    
    if success_count < total_requests:
        print("🚨 RATE LIMIT CONFIRMED - Need xAI Grok fallback!")
    else:
        print("✅ No rate limiting issues detected")

if __name__ == "__main__":
    test_groq_api()
    test_multiple_requests()
