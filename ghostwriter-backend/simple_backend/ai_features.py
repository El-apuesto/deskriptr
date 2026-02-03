# AI-Powered Standout Features for Production

"""
STORY-GENERATOR AI FEATURES THAT WILL MAKE YOUR APP STAND OUT:

1. AI Story Critique & Enhancement
2. Character Development Assistant  
3. Plot Hole Detection
4. Writing Style Analysis
5. Emotional Arc Mapping
6. Dialogue Improvement
7. Pacing Analysis
8. Genre Compliance Checker
9. Readability Score
10. SEO-Friendly Title Generation
"""

# 1. AI Story Critique & Enhancement
def critique_and_enhance_story(story_content, genre):
    """AI analyzes story and provides specific improvement suggestions"""
    critique_prompt = f"""
    As a professional story editor, analyze this {genre} story and provide:
    1. Strengths (what works well)
    2. Areas for improvement (specific suggestions)
    3. Pacing issues and recommendations
    4. Character development opportunities
    5. Plot enhancement ideas
    
    Story: {story_content}
    
    Provide actionable, specific feedback that will help the writer improve their story.
    """
    return critique_prompt

# 2. Character Development Assistant
def develop_characters(characters, plot):
    """AI helps flesh out characters with depth and consistency"""
    character_prompt = f"""
    Based on these characters and plot, develop detailed character profiles:
    
    Characters: {characters}
    Plot: {plot}
    
    For each character, provide:
    1. Detailed backstory (3-5 sentences)
    2. Motivations and fears
    3. Character arc throughout the story
    4. Unique voice/dialogue style
    5. Relationships with other characters
    
    Make sure characters are consistent and compelling.
    """
    return character_prompt

# 3. Plot Hole Detection
def detect_plot_holes(story_content, timeline):
    """AI identifies logical inconsistencies and plot holes"""
    plot_hole_prompt = f"""
    Analyze this story for plot holes, inconsistencies, and logical issues:
    
    Story: {story_content}
    Timeline: {timeline}
    
    Check for:
    1. Timeline inconsistencies
    2. Character behavior contradictions
    3. Unresolved plot points
    4. Logical impossibilities
    5. Missing explanations for key events
    
    Provide specific locations and suggested fixes.
    """
    return plot_hole_prompt

# 4. Writing Style Analysis
def analyze_writing_style(story_content, target_style):
    """AI compares writing style to target author/style"""
    style_prompt = f"""
    Analyze this writing sample and compare it to {target_style}'s style:
    
    Story: {story_content}
    
    Provide analysis on:
    1. Sentence structure and length variation
    2. Vocabulary level and word choice
    3. Pacing and rhythm
    4. Literary devices used
    5. Overall tone consistency
    
    Give specific suggestions to better match the target style.
    """
    return style_prompt

# 5. Emotional Arc Mapping
def map_emotional_arc(story_content):
    """AI tracks emotional journey and suggests improvements"""
    emotional_prompt = f"""
    Map the emotional arc of this story:
    
    Story: {story_content}
    
    Identify:
    1. Key emotional turning points
    2. Emotional highs and lows
    3. Character emotional development
    4. Reader engagement moments
    5. Areas where emotional impact could be strengthened
    
    Suggest specific scenes or moments to enhance emotional impact.
    """
    return emotional_prompt

# 6. Dialogue Improvement
def improve_dialogue(story_content, characters):
    """AI enhances dialogue authenticity and character voice"""
    dialogue_prompt = f"""
    Analyze and improve the dialogue in this story:
    
    Story: {story_content}
    Characters: {characters}
    
    For each character's dialogue, assess:
    1. Voice consistency and uniqueness
    2. Natural flow and authenticity
    3. Subtext and underlying emotions
    4. Information revealed through dialogue
    5. Areas for improvement with specific examples
    
    Rewrite weak dialogue examples to be more compelling.
    """
    return dialogue_prompt

# 7. Pacing Analysis
def analyze_pacing(story_content, story_length):
    """AI analyzes story pacing and suggests improvements"""
    pacing_prompt = f"""
    Analyze the pacing of this {story_length} story:
    
    Story: {story_content}
    
    Evaluate:
    1. Opening hook effectiveness
    2. Rising tension and conflict
    3. Climax impact and timing
    4. Resolution satisfaction
    5. Overall pacing rhythm
    6. Sections that drag or rush
    
    Provide specific suggestions to improve pacing and reader engagement.
    """
    return pacing_prompt

