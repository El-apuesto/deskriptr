# GROQ TO XAI GROK SWAP - Production Ready AI Integration
# Replace Groq with xAI Grok for better rate limits and reliability

import os
import requests
import json
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIServiceManager:
    """Manage multiple AI services with fallback"""
    
    def __init__(self):
        self.primary_service = "grok"  # Use xAI Grok as primary
        self.fallback_service = "groq"  # Use Groq as fallback
        
        # API configurations
        self.grok_config = {
            "api_key": os.getenv("XAI_API_KEY"),
            "base_url": "https://api.x.ai/v1",
            "model": "grok-beta",
            "max_tokens": 2000,
            "temperature": 0.8
        }
        
        self.groq_config = {
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.1-8b-instant",  # Updated to working model
            "max_tokens": 2000,
            "temperature": 0.8
        }
    
    def generate_with_grok(self, prompt: str) -> Optional[str]:
        """Generate story using xAI Grok"""
        try:
            if not self.grok_config["api_key"]:
                logger.warning("xAI API key not configured")
                return None
            
            headers = {
                "Authorization": f"Bearer {self.grok_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.grok_config["model"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a talented story writer who creates engaging, well-written stories based on user prompts. Write compelling narratives that are appropriate for the target audience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.grok_config["max_tokens"],
                "temperature": self.grok_config["temperature"]
            }
            
            response = requests.post(
                f"{self.grok_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"xAI Grok API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"xAI Groq generation failed: {str(e)}")
            return None
    
    def generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate story using Groq (fallback)"""
        try:
            from groq import Groq
            
            if not self.groq_config["api_key"]:
                logger.warning("Groq API key not configured")
                return None
            
            client = Groq(api_key=self.groq_config["api_key"])
            
            completion = client.chat.completions.create(
                model=self.groq_config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a talented story writer who creates engaging, well-written stories based on user prompts. Write compelling narratives that are appropriate for the target audience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.groq_config["max_tokens"],
                temperature=self.groq_config["temperature"]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
            return None
    
    def generate_story(self, story_data) -> str:
        """Generate story with automatic fallback"""
        
        # Handle both dict and object inputs
        if hasattr(story_data, 'story_length'):
            # It's an object, use attributes
            plot = story_data.plot
            when_where = story_data.when_where
            characters = story_data.characters
            genre = story_data.genre
            writing_style = story_data.writing_style
            timeline = story_data.timeline
            mood = getattr(story_data, 'mood', '')
            themes = getattr(story_data, 'themes', '')
            point_of_view = getattr(story_data, 'point_of_view', 'third person')
            target_audience = getattr(story_data, 'target_audience', 'general')
            story_length = getattr(story_data, 'story_length', 'medium')
            additional_notes = getattr(story_data, 'additional_notes', '')
        else:
            # It's a dict, use keys
            plot = story_data.get('plot', '')
            when_where = story_data.get('when_where', '')
            characters = story_data.get('characters', '')
            genre = story_data.get('genre', '')
            writing_style = story_data.get('writing_style', '')
            timeline = story_data.get('timeline', '')
            mood = story_data.get('mood', '')
            themes = story_data.get('themes', '')
            point_of_view = story_data.get('point_of_view', 'third person')
            target_audience = story_data.get('target_audience', 'general')
            story_length = story_data.get('story_length', 'medium')
            additional_notes = story_data.get('additional_notes', '')
        
        # Create comprehensive prompt
        prompt = f"""
        Write a {story_length} story in the {genre} genre.
        
        Plot: {plot}
        Setting: {when_where}
        Characters: {characters}
        Writing Style: {writing_style}
        Timeline: {timeline}
        Mood: {mood}
        Themes: {themes}
        Point of View: {point_of_view}
        Target Audience: {target_audience}
        
        Additional Notes: {additional_notes}
        
        Please write a compelling, well-structured story based on these elements.
        Make it engaging and appropriate for the target audience.
        The story should be approximately 500-1000 words.
        """
        
        # Try primary service first
        logger.info(f"Attempting story generation with {self.primary_service}")
        content = None
        
        if self.primary_service == "grok":
            content = self.generate_with_grok(prompt)
            if not content:
                logger.warning("xAI Grok failed, trying Groq fallback")
                content = self.generate_with_groq(prompt)
        else:
            content = self.generate_with_groq(prompt)
            if not content:
                logger.warning("Groq failed, trying xAI Grok fallback")
                content = self.generate_with_grok(prompt)
        
        if content:
            logger.info(f"Story generated successfully using {'xAI Grok' if self.primary_service == 'grok' and content else 'Groq'}")
            return content
        else:
            logger.error("All AI services failed")
            return self._generate_fallback_story(story_data)
    
    def _generate_fallback_story(self, story_data) -> str:
        """Generate fallback story when all AI services fail"""
        
        # Handle both dict and object inputs
        if hasattr(story_data, 'story_length'):
            # It's an object, use attributes
            plot = story_data.plot
            when_where = story_data.when_where
            characters = story_data.characters
            genre = story_data.genre
            writing_style = story_data.writing_style
            timeline = story_data.timeline
            mood = getattr(story_data, 'mood', '')
            themes = getattr(story_data, 'themes', '')
            point_of_view = getattr(story_data, 'point_of_view', 'third person')
            target_audience = getattr(story_data, 'target_audience', 'general')
            story_length = getattr(story_data, 'story_length', 'medium')
            additional_notes = getattr(story_data, 'additional_notes', '')
        else:
            # It's a dict, use keys
            plot = story_data.get('plot', '')
            when_where = story_data.get('when_where', '')
            characters = story_data.get('characters', '')
            genre = story_data.get('genre', '')
            writing_style = story_data.get('writing_style', '')
            timeline = story_data.get('timeline', '')
            mood = story_data.get('mood', '')
            themes = story_data.get('themes', '')
            point_of_view = story_data.get('point_of_view', 'third person')
            target_audience = story_data.get('target_audience', 'general')
            story_length = story_data.get('story_length', 'medium')
            additional_notes = story_data.get('additional_notes', '')
        
        return f"""
        Once upon a time in {when_where}, there lived someone who would change everything.
        
        {characters}
        
        The story begins with {plot}. This {genre} tale takes readers on a journey through {themes or 'various challenges and discoveries'}.
        
        Written in the style of {writing_style}, this {story_length} story explores {mood or 'deep emotions and thrilling adventures'}.
        
        The timeline follows {timeline}, creating a narrative that captivates {target_audience} readers.
        
        {additional_notes}
        
        The end.
        """

# Global AI service manager
ai_manager = AIServiceManager()

def generate_story_content(story_data):
    """Main story generation function"""
    return ai_manager.generate_story(story_data)

# Test function
def test_ai_services():
    """Test both AI services"""
    print("🧪 TESTING AI SERVICES")
    print("=" * 50)
    
    # Test data
    test_story_data = {
        "plot": "A detective solves a mysterious murder in Victorian London",
        "when_where": "Victorian London, 1888",
        "characters": "Detective Sherlock Holmes, Dr. Watson, Professor Moriarty",
        "genre": "mystery",
        "writing_style": "Arthur Conan Doyle",
        "timeline": "1. Murder occurs 2. Investigation begins 3. Clues found 4. Mystery solved",
        "story_length": "short",
        "mood": "suspenseful",
        "themes": "justice, deduction, mystery",
        "point_of_view": "third person",
        "target_audience": "adults",
        "additional_notes": "Make it clever and full of twists"
    }
    
    print("1. Testing xAI Grok...")
    grok_content = ai_manager.generate_with_grok(f"Write a short mystery story: {test_story_data['plot']}")
    
    if grok_content:
        print("✅ xAI Grok working!")
        print(f"Content preview: {grok_content[:200]}...")
        print(f"Length: {len(grok_content)} characters")
    else:
        print("❌ xAI Grok failed")
    
    print("\n2. Testing Groq...")
    groq_content = ai_manager.generate_with_groq(f"Write a short mystery story: {test_story_data['plot']}")
    
    if groq_content:
        print("✅ Groq working!")
        print(f"Content preview: {groq_content[:200]}...")
        print(f"Length: {len(groq_content)} characters")
    else:
        print("❌ Groq failed")
    
    print("\n3. Testing with fallback system...")
    final_content = ai_manager.generate_story(test_story_data)
    
    if final_content:
        print("✅ Fallback system working!")
        print(f"Final content preview: {final_content[:200]}...")
        print(f"Length: {len(final_content)} characters")
    else:
        print("❌ All systems failed")
    
    print("\n" + "=" * 50)
    print("🎯 AI Service Test Complete!")

if __name__ == "__main__":
    test_ai_services()
