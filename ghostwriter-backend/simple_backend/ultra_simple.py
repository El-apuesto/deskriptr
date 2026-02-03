from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import hashlib
import jwt
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Initialize FastAPI
app = FastAPI(title="Ultra Simple Story Generator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# In-memory storage (no database)
users = {}
stories = {}
SECRET_KEY = "ultra-simple-secret"

# Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "your-groq-api-key-here"))

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class StoryRequest(BaseModel):
    # Core story elements
    plot: str
    when_where: str
    characters: str
    genre: str
    writing_style: str
    timeline: str
    
    # Enhanced options
    mood: str = ""  # e.g., "dark, mysterious, uplifting"
    themes: str = ""  # e.g., "betrayal, redemption, coming of age"
    point_of_view: str = "third person"  # first person, third person, omniscient
    target_audience: str = "general"  # young adult, adult, mature
    story_length: str = "medium"  # short, medium, long
    additional_notes: str = ""  # Any specific requirements
    
    # Cover generation
    title: str = ""  # Story title for cover
    author_name: str = ""  # Author name for cover
    generate_cover: bool = False  # Whether to generate cover image
    
    # Chapter editing
    split_into_chapters: bool = True  # Auto-split into chapters
    num_chapters: int = 3  # Number of chapters to split into

class ChapterEdit(BaseModel):
    story_id: int
    chapter_number: int
    chapter_content: str

class PhotoUpload(BaseModel):
    story_id: int
    photo_type: str  # "cover" or "author"
    photo_data: str  # Base64 encoded image
    filename: str

# Real Cover Generation
def generate_real_cover_image(request: StoryRequest):
    """Generate actual cover image using PIL and templates"""
    try:
        # Cover dimensions (standard book cover)
        width, height = 800, 1200
        
        # Create base image
        cover = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(cover)
        
        # Genre-based color schemes and templates
        genre_configs = {
            "fantasy": {
                "bg_color": "#1a1a2e",
                "accent_color": "#16213e",
                "text_color": "#e94560",
                "template": "gradient mystical"
            },
            "scifi": {
                "bg_color": "#0f0f0f",
                "accent_color": "#1a1a1a",
                "text_color": "#00ff41",
                "template": "tech grid"
            },
            "mystery": {
                "bg_color": "#2c3e50",
                "accent_color": "#34495e",
                "text_color": "#ecf0f1",
                "template": "shadow noir"
            },
            "romance": {
                "bg_color": "#ffebee",
                "accent_color": "#ffcdd2",
                "text_color": "#c2185b",
                "template": "soft gradient"
            },
            "thriller": {
                "bg_color": "#263238",
                "accent_color": "#37474f",
                "text_color": "#ff5252",
                "template": "dramatic split"
            },
            "horror": {
                "bg_color": "#000000",
                "accent_color": "#1a1a1a",
                "text_color": "#ff0000",
                "template": "dark texture"
            },
            "adventure": {
                "bg_color": "#2e7d32",
                "accent_color": "#388e3c",
                "text_color": "#ffffff",
                "template": "outdoor map"
            },
            "historical": {
                "bg_color": "#8d6e63",
                "accent_color": "#a1887f",
                "text_color": "#fff3e0",
                "template": "vintage parchment"
            },
            "literary": {
                "bg_color": "#f5f5f5",
                "accent_color": "#e0e0e0",
                "text_color": "#212121",
                "template": "minimalist"
            },
            "comedy": {
                "bg_color": "#fff59d",
                "accent_color": "#ffeb3b",
                "text_color": "#f57c00",
                "template": "playful bubbles"
            },
            "satire": {
                "bg_color": "#eceff1",
                "accent_color": "#cfd8dc",
                "text_color": "#37474f",
                "template": "political cartoon"
            },
            "deadpan": {
                "bg_color": "#ffffff",
                "accent_color": "#f5f5f5",
                "text_color": "#424242",
                "template": "clean minimal"
            },
            "absurdist": {
                "bg_color": "#e91e63",
                "accent_color": "#f06292",
                "text_color": "#ffffff",
                "template": "surreal collage"
            },
            "biography": {
                "bg_color": "#5d4037",
                "accent_color": "#6d4c41",
                "text_color": "#d7ccc8",
                "template": "elegant portrait"
            }
        }
        
        config = genre_configs.get(request.genre.lower(), genre_configs["literary"])
        
        # Apply template
        if config["template"] == "gradient mystical":
            # Fantasy gradient
            for y in range(height):
                color_value = int(26 + (y / height) * 30)
                draw.rectangle([(0, y), (width, y)], fill=(color_value, color_value, color_value + 20))
            
            # Add mystical symbols
            for _ in range(20):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(2, 8)
                draw.ellipse([(x, y), (x+size, y+size)], fill=config["text_color"], outline=None)
                
        elif config["template"] == "tech grid":
            # Sci-fi grid
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            grid_spacing = 40
            for x in range(0, width, grid_spacing):
                draw.line([(x, 0), (x, height)], fill=config["text_color"], width=1)
            for y in range(0, height, grid_spacing):
                draw.line([(0, y), (width, y)], fill=config["text_color"], width=1)
                
        elif config["template"] == "shadow noir":
            # Mystery shadows
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            for _ in range(15):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                w = np.random.randint(50, 200)
                h = np.random.randint(50, 200)
                draw.rectangle([(x, y), (x+w, y+h)], fill=config["accent_color"], outline=None)
                
        elif config["template"] == "soft gradient":
            # Romance soft gradient
            for y in range(height):
                r = int(255 + (y / height) * 10)
                g = int(235 + (y / height) * 10)
                b = int(238 + (y / height) * 10)
                draw.rectangle([(0, y), (width, y)], fill=(r, g, b))
                
        elif config["template"] == "dramatic split":
            # Thriller diagonal split
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            draw.polygon([(0, 0), (width, 0), (width, height//2), (0, height)], fill=config["accent_color"])
            
        elif config["template"] == "dark texture":
            # Horror dark texture
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            for _ in range(100):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                draw.point((x, y), fill=(50, 0, 0))
                
        elif config["template"] == "outdoor map":
            # Adventure map style
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add map-like lines
            for _ in range(10):
                x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
                x2, y2 = np.random.randint(0, width), np.random.randint(0, height)
                draw.line([(x1, y1), (x2, y2)], fill=config["accent_color"], width=2)
                
        elif config["template"] == "vintage parchment":
            # Historical parchment
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add aged texture
            for _ in range(50):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                draw.point((x, y), fill=(139, 90, 43))
                
        elif config["template"] == "minimalist":
            # Literary minimalist
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add simple geometric shapes
            draw.rectangle([(100, 200), (width-100, 300)], fill=config["accent_color"])
            
        elif config["template"] == "playful bubbles":
            # Comedy bubbles
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            for _ in range(30):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(20, 80)
                draw.ellipse([(x, y), (x+size, y+size)], fill=config["accent_color"], outline=config["text_color"], width=2)
                
        elif config["template"] == "political cartoon":
            # Satire cartoon style
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add cartoon-like elements
            for _ in range(10):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(30, 100)
                draw.ellipse([(x, y), (x+size, y+size)], fill=config["accent_color"], outline=config["text_color"])
                
        elif config["template"] == "clean minimal":
            # Deadpan clean minimal
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add single clean line
            draw.line([(100, height//2), (width-100, height//2)], fill=config["text_color"], width=3)
            
        elif config["template"] == "surreal collage":
            # Absurdist collage
            colors = ["#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3"]
            for _ in range(20):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                w = np.random.randint(50, 200)
                h = np.random.randint(50, 200)
                color = np.random.choice(colors)
                draw.rectangle([(x, y), (x+w, y+h)], fill=color, outline=None)
                
        elif config["template"] == "elegant portrait":
            # Biography elegant portrait
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
            # Add elegant frame
            frame_width = 50
            draw.rectangle([(frame_width, frame_width), (width-frame_width, height-frame_width)], 
                          outline=config["text_color"], width=5)
        
        else:
            # Default background
            draw.rectangle([(0, 0), (width, height)], fill=config["bg_color"])
        
        # Add title text
        title = request.title or "Untitled Story"
        author = request.author_name or "Anonymous"
        
        # Try to use a nice font, fallback to default
        try:
            # Try different font sizes for title
            title_font_size = 60
            title_font = ImageFont.truetype("arial.ttf", title_font_size)
        except:
            title_font = ImageFont.load_default()
        
        # Calculate text position (center)
        title_position = (width // 2, height // 3)
        author_position = (width // 2, height // 2)
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        # Add text shadow for better readability
        draw.text((title_x + 2, title_position[1] + 2), title, fill="black", font=title_font)
        draw.text((title_x, title_position[1]), title, fill=config["text_color"], font=title_font)
        
        # Add author text
        try:
            author_font = ImageFont.truetype("arial.ttf", 30)
        except:
            author_font = ImageFont.load_default()
            
        author_bbox = draw.textbbox((0, 0), author, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (width - author_width) // 2
        
        draw.text((author_x + 1, author_position[1] + 1), author, fill="black", font=author_font)
        draw.text((author_x, author_position[1]), author, fill=config["text_color"], font=author_font)
        
        # Convert to base64
        buffer = BytesIO()
        cover.save(buffer, format='PNG')
        cover_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image_data": cover_base64,
            "format": "PNG",
            "width": width,
            "height": height,
            "template": config["template"],
            "title": title,
            "author": author
        }
        
    except Exception as e:
        # Fallback to simple text-based cover
        return generate_fallback_cover(request)

def generate_fallback_cover(request: StoryRequest):
    """Fallback simple cover generation"""
    width, height = 800, 1200
    cover = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(cover)
    
    # Simple design
    draw.rectangle([(50, 50), (width-50, height-50)], outline='#333', width=3)
    
    title = request.title or "Untitled Story"
    author = request.author_name or "Anonymous"
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        author_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
    
    # Center text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_width = author_bbox[2] - author_bbox[0]
    author_x = (width - author_width) // 2
    
    draw.text((title_x, height//3), title, fill='#333', font=title_font)
    draw.text((author_x, height//2), author, fill='#666', font=author_font)
    
    buffer = BytesIO()
    cover.save(buffer, format='PNG')
    cover_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "image_data": cover_base64,
        "format": "PNG",
        "width": width,
        "height": height,
        "template": "fallback",
        "title": title,
        "author": author
    }

# Chapter Management
def split_into_chapters(content: str, num_chapters: int = 3):
    """Split story content into chapters"""
    paragraphs = content.split('\n\n')
    
    # Filter out empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    if len(paragraphs) <= num_chapters:
        # Not enough paragraphs, split evenly
        chapter_size = max(1, len(paragraphs) // num_chapters)
        chapters = []
        for i in range(num_chapters):
            start = i * chapter_size
            end = start + chapter_size if i < num_chapters - 1 else len(paragraphs)
            chapter_content = '\n\n'.join(paragraphs[start:end])
            chapters.append({
                "chapter_number": i + 1,
                "title": f"Chapter {i + 1}",
                "content": chapter_content
            })
        return chapters
    
    # Try to find natural break points (paragraphs that end with scene breaks)
    chapter_size = len(paragraphs) // num_chapters
    chapters = []
    
    for i in range(num_chapters):
        start = i * chapter_size
        end = start + chapter_size if i < num_chapters - 1 else len(paragraphs)
        
        # Look for natural break points near the end
        if i < num_chapters - 1 and end < len(paragraphs):
            # Look for paragraphs that end with dramatic punctuation or scene breaks
            for j in range(min(end + 2, len(paragraphs) - 1), max(start + 1, end - 2), -1):
                paragraph = paragraphs[j]
                if (paragraph.endswith('.') or paragraph.endswith('!') or paragraph.endswith('?') or 
                    '---' in paragraph or '***' in paragraph or len(paragraph) < 100):
                    end = j + 1
                    break
        
        chapter_content = '\n\n'.join(paragraphs[start:end])
        chapters.append({
            "chapter_number": i + 1,
            "title": f"Chapter {i + 1}",
            "content": chapter_content
        })
    
    return chapters

def rebuild_story_from_chapters(chapters: list):
    """Rebuild full story from edited chapters"""
    return '\n\n'.join([chapter['content'] for chapter in sorted(chapters, key=lambda x: x['chapter_number'])])
def export_to_pdf(story_data: dict, request: StoryRequest):
    """Export story to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title page
    title_style = styles['Title']
    title_style.textColor = 'black'
    title_style.alignment = 1  # Center
    
    story.append(Paragraph(request.title or "Untitled Story", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"By {request.author_name or 'Anonymous'}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Story metadata
    meta_style = styles['Normal']
    meta_style.fontSize = 10
    meta_style.textColor = 'gray'
    
    story.append(Paragraph(f"Genre: {request.genre}", meta_style))
    story.append(Paragraph(f"Writing Style: {request.writing_style}", meta_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    story.append(Spacer(1, 30))
    
    # Story content
    content_style = styles['Normal']
    content_style.fontSize = 12
    content_style.leading = 16
    
    paragraphs = story_data['content'].split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, content_style))
            story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    
    # Return as base64
    pdf_base64 = base64.b64encode(buffer.read()).decode()
    return pdf_base64

def export_to_word(story_data: dict, request: StoryRequest):
    """Export story to Word-like format (HTML that can be opened in Word)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{request.title or 'Untitled Story'}</title>
        <style>
            body {{ font-family: 'Times New Roman', serif; line-height: 1.6; margin: 40px; }}
            h1 {{ text-align: center; color: #333; }}
            h2 {{ color: #666; border-bottom: 1px solid #ccc; }}
            .meta {{ color: #888; font-size: 12px; margin-bottom: 30px; }}
            .content {{ text-align: justify; }}
        </style>
    </head>
    <body>
        <h1>{request.title or 'Untitled Story'}</h1>
        <p class="meta">By {request.author_name or 'Anonymous'}</p>
        <div class="meta">
            <p>Genre: {request.genre}</p>
            <p>Writing Style: {request.writing_style}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        <div class="content">
            {story_data['content'].replace(chr(10), '<br><br>')}
        </div>
    </body>
    </html>
    """
    
    return base64.b64encode(html_content.encode()).decode()

def export_to_text(story_data: dict, request: StoryRequest):
    """Export story to plain text"""
    text_content = f"""
{'='*50}
{request.title or 'Untitled Story'}
By {request.author_name or 'Anonymous'}
{'='*50}

Genre: {request.genre}
Writing Style: {request.writing_style}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{'-'*50}

{story_data['content']}
"""
    
    return base64.b64encode(text_content.encode()).decode()
def generate_story_content(request: StoryRequest):
    # Build comprehensive prompt
    prompt_parts = []
    
    # Handle biography/memoir differently
    if request.genre.lower() == "biography":
        prompt_parts = [
            f"Write a {request.story_length} {request.genre}",
            f"Subject: {request.plot}",  # For biography, plot is the person's life
            f"Time Period: {request.when_where}",  # When/where is the time period
            f"Key People: {request.characters}",  # Characters are key people in their life
            f"Life Events: {request.timeline}",  # Timeline is life events
            f"Writing style: Emulate {request.writing_style}",
            f"Tone: {request.mood if request.mood else 'engaging and authentic'}",
            f"Themes: {request.themes if request.themes else 'personal growth, overcoming challenges, legacy'}",
            "",
            "BIOGRAPHY GUIDELINES:",
            f"- Write in {request.point_of_view} perspective",
            f"- Maintain an {request.mood if request.mood else 'authentic and respectful'} tone",
            f"- Target {request.target_audience} readers",
            f"- Length: {request.story_length} ({'500-800 words' if request.story_length == 'short' else '1500-2500 words' if request.story_length == 'medium' else '3000-5000 words'})",
            "- Focus on significant life events and their impact",
            "- Include personal struggles and triumphs",
            "- Show how the person influenced others or their field",
            "- Create a compelling narrative arc",
            "- Include authentic details and context",
            "",
            "Write the biography now:"
        ]
    else:
        # Regular fiction genres
        prompt_parts = [
            f"Write a {request.story_length} {request.genre} story",
            f"Target audience: {request.target_audience}",
            f"Point of view: {request.point_of_view}",
            f"Writing style: Emulate {request.writing_style}",
            f"Mood/Tone: {request.mood if request.mood else 'engaging and immersive'}",
            f"Themes: {request.themes if request.themes else 'character development and plot progression'}",
            "",
            "STORY ELEMENTS:",
            f"Plot: {request.plot}",
            f"Setting: {request.when_where}",
            f"Characters: {request.characters}",
            f"Timeline/Key Events: {request.timeline}",
        ]
        
        if request.additional_notes:
            prompt_parts.extend([
                "",
                "ADDITIONAL REQUIREMENTS:",
                request.additional_notes
            ])
        
        # Add genre-specific guidelines
        if request.genre.lower() in ["comedy", "satire", "deadpan", "absurdist"]:
            prompt_parts.extend([
                "",
                "COMEDY WRITING GUIDELINES:",
                "- Include humor, wit, or satire as appropriate",
                "- Create funny situations, dialogue, or observations",
                "- Use comedic timing and pacing",
                "- Balance humor with story progression"
            ])
        else:
            prompt_parts.extend([
                "",
                "WRITING GUIDELINES:",
                f"- Write in {request.point_of_view} perspective",
                f"- Maintain a {request.mood if request.mood else 'consistent and engaging'} tone throughout",
                f"- Target {request.target_audience} readers with appropriate complexity and themes",
                f"- Length should be {request.story_length} (approximately {'500-800 words' if request.story_length == 'short' else '1500-2500 words' if request.story_length == 'medium' else '3000-5000 words'})",
                f"- Incorporate the themes: {request.themes if request.themes else 'growth, conflict, and resolution'}",
                "- Create vivid, immersive descriptions",
                "- Develop compelling character arcs",
                "- Build tension and maintain reader engagement",
                "- Deliver a satisfying conclusion"
            ])
        
        prompt_parts.extend([
            "",
            "Write the complete story now:"
        ])
    
    prompt = "\n".join(prompt_parts)
    
    # Adjust system prompt based on genre
    if request.genre.lower() == "biography":
        system_prompt = f"""You are a master biographer specializing in {request.writing_style if request.writing_style else 'engaging life stories'}. 
        You write compelling biographies that capture the essence of real people's lives, 
        their struggles, triumphs, and lasting impact. Your biographies resonate with {request.target_audience} audiences 
        through authentic storytelling and thoughtful analysis of {request.themes if request.themes else 'human experience and legacy'}."""
    elif request.genre.lower() in ["comedy", "satire", "deadpan", "absurdist"]:
        system_prompt = f"""You are a master comedic writer specializing in {request.genre} fiction. 
        You write in the style of {request.writing_style if request.writing_style else 'brilliant comedy writers'}, 
        creating hilarious narratives that resonate with {request.target_audience} audiences. 
        Your work is known for its wit, timing, and clever exploration of {request.themes if request.themes else 'human absurdity and social commentary'}."""
    else:
        system_prompt = f"""You are a master storyteller specializing in {request.genre} fiction. 
        You write in the style of {request.writing_style}, creating immersive narratives 
        that resonate with {request.target_audience} audiences. Your stories are known for 
        their vivid descriptions, compelling characters, and engaging plots that explore 
        themes of {request.themes if request.themes else 'human experience and growth'}."""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Story generation failed: {str(e)}")

# Routes
@app.post("/api/auth/signup")
def signup(user: UserCreate):
    # Validate input
    if not user.email or not user.password or not user.full_name:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    if len(user.password) < 3:
        raise HTTPException(status_code=400, detail="Password must be at least 3 characters")
    
    # Check if user exists
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user (hash password)
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    users[user.email] = {
        "id": len(users) + 1,
        "email": user.email,
        "password": hashed_password,
        "full_name": user.full_name
    }
    
    # Create token
    token = jwt.encode({"user_id": users[user.email]["id"]}, SECRET_KEY)
    return {"access_token": token, "user": {"id": users[user.email]["id"], "email": user.email}}

@app.post("/api/auth/login")
def login(user: UserLogin):
    # Validate input
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    if user.email not in users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if users[user.email]["password"] != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"user_id": users[user.email]["id"]}, SECRET_KEY)
    return {"access_token": token, "user": {"id": users[user.email]["id"], "email": user.email}}

@app.post("/api/stories/generate")
def generate_story(request: StoryRequest):
    try:
        # Generate story content
        content = generate_story_content(request)
        
        # Generate cover if requested
        cover_info = None
        if request.generate_cover:
            cover_info = generate_real_cover_image(request)
        
        # Split into chapters if requested
        chapters = []
        if request.split_into_chapters:
            chapters = split_into_chapters(content, request.num_chapters)
        
        # Save story (in memory)
        story_id = len(stories) + 1
        story_data = {
            "id": story_id,
            "plot": request.plot,
            "when_where": request.when_where,
            "characters": request.characters,
            "genre": request.genre,
            "writing_style": request.writing_style,
            "timeline": request.timeline,
            "content": content,
            "title": request.title or "Untitled Story",
            "author_name": request.author_name or "Anonymous",
            "cover_info": cover_info,
            "chapters": chapters,
            "photos": {},  # Store uploaded photos
            "created_at": datetime.now().isoformat()
        }
        
        stories[story_id] = story_data
        
        # Generate exports
        exports = {
            "pdf": export_to_pdf(story_data, request),
            "word": export_to_word(story_data, request),
            "text": export_to_text(story_data, request)
        }
        
        return {
            "id": story_id,
            "content": content,
            "title": request.title or "Untitled Story",
            "author": request.author_name or "Anonymous",
            "cover_info": cover_info,
            "chapters": chapters,
            "exports": exports,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/edit-chapter")
def edit_chapter(edit: ChapterEdit):
    try:
        if edit.story_id not in stories:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = stories[edit.story_id]
        
        # Update chapter content
        for i, chapter in enumerate(story["chapters"]):
            if chapter["chapter_number"] == edit.chapter_number:
                story["chapters"][i]["content"] = edit.chapter_content
                break
        else:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        # Rebuild full story from chapters
        story["content"] = rebuild_story_from_chapters(story["chapters"])
        
        # Regenerate exports with updated content
        request = StoryRequest(
            plot=story["plot"],
            when_where=story["when_where"],
            characters=story["characters"],
            genre=story["genre"],
            writing_style=story["writing_style"],
            timeline=story["timeline"],
            title=story["title"],
            author_name=story["author_name"]
        )
        
        story["exports"] = {
            "pdf": export_to_pdf(story, request),
            "word": export_to_word(story, request),
            "text": export_to_text(story, request)
        }
        
        return {"message": "Chapter updated successfully", "content": story["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/upload-photo")
def upload_photo(upload: PhotoUpload):
    try:
        if upload.story_id not in stories:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = stories[upload.story_id]
        
        # Store photo as-is (no processing)
        if "photos" not in story:
            story["photos"] = {}
        
        story["photos"][upload.photo_type] = {
            "data": upload.photo_data,
            "filename": upload.filename,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {"message": f"{upload.photo_type} photo uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stories/{story_id}")
def get_story(story_id: int):
    try:
        if story_id not in stories:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return stories[story_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Ultra Simple Story Generator API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
