# PRODUCTION IMPLEMENTATION PRIORITY MATRIX
"""
IMPLEMENTATION ORDER WITH SPECIFIC CODE EXAMPLES
Start Here → Go Here → Finish Here
"""

# =============================================================================
# 🚀 PHASE 1: CRITICAL INFRASTRUCTURE (Week 1-2)
# =============================================================================

PHASE_1_CRITICAL = {
    "1_Database_Setup": {
        "description": "Replace in-memory storage with PostgreSQL",
        "priority": "🔴 CRITICAL",
        "time": "3-4 days",
        "code_example": """
# database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/storygen")

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String, default="free")

# models/story.py
class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text)
    genre = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cover_image_url = Column(String)
    is_published = Column(Boolean, default=False)
""",
        "files_to_create": [
            "database.py",
            "models/__init__.py",
            "models/user.py", 
            "models/story.py",
            "alembic/versions/001_initial.py"
        ]
    },
    
    "2_Error_Handling_Logging": {
        "description": "Comprehensive error handling and structured logging",
        "priority": "🔴 CRITICAL", 
        "time": "2-3 days",
        "code_example": """
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

def setup_logging():
    # Structured JSON logging
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    # Sentry for error tracking
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration(auto_enabling_integrations=False)]
    )

# exceptions.py
class StoryGeneratorException(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class InsufficientCreditsError(StoryGeneratorException):
    def __init__(self, message: str = "Insufficient credits for story generation"):
        super().__init__(message, "INSUFFICIENT_CREDITS")

class StoryGenerationError(StoryGeneratorException):
    def __init__(self, message: str = "Failed to generate story"):
        super().__init__(message, "GENERATION_FAILED")

# error_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def story_generator_exception_handler(request: Request, exc: StoryGeneratorException):
    logger.error(
        "Story generator error",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "path": str(request.url),
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.error_code or "UNKNOWN_ERROR",
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
""",
        "files_to_create": [
            "logging_config.py",
            "exceptions.py",
            "error_handlers.py"
        ]
    },
    
    "3_Rate_Limiting": {
        "description": "API rate limiting and abuse prevention",
        "priority": "🔴 CRITICAL",
        "time": "2-3 days", 
        "code_example": """
# rate_limiter.py
import redis
import time
from typing import Optional
from fastapi import Request, HTTPException
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed
        Returns: (allowed, remaining_requests)
        """
        current_time = int(time.time())
        window_start = current_time - window
        
        # Clean old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = self.redis.zcard(key)
        
        if current_requests >= limit:
            return False, 0
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return True, limit - current_requests - 1

# middleware.py
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name())
rate_limiter = RateLimiter(redis_client)

async def rate_limit_middleware(request: Request, call_next):
    # Get user from JWT or IP for anonymous
    user_id = getattr(request.state, 'user_id', request.client.host)
    
    # Different limits based on subscription tier
    tier = getattr(request.state, 'subscription_tier', 'free')
    
    limits = {
        'free': {'requests': 10, 'window': 3600},  # 10/hour
        'basic': {'requests': 100, 'window': 3600},  # 100/hour  
        'pro': {'requests': 1000, 'window': 3600},  # 1000/hour
        'enterprise': {'requests': 10000, 'window': 3600}  # 10000/hour
    }
    
    limit_config = limits.get(tier, limits['free'])
    key = f"rate_limit:{user_id}"
    
    allowed, remaining = rate_limiter.is_allowed(
        key, 
        limit_config['requests'], 
        limit_config['window']
    )
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for {user_id}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please upgrade your plan."
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
""",
        "files_to_create": [
            "rate_limiter.py",
            "middleware.py",
            "redis_config.py"
        ]
    },
    
    "4_Security_Hardening": {
        "description": "Input validation and security measures",
        "priority": "🔴 CRITICAL",
        "time": "2-3 days",
        "code_example": """
# validators.py
from pydantic import BaseModel, validator, EmailStr
import re
from typing import Optional

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
    
    @validator('plot')
    def validate_plot(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Plot must be at least 10 characters long')
        if len(v) > 5000:
            raise ValueError('Plot cannot exceed 5000 characters')
        # Sanitize input
        return re.sub(r'[<>"\']', '', v.strip())
    
    @validator('genre')
    def validate_genre(cls, v):
        allowed_genres = [
            'fantasy', 'scifi', 'mystery', 'romance', 'thriller',
            'horror', 'adventure', 'historical', 'literary',
            'comedy', 'satire', 'deadpan', 'absurdist', 'biography'
        ]
        if v.lower() not in allowed_genres:
            raise ValueError(f'Genre must be one of: {", ".join(allowed_genres)}')
        return v.lower()

# security.py
import bcrypt
import secrets
from typing import Optional

class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Basic HTML sanitization"""
        import html
        return html.escape(text)

# middleware.py (Security headers)
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
""",
        "files_to_create": [
            "validators.py",
            "security.py",
            "middleware_security.py"
        ]
    },
    
    "5_Monitoring": {
        "description": "Application monitoring and health checks",
        "priority": "🔴 CRITICAL",
        "time": "2 days",
        "code_example": """
# health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
import redis
import time
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Basic health check"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        }
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with metrics"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time,
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent
    }

# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
STORIES_GENERATED = Counter('stories_generated_total', 'Total stories generated')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
""",
        "files_to_create": [
            "health.py",
            "monitoring.py",
            "metrics.py"
        ]
    }
}