# 8. Genre Compliance Checker
def check_genre_compliance(story_content, genre):
    """AI ensures story meets genre expectations and conventions"""
    genre_prompt = f"""
    Verify this story meets {genre} genre conventions:
    
    Story: {story_content}
    
    Check for:
    1. Genre-specific tropes and elements
    2. Reader expectations for this genre
    3. Marketability within the genre
    4. Missing genre conventions
    5. Areas that might confuse or disappoint genre readers
    
    Provide suggestions to strengthen genre appeal.
    """
    return genre_prompt

# 9. Readability Score
def calculate_readability(story_content):
    """AI calculates readability metrics and suggests improvements"""
    readability_prompt = f"""
    Analyze readability of this story:
    
    Story: {story_content}
    
    Calculate and provide:
    1. Flesch-Kincaid readability score
    2. Average sentence length
    3. Vocabulary complexity level
    4. Paragraph structure analysis
    5. Target audience appropriateness
    
    Suggest improvements for optimal readability.
    """
    return readability_prompt

# 10. SEO-Friendly Title Generation
def generate_seo_titles(story_content, genre):
    """AI generates catchy, SEO-friendly titles"""
    title_prompt = f"""
    Generate 10 compelling, SEO-friendly titles for this {genre} story:
    
    Story: {story_content}
    
    Create titles that are:
    1. Intriguing and clickable
    2. SEO-optimized with relevant keywords
    3. Appropriate for the target audience
    4. Memorable and shareable
    5. Under 60 characters for optimal display
    
    Rank titles by effectiveness and explain reasoning.
    """
    return title_prompt

# 11. Story Blurb Generator
def generate_story_blurb(story_content, genre, target_audience):
    """AI creates compelling book descriptions for marketing"""
    blurb_prompt = f"""
    Write a compelling book blurb for this {genre} story targeting {target_audience}:
    
    Story: {story_content}
    
    Create a blurb that:
    1. Hooks readers immediately
    2. Introduces main conflict and stakes
    3. Hints at themes without spoiling
    4. Establishes tone and genre
    5. Ends with a compelling question or statement
    6. Is 150-200 words for optimal marketing
    
    Make it irresistible to the target audience.
    """
    return blurb_prompt

# 12. Character Name Generator
def generate_character_names(genre, character_description):
    """AI generates genre-appropriate character names"""
    name_prompt = f"""
    Generate 10 character names perfect for this {genre} character:
    
    Character: {character_description}
    
    Provide names that:
    1. Fit the genre's time period and culture
    2. Match the character's personality
    3. Are memorable and pronounceable
    4. Have appropriate meanings or connotations
    5. Stand out from common clichés
    
    Include brief explanations for each name choice.
    """
    return name_prompt

# 13. Setting Description Enhancer
def enhance_setting_description(setting, mood, genre):
    """AI enriches setting descriptions with sensory details"""
    setting_prompt = f"""
    Enhance this setting description for a {genre} story with {mood} mood:
    
    Setting: {setting}
    
    Expand with:
    1. Vivid sensory details (sight, sound, smell, touch, taste)
    2. Atmospheric elements that enhance mood
    3. Historical or cultural context
    4. Symbolic elements that support themes
    5. Interactive elements characters can engage with
    
    Make the setting feel alive and integral to the story.
    """
    return setting_prompt

# 14. Theme Development Assistant
def develop_themes(themes, plot, characters):
    """AI helps weave themes more deeply into the narrative"""
    theme_prompt = f"""
    Analyze and strengthen theme development in this story:
    
    Themes: {themes}
    Plot: {plot}
    Characters: {characters}
    
    Provide suggestions for:
    1. Weaving themes more naturally into dialogue
    2. Symbolic elements that reinforce themes
    3. Character arcs that embody themes
    4. Plot events that explore thematic questions
    5. Subtle thematic foreshadowing
    
    Help make themes more impactful and integrated.
    """
    return theme_prompt

# 15. Story Structure Analyzer
def analyze_story_structure(story_content, genre):
    """AI analyzes story structure against classic frameworks"""
    structure_prompt = f"""
    Analyze this {genre} story's narrative structure:
    
    Story: {story_content}
    
    Evaluate against:
    1. Three-act structure (setup, confrontation, resolution)
    2. Hero's journey elements (if applicable)
    3. Freytag's pyramid (exposition, rising action, climax, falling action, denouement)
    4. Genre-specific structure expectations
    5. Pacing and tension curves
    
    Identify structural strengths and areas for improvement.
    """
    return structure_prompt
