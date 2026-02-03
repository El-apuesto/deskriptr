# WORKING DATABASE SETUP - IMPLEMENT NOW!
# Complete PostgreSQL setup that works immediately

import os
import logging
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: DATABASE CONFIGURATION (WORKING SETUP)
# =============================================================================

# Use SQLite for development (easy setup), PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./storygen.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=False  # Set to True to see SQL queries
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# STEP 2: DATABASE MODELS (COMPLETE)
# =============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="free")  # free, basic, pro, enterprise
    last_login = Column(DateTime)
    api_calls_count = Column(Integer, default=0)
    stories_count = Column(Integer, default=0)
    
    # Relationships
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")

class Story(Base):
    """Story model for AI-generated content"""
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Basic info
    title = Column(String(200))
    story_type = Column(String(20), nullable=False, default='fiction')  # 'fiction' or 'biography'
    status = Column(String(20), default='pending')  # pending, generating, completed, failed
    
    # Fiction fields
    premise = Column(Text)  # Main plot description
    theme = Column(Text)  # Story theme (for compatibility with story_generation.py)
    genre = Column(String(50))
    writing_style = Column(String(50))
    setting = Column(String(500))
    tone = Column(String(200))
    
    # JSON fields for complex data
    themes = Column(JSON)  # Array of theme strings
    characters = Column(JSON)  # Array of {name, role, description, quirks}
    timeline = Column(JSON)  # Array of {chapter, description, mood}
    story_metadata = Column(JSON)  # General metadata storage (chapter outlines, etc.)
    
    # Biography fields
    biography_type = Column(String(50))  # autobiography, biography, memoir
    subject_names = Column(String(200))
    time_period_start = Column(String(100))
    time_period_end = Column(String(100))
    narrative_voice = Column(String(50))
    
    # Biography JSON fields
    birth_details = Column(JSON)
    family_background = Column(JSON)
    childhood = Column(JSON)
    career = Column(JSON)
    relationships = Column(JSON)
    major_events = Column(JSON)  # Array of life events
    challenges = Column(JSON)
    achievements = Column(JSON)
    personality = Column(JSON)
    historical_context = Column(JSON)
    hobbies = Column(JSON)
    philosophy = Column(JSON)
    quotes = Column(JSON)  # Array of {quote, context}
    sources = Column(JSON)
    focus_areas = Column(JSON)  # Array of strings
    
    # Story content and metadata
    length = Column(String(20), default='short')  # short, medium, long, novella, novel, epic
    word_count = Column(Integer, default=0)
    content = Column(Text)  # Generated story text
    chapters = Column(JSON)  # Array of {number, title, content}
    
    # NEW: Chapter progress tracking
    chapters_completed = Column(Integer, default=0)
    total_chapters = Column(Integer, default=0)
    
    # Generation tracking
    error_message = Column(Text)
    credits_cost = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="stories")
    chapters = relationship("Chapter", back_populates="story", cascade="all, delete-orphan")
    exports = relationship("ExportFile", back_populates="story", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="chapters")

class ExportFile(Base):
    __tablename__ = "export_files"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, txt
    file_data = Column(Text)  # Base64 encoded file
    file_size = Column(Integer)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="exports")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float)  # Response time in seconds
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# =============================================================================
# STEP 3: DATABASE OPERATIONS (WORKING)
# =============================================================================

