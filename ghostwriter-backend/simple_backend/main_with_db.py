# MAIN.PY WITH WORKING DATABASE - REPLACE YOUR CURRENT MAIN.PY
# Complete FastAPI app with database integration

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging
import os
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets
import time

# Import our working database
from working_database import (
    db_manager, init_working_database, check_database_health,
    User, Story, Chapter, ExportFile
)

# =============================================================================
# SETUP LOGGING
# =============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Story Generator API",
    description="AI-powered story generation with database persistence",
    version="2.0.0"
)

# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =============================================================================
# SECURITY SETUP
# =============================================================================

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"email": email, "user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class StoryRequest(BaseModel):
    plot: str
    when_where: str
    characters: str
    genre: str
    writing_style: str
    timeline: str
    mood: Optional[str] = ""
    themes: Optional[str] = ""
    point_of_view: str = "third person"
    target_audience: str = "general"
    story_length: str = "medium"
    additional_notes: Optional[str] = ""
    title: Optional[str] = ""
    author_name: Optional[str] = ""
    generate_cover: bool = False
    split_into_chapters: bool = True
    num_chapters: int = 3

class ChapterEdit(BaseModel):
    story_id: int
    chapter_number: int
    chapter_content: str

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/auth/signup")
async def signup(user_data: UserCreate):
    """User signup"""
    try:
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        user = db_manager.create_user(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_tier": user.subscription_tier
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """User login"""
    try:
        # Get user
        user = db_manager.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login
        db_manager.update_user_last_login(user.id)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_tier": user.subscription_tier
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
# =============================================================================
# YOUR ACTUAL PAYMENT PACKAGES
# =============================================================================

@app.get("/api/payments/packages")
async def get_credit_packages():
    """Get YOUR actual credit packages"""
    return {
        "packages": {
            "novella": {"credits": 130, "price": 1300, "name": "Novella Pack", "description": "45,000 word novella generation"},
            "premium_novella": {"credits": 150, "price": 1500, "name": "Premium Novella Pack", "description": "45,000 word novella + premium features"},
            "novel": {"credits": 210, "price": 2100, "name": "Novel Pack", "description": "90,000 word novel generation"},
            "premium_novel": {"credits": 230, "price": 2300, "name": "Premium Novel Pack", "description": "90,000 word novel + premium features"},
            "double_feature": {"credits": 390, "price": 3900, "name": "Double Feature Pack", "description": "2 novel generations"},
            "triple_feature": {"credits": 630, "price": 6300, "name": "Triple Feature Pack", "description": "3 novel generations"},
            "non_fiction_upgrade": {"credits": 50, "price": 500, "name": "Non-Fiction Upgrade", "description": "Upgrade to biography/memoir generation"}
        },
        "premium_features": {
            "about_author": "About the Author section",
            "title_page": "Professional title page", 
            "table_of_contents": "Auto-generated table of contents",
            "ai_images": "10 AI-generated cover images",
            "cover_upload": "Custom cover upload option",
            "author_photo": "Author photo upload for about page"
        }
    }

@app.post("/api/payments/create-checkout-session")
async def create_checkout_session(package: str, current_user: dict = Depends(verify_token)):
    """Create Stripe checkout session for YOUR credit packages"""
    try:
        packages = {
            "novella": {"credits": 130, "price": 1300, "name": "Novella Pack"},
            "premium_novella": {"credits": 150, "price": 1500, "name": "Premium Novella Pack"},
            "novel": {"credits": 210, "price": 2100, "name": "Novel Pack"},
            "premium_novel": {"credits": 230, "price": 2300, "name": "Premium Novel Pack"},
            "double_feature": {"credits": 390, "price": 3900, "name": "Double Feature Pack"},
            "triple_feature": {"credits": 630, "price": 6300, "name": "Triple Feature Pack"},
            "non_fiction_upgrade": {"credits": 50, "price": 500, "name": "Non-Fiction Upgrade"}
        }
        
        if package not in packages:
            raise HTTPException(status_code=400, detail=f"Invalid package. Choose from: {', '.join(packages.keys())}")
        
        pkg = packages[package]
        
        # For now, return a mock session (you'll need real Stripe integration)
        return {
            "success": True,
            "checkout_url": f"https://checkout.stripe.com/pay/mock_session_{package}",
            "session_id": f"mock_session_{package}_{current_user['user_id']}",
            "credits": pkg["credits"],
            "price_usd": pkg["price"] / 100,
            "package_name": pkg["name"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

# =============================================================================
# STORY ENDPOINTS
# =============================================================================

@app.post("/api/stories/generate", response_model=dict)
async def generate_story(
    story_data: StoryRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate a story using your original multi-step novel system"""
    try:
        # Check credits and deduct using YOUR actual credit system
        # YOUR CREDIT COSTS:
        credit_costs = {
            "short": 0,
            "medium": 0,
            "long": 0,
            "novella": 130,           # $13
            "premium_novella": 150,    # $15
            "novel": 210,             # $21
            "premium_novel": 230,      # $23
            "double_feature": 390,     # $39 (2 novels)
            "triple_feature": 630,      # $63 (3 novels)
            "non_fiction_upgrade": 50   # $5
        }
        
        story_length = story_data.story_length or "short"
        required_credits = credit_costs.get(story_length, 0)
        
        if required_credits > 0:
            # Check user credits
            user = db_manager.get_user_by_id(current_user["user_id"])
            if not user or getattr(user, 'credits_balance', 0) < required_credits:
                raise HTTPException(
                    status_code=402,
                    detail=f"Insufficient credits. Required: {required_credits} credits"
                )
            
            # Deduct credits
            db_manager.deduct_user_credits(current_user["user_id"], required_credits)
        
        # Import your original story generation system
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ghostwriter-backend'))
        
        from story_generation import generate_story, create_story_record
        
        # Create story record using your original system
        story_record_data = {
            'user_id': current_user["user_id"],
            'genre': story_data.genre,
            'theme': story_data.plot,  # Your system uses 'theme'
            'characters': story_data.characters,
            'setting': story_data.when_where,
            'length': story_data.story_length or 'novel',  # Default to novel length
            'title': story_data.title or 'Untitled Story',
            'credits_cost': required_credits
        }
        
        # Use your original database session
        db = db_manager.get_session()
        
        # Create story record using your original system
        story = create_story_record(db, story_record_data)
        
        # Start your original multi-step generation in background
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def run_story_generation():
            generate_story(
                db=db,
                story_id=story.id,
                genre=story_data.genre,
                theme=story_data.plot,
                characters=story_data.characters,
                setting=story_data.when_where,
                length=story_data.story_length or 'novel'
            )
        
        # Run in background thread
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            loop.run_in_executor(pool, run_story_generation)
        
        return {
            "id": story.id,
            "title": story.title,
            "status": story.status,
            "message": "Story generation started using your original multi-step novel system",
            "story_type": "novel_generation",
            "word_count_target": "90,000-140,000 words",
            "chapters": "12-18 chapters",
            "credits_deducted": required_credits
        }
        
    except Exception as e:
        logger.error(f"Story generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start story generation: {str(e)}"
        )
    finally:
        if 'db' in locals():
            db.close()

@app.get("/api/stories/{story_id}")
async def get_story(
    story_id: int,
    current_user: dict = Depends(verify_token)
):
    """Get a specific story"""
    try:
        story = db_manager.get_story(story_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Check if user owns the story
        if story.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get chapters
        chapters = db_manager.get_story_chapters(story_id)
        
        # Get exports
        exports = db_manager.get_story_exports(story_id)
        
        return {
            "id": story.id,
            "title": story.title,
            "content": story.content,
            "genre": story.genre,
            "writing_style": story.writing_style,
            "author_name": story.author_name,
            "cover_image_data": story.cover_image_data,
            "word_count": story.word_count,
            "created_at": story.created_at.isoformat(),
            "updated_at": story.updated_at.isoformat(),
            "chapters": [
                {
                    "id": chapter.id,
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "content": chapter.content,
                    "word_count": chapter.word_count
                }
                for chapter in chapters
            ],
            "exports": [
                {
                    "id": export.id,
                    "file_type": export.file_type,
                    "file_size": export.file_size,
                    "download_count": export.download_count,
                    "created_at": export.created_at.isoformat()
                }
                for export in exports
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get story error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get story"
        )

@app.get("/api/users/me/stories")
async def get_my_stories(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(verify_token)
):
    """Get current user's stories"""
    try:
        stories = db_manager.get_user_stories(current_user["user_id"], limit, offset)
        
        return {
            "stories": [
                {
                    "id": story.id,
                    "title": story.title,
                    "genre": story.genre,
                    "word_count": story.word_count,
                    "created_at": story.created_at.isoformat(),
                    "updated_at": story.updated_at.isoformat(),
                    "is_published": story.is_published
                }
                for story in stories
            ],
            "total": len(stories),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Get user stories error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get stories"
        )

@app.get("/api/users/me/stats")
async def get_my_stats(current_user: dict = Depends(verify_token)):
    """Get current user's statistics"""
    try:
        stats = db_manager.get_user_stats(current_user["user_id"])
        return stats
    except Exception as e:
        logger.error(f"Get user stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get stats"
        )

# =============================================================================
# CHAPTER EDITING ENDPOINTS
# =============================================================================

@app.post("/api/stories/edit-chapter")
async def edit_chapter(
    chapter_data: ChapterEdit,
    current_user: dict = Depends(verify_token)
):
    """Edit a chapter"""
    try:
        # Get story to verify ownership
        story = db_manager.get_story(chapter_data.story_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        if story.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update chapter
        chapter = db_manager.update_chapter(
            chapter_data.chapter_number,
            chapter_data.chapter_content
        )
        
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Rebuild story content from chapters
        chapters = db_manager.get_story_chapters(chapter_data.story_id)
        new_content = "\n\n".join([ch.content for ch in chapters])
        
        # Update story content
        db_manager.update_story(chapter_data.story_id, {"content": new_content})
        
        return {
            "message": "Chapter updated successfully",
            "content": new_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit chapter error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to edit chapter"
        )

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Basic health check"""
    health = check_database_health()
    return health

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Story Generator API with Database",
        "status": "running",
        "version": "2.0.0",
        "database": check_database_health()["status"]
    }

# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting Story Generator API...")
    
    # Initialize database
    if init_working_database():
        logger.info("✅ Database initialized successfully")
    else:
        logger.error("❌ Database initialization failed")
        # In production, you might want to exit here
    
    logger.info("🎉 Story Generator API is ready!")

# =============================================================================
# PLACEHOLDER FUNCTIONS (Replace with your existing implementations)
# =============================================================================

def generate_story_content(story_data):
    """Generate story content using your original multi-step novel system"""
    # Import your original story generation system
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ghostwriter-backend'))
    
    from story_generation import generate_story, create_story_record
    
    # This will use your original system that handles:
    # - 80,000-140,000 word novels
    # - Chapter-by-chapter generation
    # - Context continuity
    # - Progress tracking
    return "Using original story generation system"

def generate_cover_image(story_data):
    """Generate cover image - replace with your implementation"""
    return {
        "description": f"Cover for {story_data.title or 'Untitled Story'}",
        "style": story_data.genre,
        "title": story_data.title or "Untitled Story",
        "author": story_data.author_name or "Anonymous"
    }

def split_into_chapters(content, num_chapters):
    """Split content into chapters - replace with your implementation"""
    paragraphs = content.split('\n\n')
    chapters = []
    
    for i in range(num_chapters):
        start = i * len(paragraphs) // num_chapters
        end = (i + 1) * len(paragraphs) // num_chapters if i < num_chapters - 1 else len(paragraphs)
        
        chapter_content = '\n\n'.join(paragraphs[start:end])
        chapters.append({
            "chapter_number": i + 1,
            "title": f"Chapter {i + 1}",
            "content": chapter_content
        })
    
    return chapters

def export_to_pdf(story_data, story_request):
    """Export to PDF - replace with your implementation"""
    return "base64_encoded_pdf_data_here"

def export_to_word(story_data, story_request):
    """Export to Word - replace with your implementation"""
    return "base64_encoded_word_data_here"

def export_to_text(story_data, story_request):
    """Export to text - replace with your implementation"""
    return "base64_encoded_text_data_here"

# =============================================================================
# RUN THE APP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