# =============================================================================
# 🚀 PHASE 2: HIGH PRIORITY (Week 3-4)
# =============================================================================

PHASE_2_HIGH = {
    "6_User_Management": {
        "description": "Complete user profile and story management",
        "priority": "🟡 HIGH",
        "time": "4-5 days",
        "code_example": """
# services/user_service.py
from sqlalchemy.orm import Session
from .models.user import User
from .models.story import Story
from .security import SecurityManager
from typing import Optional, List

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email: str, password: str, full_name: str) -> User:
        """Create new user"""
        hashed_password = SecurityManager.hash_password(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user_preferences(self, user_id: int, preferences: dict) -> User:
        """Update user preferences"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update preferences (add preferences table as needed)
        for key, value in preferences.items():
            setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_stories(self, user_id: int, limit: int = 50) -> List[Story]:
        """Get user's stories"""
        return self.db.query(Story).filter(
            Story.user_id == user_id
        ).order_by(Story.created_at.desc()).limit(limit).all()

# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .services.user_service import UserService
from .validators import UserUpdateRequest

router = APIRouter()

@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    user_service = UserService(db)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "created_at": current_user.created_at
    }

@router.put("/me")
async def update_current_user(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    user_service = UserService(db)
    updated_user = user_service.update_user_preferences(
        current_user.id, 
        user_update.dict(exclude_unset=True)
    )
    
    return {"message": "Profile updated successfully"}

@router.get("/me/stories")
async def get_my_stories(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's stories"""
    user_service = UserService(db)
    stories = user_service.get_user_stories(current_user.id, limit)
    
    return {
        "stories": [
            {
                "id": story.id,
                "title": story.title,
                "genre": story.genre,
                "created_at": story.created_at,
                "updated_at": story.updated_at,
                "is_published": story.is_published
            }
            for story in stories
        ]
    }
""",
        "files_to_create": [
            "services/user_service.py",
            "services/story_service.py",
            "routes/users.py",
            "routes/library.py"
        ]
    },
    
    "7_File_Storage": {
        "description": "AWS S3 integration for file storage",
        "priority": "🟡 HIGH",
        "time": "3-4 days",
        "code_example": """
# storage.py
import boto3
import os
from typing import Optional, BinaryIO
from botocore.exceptions import NoCredentialsError, ClientError
import uuid
from PIL import Image
import io

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    def upload_file(
        self, 
        file_data: BinaryIO, 
        file_name: str, 
        content_type: str,
        folder: str = "uploads"
    ) -> str:
        """Upload file to S3 and return URL"""
        # Generate unique filename
        unique_filename = f"{folder}/{uuid.uuid4()}_{file_name}"
        
        try:
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                unique_filename,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Make files publicly accessible
                }
            )
            
            # Return public URL
            return f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def upload_image(self, image_data: bytes, file_name: str, folder: str = "images") -> str:
        """Upload and optimize image"""
        # Optimize image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        max_size = (1920, 1080)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85, optimize=True)
        img_buffer.seek(0)
        
        return self.upload_file(
            img_buffer, 
            file_name, 
            'image/jpeg',
            folder
        )
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            # Extract key from URL
            key = file_url.split(f"https://{self.bucket_name}.s3.amazonaws.com/")[-1]
            
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
            
        except ClientError as e:
            print(f"Failed to delete file: {str(e)}")
            return False

# services/file_service.py
from .storage import S3Storage
from typing import Optional

class FileService:
    def __init__(self):
        self.storage = S3Storage()
    
    def upload_cover_image(self, image_data: bytes, story_id: int) -> str:
        """Upload story cover image"""
        file_name = f"story_{story_id}_cover.jpg"
        return self.storage.upload_image(image_data, file_name, "covers")
    
    def upload_author_photo(self, image_data: bytes, user_id: int) -> str:
        """Upload author profile photo"""
        file_name = f"user_{user_id}_author.jpg"
        return self.storage.upload_image(image_data, file_name, "authors")
    
    def upload_export_file(self, file_data: bytes, story_id: int, format: str) -> str:
        """Upload export file (PDF, DOCX, TXT)"""
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        
        file_name = f"story_{story_id}_export.{format}"
        content_type = content_types.get(format, 'application/octet-stream')
        
        return self.storage.upload_file(
            io.BytesIO(file_data),
            file_name,
            content_type,
            "exports"
        )
""",
        "files_to_create": [
            "storage.py",
            "services/file_service.py",
            "routes/files.py"
        ]
    },
    
    "8_Testing_Suite": {
        "description": "Comprehensive testing coverage",
        "priority": "🟡 HIGH",
        "time": "3-4 days",
        "code_example": """
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from .main import app
from .database import get_db, Base
from .models.user import User
from .models.story import Story

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# tests/test_stories.py
import pytest
from fastapi.testclient import TestClient

class TestStoryGeneration:
    def test_generate_story_success(self, client: TestClient, test_user):
        """Test successful story generation"""
        # Login first
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        story_data = {
            "plot": "A detective solves a mystery in Victorian London",
            "when_where": "Victorian London, 1888",
            "characters": "Detective Sherlock Holmes, Dr. Watson",
            "genre": "mystery",
            "writing_style": "Arthur Conan Doyle",
            "timeline": "1. Murder occurs 2. Investigation begins 3. Clues found 4. Mystery solved",
            "title": "The Victorian Mystery",
            "author_name": "Test Author",
            "generate_cover": True
        }
        
        response = client.post("/api/stories/generate", json=story_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "id" in data
        assert "cover_info" in data
        assert len(data["content"]) > 100
    
    def test_generate_story_invalid_genre(self, client: TestClient, test_user):
        """Test story generation with invalid genre"""
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com", 
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        story_data = {
            "plot": "Test plot",
            "when_where": "Test setting",
            "characters": "Test characters",
            "genre": "invalid_genre",  # Invalid genre
            "writing_style": "Test style",
            "timeline": "Test timeline"
        }
        
        response = client.post("/api/stories/generate", json=story_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self, client: TestClient, test_user):
        """Test rate limiting"""
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        story_data = {
            "plot": "Test plot",
            "when_where": "Test setting", 
            "characters": "Test characters",
            "genre": "fantasy",
            "writing_style": "Test style",
            "timeline": "Test timeline"
        }
        
        # Make multiple requests quickly
        responses = []
        for _ in range(15):  # Exceed free tier limit of 10/hour
            response = client.post("/api/stories/generate", json=story_data, headers=headers)
            responses.append(response)
        
        # Should hit rate limit
        assert any(r.status_code == 429 for r in responses)

# tests/test_integration.py
class TestIntegration:
    def test_full_user_journey(self, client: TestClient):
        """Test complete user journey from signup to story generation"""
        # 1. Signup
        signup_data = {
            "email": "journey@example.com",
            "password": "password123",
            "full_name": "Journey User"
        }
        
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 200
        token = signup_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get user profile
        profile_response = client.get("/api/users/me", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "journey@example.com"
        
        # 3. Generate story
        story_data = {
            "plot": "A space adventure to Mars",
            "when_where": "Mars colony, 2150",
            "characters": "Commander Sarah, robot assistant",
            "genre": "scifi",
            "writing_style": "Arthur C. Clarke",
            "timeline": "1. Launch 2. Journey 3. Arrival 4. Discovery",
            "title": "Mars Adventure",
            "author_name": "Journey User"
        }
        
        story_response = client.post("/api/stories/generate", json=story_data, headers=headers)
        assert story_response.status_code == 200
        
        story_id = story_response.json()["id"]
        
        # 4. Get user's stories
        library_response = client.get("/api/users/me/stories", headers=headers)
        assert library_response.status_code == 200
        stories = library_response.json()["stories"]
        assert len(stories) == 1
        assert stories[0]["id"] == story_id
        
        # 5. Get specific story
        story_detail_response = client.get(f"/api/stories/{story_id}", headers=headers)
        assert story_detail_response.status_code == 200
        assert story_detail_response.json()["title"] == "Mars Adventure"

# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
""",
        "files_to_create": [
            "conftest.py",
            "tests/test_stories.py",
            "tests/test_users.py",
            "tests/test_integration.py",
            "pytest.ini"
        ]
    }
}

print("🚀 IMPLEMENTATION ROADMAP READY!")
print("📊 Phase 1 (Critical): 5 items, 11-15 days")
print("📈 Phase 2 (High): 3 items, 10-13 days")
print("⏱️ Total Time: 3-4 weeks to production ready!")
print("💰 Cost: $160-600/month + development time")