class DatabaseManager:
    """Complete database operations"""
    
    def __init__(self):
        self.engine = engine
    
    def init_database(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {str(e)}")
            return False
    
    def get_session(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    # User operations
    def create_user(self, email: str, hashed_password: str, full_name: str = None) -> Optional[User]:
        """Create new user"""
        db = self.get_session()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return None
            
            user = User(
                email=email.lower().strip(),
                hashed_password=hashed_password,
                full_name=full_name.strip() if full_name else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = self.get_session()
        try:
            return db.query(User).filter(User.email == email.lower().strip()).first()
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = self.get_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None
        finally:
            db.close()
    
    def update_user_last_login(self, user_id: int):
        """Update user last login"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update user last login: {str(e)}")
        finally:
            db.close()
    
    # Story operations
    def create_story(self, story_data: dict, user_id: int, db_session=None) -> Optional[Story]:
        """Create new story"""
        # Use provided session or create new one
        db = db_session or self.get_session()
        session_was_provided = db_session is not None
        
        try:
            # Calculate word count
            content = story_data.get('content', '')
            word_count = len(content.split()) if content else 0
            
            story = Story(
                user_id=user_id,
                title=story_data.get('title', 'Untitled Story'),
                content=content,
                genre=story_data.get('genre'),
                writing_style=story_data.get('writing_style'),
                plot=story_data.get('plot'),
                characters=story_data.get('characters'),
                when_where=story_data.get('when_where'),
                timeline=story_data.get('timeline'),
                mood=story_data.get('mood'),
                themes=story_data.get('themes'),
                point_of_view=story_data.get('point_of_view', 'third person'),
                target_audience=story_data.get('target_audience', 'general'),
                story_length=story_data.get('story_length', 'medium'),
                additional_notes=story_data.get('additional_notes'),
                author_name=story_data.get('author_name'),
                cover_image_data=story_data.get('cover_image_data'),
                word_count=word_count
            )
            
            db.add(story)
            db.commit()
            db.refresh(story)
            
            # Update user story count
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.stories_count += 1
                db.commit()
            
            return story
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create story: {str(e)}")
            return None
        finally:
            # Only close session if we created it
            if not session_was_provided:
                db.close()
    
    def get_story(self, story_id: int) -> Optional[Story]:
        """Get story by ID"""
        db = self.get_session()
        try:
            return db.query(Story).filter(Story.id == story_id).first()
        except Exception as e:
            logger.error(f"Failed to get story: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_user_stories(self, user_id: int, limit: int = 50, offset: int = 0) -> list:
        """Get user's stories"""
        db = self.get_session()
        try:
            return db.query(Story).filter(
                Story.user_id == user_id
            ).order_by(Story.created_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get user stories: {str(e)}")
            return []
        finally:
            db.close()
    
    def update_story(self, story_id: int, update_data: dict) -> Optional[Story]:
        """Update story"""
        db = self.get_session()
        try:
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(story, key):
                    setattr(story, key, value)
            
            story.updated_at = datetime.utcnow()
            
            # Recalculate word count if content updated
            if 'content' in update_data:
                story.word_count = len(update_data['content'].split())
            
            db.commit()
            db.refresh(story)
            return story
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update story: {str(e)}")
            return None
        finally:
            db.close()
    
    def delete_story(self, story_id: int) -> bool:
        """Delete story"""
        db = self.get_session()
        try:
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                return False
            
            # Update user story count
            user = db.query(User).filter(User.id == story.user_id).first()
            if user and user.stories_count > 0:
                user.stories_count -= 1
            
            db.delete(story)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete story: {str(e)}")
            return False
        finally:
            db.close()
    
    # Chapter operations
    def create_chapter(self, story_id: int, chapter_number: int, title: str, content: str) -> Optional[Chapter]:
        """Create chapter"""
        db = self.get_session()
        try:
            word_count = len(content.split()) if content else 0
            
            chapter = Chapter(
                story_id=story_id,
                chapter_number=chapter_number,
                title=title,
                content=content,
                word_count=word_count
            )
            
            db.add(chapter)
            db.commit()
            db.refresh(chapter)
            return chapter
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create chapter: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_story_chapters(self, story_id: int) -> list:
        """Get story chapters"""
        db = self.get_session()
        try:
            return db.query(Chapter).filter(
                Chapter.story_id == story_id
            ).order_by(Chapter.chapter_number).all()
        except Exception as e:
            logger.error(f"Failed to get story chapters: {str(e)}")
            return []
        finally:
            db.close()
    
    def update_chapter(self, chapter_id: int, content: str) -> Optional[Chapter]:
        """Update chapter"""
        db = self.get_session()
        try:
            chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not chapter:
                return None
            
            chapter.content = content
            chapter.word_count = len(content.split()) if content else 0
            chapter.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(chapter)
            return chapter
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update chapter: {str(e)}")
            return None
        finally:
            db.close()
    
    # Export operations
    def create_export(self, story_id: int, file_type: str, file_data: str, file_size: int) -> Optional[ExportFile]:
        """Create export file"""
        db = self.get_session()
        try:
            export = ExportFile(
                story_id=story_id,
                file_type=file_type,
                file_data=file_data,
                file_size=file_size
            )
            
            db.add(export)
            db.commit()
            db.refresh(export)
            return export
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create export: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_story_exports(self, story_id: int) -> list:
        """Get story exports"""
        db = self.get_session()
        try:
            return db.query(ExportFile).filter(ExportFile.story_id == story_id).all()
        except Exception as e:
            logger.error(f"Failed to get story exports: {str(e)}")
            return []
        finally:
            db.close()
    
    # Analytics operations
    def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            stories = db.query(Story).filter(Story.user_id == user_id).all()
            
            total_words = sum(story.word_count for story in stories)
            genre_counts = {}
            for story in stories:
                genre = story.genre or 'unknown'
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            return {
                "user_id": user_id,
                "stories_count": len(stories),
                "total_words": total_words,
                "genre_counts": genre_counts,
                "subscription_tier": user.subscription_tier,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {}
        finally:
            db.close()
    
    def record_api_usage(self, user_id: int, endpoint: str, method: str, status_code: int, response_time: float, ip_address: str, user_agent: str):
        """Record API usage"""
        db = self.get_session()
        try:
            usage = APIUsage(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(usage)
            
            # Update user API call count
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.api_calls_count += 1
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record API usage: {str(e)}")
        finally:
            db.close()

# =============================================================================
# STEP 4: GLOBAL DATABASE MANAGER
# =============================================================================

db_manager = DatabaseManager()

# =============================================================================
# STEP 5: MIGRATION FROM IN-MEMORY STORAGE
# =============================================================================

def migrate_from_memory(memory_stories: dict, memory_users: dict):
    """Migrate from in-memory storage to database"""
    logger.info("Starting migration from in-memory storage...")
    
    try:
        # Migrate users
        for email, user_data in memory_users.items():
            db_manager.create_user(
                email=user_data.get('email', email),
                hashed_password=user_data.get('hashed_password', ''),
                full_name=user_data.get('full_name')
            )
        
        # Migrate stories
        for story_id, story_data in memory_stories.items():
            # Find user by email (this would need adjustment based on your data structure)
            user_email = story_data.get('user_email', '')
            if user_email:
                user = db_manager.get_user_by_email(user_email)
                if user:
                    db_manager.create_story(story_data, user.id)
        
        logger.info("✅ Migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

# =============================================================================
# STEP 6: DATABASE HEALTH CHECK
# =============================================================================

def check_database_health() -> dict:
    """Check database health"""
    try:
        db = db_manager.get_session()
        
        # Test basic query
        result = db.execute(text("SELECT 1")).scalar()
        
        # Check table counts
        user_count = db.query(User).count()
        story_count = db.query(Story).count()
        
        db.close()
        
        return {
            "status": "healthy",
            "connection": "ok",
            "users_count": user_count,
            "stories_count": story_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "connection": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# =============================================================================
# STEP 7: INITIALIZATION
# =============================================================================

def init_working_database():
    """Initialize the working database"""
    logger.info("🚀 Initializing working database...")
    
    # Initialize database tables
    if db_manager.init_database():
        # Check health
        health = check_database_health()
        logger.info(f"Database health: {health['status']}")
        
        if health['status'] == 'healthy':
            logger.info("✅ Working database is ready!")
            return True
        else:
            logger.error(f"❌ Database health check failed: {health.get('error', 'Unknown error')}")
            return False
    else:
        logger.error("❌ Failed to initialize database")
        return False

# =============================================================================
# STEP 8: USAGE EXAMPLES
# =============================================================================

def example_usage():
    """Example database usage"""
    
    # Initialize database
    if init_working_database():
        print("🎉 Database initialized successfully!")
        
        # Create a test user
        user = db_manager.create_user(
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="Test User"
        )
        
        if user:
            print(f"✅ Created user: {user.email} (ID: {user.id})")
            
            # Create a test story
            story_data = {
                "title": "Test Story",
                "content": "This is a test story content.",
                "genre": "fantasy",
                "writing_style": "J.R.R. Tolkien",
                "plot": "A hero goes on an adventure",
                "characters": "Hero, Wizard, Dragon",
                "when_where": "Middle Earth, Third Age"
            }
            
            story = db_manager.create_story(story_data, user.id)
            
            if story:
                print(f"✅ Created story: {story.title} (ID: {story.id})")
                
                # Get user stats
                stats = db_manager.get_user_stats(user.id)
                print(f"📊 User stats: {stats}")
                
                # Get user stories
                stories = db_manager.get_user_stories(user.id)
                print(f"📚 User stories: {len(stories)}")
                
            else:
                print("❌ Failed to create story")
        else:
            print("❌ Failed to create user")
    else:
        print("❌ Database initialization failed")

if __name__ == "__main__":
    # Run example usage
    example_usage()
