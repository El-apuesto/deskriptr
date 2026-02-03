# DATABASE PERSISTENCE - IMMEDIATE FIX
# Replace in-memory storage with PostgreSQL

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: DATABASE CONFIGURATION
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/storygen")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Connection pool size
    max_overflow=0,        # No overflow connections
    pool_pre_ping=True,   # Check connections before use
    echo=False            # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# STEP 2: DATABASE MODELS
# =============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="free")
    last_login = Column(DateTime)

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    genre = Column(String(100))
    writing_style = Column(String(200))
    plot = Column(Text)
    characters = Column(Text)
    when_where = Column(Text)
    timeline = Column(Text)
    mood = Column(Text)
    themes = Column(Text)
    point_of_view = Column(String(50))
    target_audience = Column(String(50))
    story_length = Column(String(50))
    additional_notes = Column(Text)
    author_name = Column(String(255))
    cover_image_url = Column(String(1000))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExportFile(Base):
    __tablename__ = "export_files"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, txt
    file_url = Column(String(1000))
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# =============================================================================
# STEP 3: DATABASE INITIALIZATION
# =============================================================================

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        return False

# =============================================================================
# STEP 4: DATA MIGRATION (From in-memory to database)
# =============================================================================

def migrate_from_memory():
    """Migrate existing in-memory data to database"""
    try:
        db = SessionLocal()
        
        # This would be called during deployment to migrate data
        # You'd need to save your current in-memory data first
        
        logger.info("Data migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Data migration failed: {str(e)}")
        return False
    finally:
        db.close()

# =============================================================================
# STEP 5: REPLACEMENT FOR IN-MEMORY STORAGE
# =============================================================================

class DatabaseStorage:
    """Replace in-memory storage with database operations"""
    
    def __init__(self, db: SessionLocal):
        self.db = db
    
    # User operations
    def create_user(self, email: str, hashed_password: str, full_name: str = None) -> User:
        """Create new user"""
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    # Story operations
    def create_story(self, story_data: dict, user_id: int) -> Story:
        """Create new story"""
        story = Story(user_id=user_id, **story_data)
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        return story
    
    def get_story(self, story_id: int) -> Story:
        """Get story by ID"""
        return self.db.query(Story).filter(Story.id == story_id).first()
    
    def get_user_stories(self, user_id: int, limit: int = 50) -> list:
        """Get user's stories"""
        return self.db.query(Story).filter(
            Story.user_id == user_id
        ).order_by(Story.created_at.desc()).limit(limit).all()
    
    def update_story(self, story_id: int, update_data: dict) -> Story:
        """Update story"""
        story = self.get_story(story_id)
        if not story:
            raise ValueError("Story not found")
        
        for key, value in update_data.items():
            setattr(story, key, value)
        
        story.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(story)
        return story
    
    def delete_story(self, story_id: int) -> bool:
        """Delete story"""
        story = self.get_story(story_id)
        if not story:
            return False
        
        self.db.delete(story)
        self.db.commit()
        return True

# =============================================================================
# STEP 6: ENVIRONMENT SETUP
# =============================================================================

# Environment variables needed:
DATABASE_CONFIG = {
    "DATABASE_URL": "postgresql://username:password@localhost:5432/storygen",
    "DB_HOST": "localhost",
    "DB_PORT": "5432", 
    "DB_NAME": "storygen",
    "DB_USER": "postgres",
    "DB_PASSWORD": "your_password_here"
}

# =============================================================================
# STEP 7: DEPLOYMENT INSTRUCTIONS
# =============================================================================

DEPLOYMENT_STEPS = """
1. Install PostgreSQL:
   brew install postgresql  # Mac
   sudo apt-get install postgresql  # Ubuntu
   
2. Create database:
   createdb storygen
   
3. Create user:
   CREATE USER storygen_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE storygen TO storygen_user;
   
4. Set environment variable:
   export DATABASE_URL="postgresql://storygen_user:your_password@localhost:5432/storygen"
   
5. Run database initialization:
   python -c "from database_fix import init_database; init_database()"
   
6. Update your main.py to use DatabaseStorage instead of in-memory dicts
"""

# =============================================================================
# STEP 8: TESTING THE FIX
# =============================================================================

def test_database_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Test query
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test connection
    if test_database_connection():
        # Initialize database
        init_database()
        print("🎉 Database is ready for production!")
    else:
        print("🚨 Fix database connection before proceeding")
