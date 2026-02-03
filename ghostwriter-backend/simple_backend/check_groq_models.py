# CHECK AVAILABLE GROQ MODELS
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

def check_available_models():
    """Check what models are available on Groq"""
    print("🔍 CHECKING AVAILABLE GROQ MODELS")
    print("=" * 50)
    
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # List available models
        models = client.models.list()
        
        print("Available models:")
        for model in models.data:
            print(f"  - {model.id}")
            if hasattr(model, 'owned_by'):
                print(f"    Owned by: {model.owned_by}")
        
        # Try current working models
        working_models = [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "gemma2-9b-it"
        ]
        
        print(f"\n🧪 TESTING WORKING MODELS:")
        
        for model in working_models:
            print(f"\nTesting {model}:")
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "Write one sentence about a detective."}
                    ],
                    max_tokens=50
                )
                
                content = completion.choices[0].message.content
                print(f"✅ {model} WORKS!")
                print(f"   Sample: {content}")
                
            except Exception as e:
                print(f"❌ {model} failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Failed to check models: {str(e)}")

if __name__ == "__main__":
    check_available_models()
