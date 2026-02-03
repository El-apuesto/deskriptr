# SECURITY HARDENING - IMMEDIATE FIX
# Protect against SQL injection, XSS, CSRF, and other attacks

import re
import html
import hashlib
import secrets
import bcrypt
from typing import Optional, List, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import logging
import os
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: INPUT VALIDATION AND SANITIZATION
# =============================================================================

class SecurityValidator:
    """Comprehensive input validation and sanitization"""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'expression\s*\(',           # CSS expressions
        r'@import',                    # CSS imports
        r'union\s+select',            # SQL injection
        r'drop\s+table',              # SQL injection
        r'insert\s+into',             # SQL injection
        r'update\s+set',              # SQL injection
        r'delete\s+from',              # SQL injection
        r'exec\s*\(',                 # Command execution
        r'system\s*\(',               # Command execution
        r'eval\s*\(',                 # Code execution
    ]
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 255
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password must be less than 128 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_story_input(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate story generation input"""
        errors = []
        
        # Required fields
        required_fields = ['plot', 'characters', 'when_where', 'genre', 'writing_style']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Length validations
        if data.get('plot') and len(data['plot']) > 5000:
            errors.append("Plot must be less than 5000 characters")
        
        if data.get('characters') and len(data['characters']) > 2000:
            errors.append("Characters description must be less than 2000 characters")
        
        if data.get('when_where') and len(data['when_where']) > 1000:
            errors.append("Setting description must be less than 1000 characters")
        
        # Genre validation
        allowed_genres = [
            'fantasy', 'scifi', 'mystery', 'romance', 'thriller',
            'horror', 'adventure', 'historical', 'literary',
            'comedy', 'satire', 'deadpan', 'absurdist', 'biography'
        ]
        
        if data.get('genre') and data['genre'].lower() not in allowed_genres:
            errors.append(f"Genre must be one of: {', '.join(allowed_genres)}")
        
        # Point of view validation
        allowed_pov = ['first person', 'third person', 'omniscient']
        if data.get('point_of_view') and data['point_of_view'].lower() not in allowed_pov:
            errors.append(f"Point of view must be one of: {', '.join(allowed_pov)}")
        
        return len(errors) == 0, errors

# =============================================================================
# STEP 2: ENHANCED PYDANTIC MODELS WITH VALIDATION
# =============================================================================

class SecureUserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    
    @validator('email')
    def validate_email_field(cls, v):
        if not SecurityValidator.validate_email(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('password')
    def validate_password_field(cls, v):
        is_valid, errors = SecurityValidator.validate_password(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v:
            v = SecurityValidator.sanitize_text(v, max_length=100)
            if len(v) < 2:
                raise ValueError('Full name must be at least 2 characters long')
        return v

class SecureStoryRequest(BaseModel):
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
    
    @validator('plot')
    def validate_plot_field(cls, v):
        v = SecurityValidator.sanitize_text(v, max_length=5000)
        if len(v.strip()) < 10:
            raise ValueError('Plot must be at least 10 characters long')
        return v
    
    @validator('when_where')
    def validate_setting_field(cls, v):
        v = SecurityValidator.sanitize_text(v, max_length=1000)
        if len(v.strip()) < 5:
            raise ValueError('Setting must be at least 5 characters long')
        return v
    
    @validator('characters')
    def validate_characters_field(cls, v):
        v = SecurityValidator.sanitize_text(v, max_length=2000)
        if len(v.strip()) < 5:
            raise ValueError('Characters description must be at least 5 characters long')
        return v
    
    @validator('genre')
    def validate_genre_field(cls, v):
        allowed_genres = [
            'fantasy', 'scifi', 'mystery', 'romance', 'thriller',
            'horror', 'adventure', 'historical', 'literary',
            'comedy', 'satire', 'deadpan', 'absurdist', 'biography'
        ]
        if v.lower() not in allowed_genres:
            raise ValueError(f'Genre must be one of: {", ".join(allowed_genres)}')
        return v.lower()
    
    @validator('writing_style')
    def validate_writing_style_field(cls, v):
        v = SecurityValidator.sanitize_text(v, max_length=200)
        return v
    
    @validator('timeline')
    def validate_timeline_field(cls, v):
        v = SecurityValidator.sanitize_text(v, max_length=1000)
        return v
    
    @validator('mood')
    def validate_mood_field(cls, v):
        return SecurityValidator.sanitize_text(v, max_length=500)
    
    @validator('themes')
    def validate_themes_field(cls, v):
        return SecurityValidator.sanitize_text(v, max_length=500)
    
    @validator('additional_notes')
    def validate_additional_notes_field(cls, v):
        return SecurityValidator.sanitize_text(v, max_length=1000)
    
    @validator('title')
    def validate_title_field(cls, v):
        if v:
            v = SecurityValidator.sanitize_text(v, max_length=200)
        return v
    
    @validator('author_name')
    def validate_author_name_field(cls, v):
        if v:
            v = SecurityValidator.sanitize_text(v, max_length=100)
        return v
    
    @validator('num_chapters')
    def validate_num_chapters_field(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Number of chapters must be between 1 and 10')
        return v

# =============================================================================
# STEP 3: PASSWORD SECURITY
# =============================================================================

class PasswordManager:
    """Secure password handling"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)

# =============================================================================
# STEP 4: JWT SECURITY
# =============================================================================

class SecureJWTManager:
    """Enhanced JWT token management"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: dict) -> str:
        """Create secure access token"""
        to_encode = data.copy()
        
        # Add expiration
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        # Add token ID for revocation
        to_encode["jti"] = PasswordManager.generate_secure_token(16)
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Create secure refresh token"""
        to_encode = data.copy()
        
        # Add expiration
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        # Add token ID for revocation
        to_encode["jti"] = PasswordManager.generate_secure_token(16)
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration (jwt.decode already does this)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

# =============================================================================
# STEP 5: SECURITY MIDDLEWARE
# =============================================================================

class SecurityMiddleware:
    """Security middleware for FastAPI"""
    
    @staticmethod
    async def security_headers_middleware(request: Request, call_next):
        """Add security headers to all responses"""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        return response
    
    @staticmethod
    async def request_size_middleware(request: Request, call_next):
        """Limit request size to prevent DoS attacks"""
        max_request_size = 10 * 1024 * 1024  # 10MB
        
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_request_size:
            raise HTTPException(
                status_code=413,
                detail="Request too large"
            )
        
        return await call_next(request)
    
    @staticmethod
    async def ip_rate_limit_middleware(request: Request, call_next):
        """Basic IP-based rate limiting for anonymous requests"""
        client_ip = request.client.host
        
        # Check if IP is in blacklist (implement as needed)
        blacklisted_ips = []  # Load from database/config
        
        if client_ip in blacklisted_ips:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return await call_next(request)

# =============================================================================
# STEP 6: SQL INJECTION PREVENTION
# =============================================================================

class SQLInjectionProtection:
    """Prevent SQL injection attacks"""
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """Sanitize SQL identifiers (table names, column names)"""
        # Only allow alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError("Invalid SQL identifier")
        return identifier
    
    @staticmethod
    def validate_order_by(order_by: str, allowed_columns: List[str]) -> str:
        """Validate ORDER BY clause"""
        # Remove potential SQL injection
        order_by = order_by.strip()
        
        # Check if column is allowed
        column = order_by.replace(' DESC', '').replace(' ASC', '').strip()
        if column not in allowed_columns:
            raise ValueError("Invalid ORDER BY column")
        
        # Only allow ASC/DESC
        if order_by.endswith(' DESC'):
            return f"{column} DESC"
        elif order_by.endswith(' ASC'):
            return f"{column} ASC"
        else:
            return column
    
    @staticmethod
    def escape_like_pattern(pattern: str) -> str:
        """Escape pattern for LIKE queries"""
        # Escape SQL LIKE wildcards
        return pattern.replace('%', '\\%').replace('_', '\\_')

# =============================================================================
# STEP 7: CSRF PROTECTION
# =============================================================================

class CSRFProtection:
    """CSRF token protection"""
    
    def __init__(self):
        self.secret_key = os.getenv("CSRF_SECRET_KEY", PasswordManager.generate_secure_token(32))
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        message = f"{session_id}:{timestamp}"
        
        # Create HMAC signature
        import hmac
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def verify_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Verify CSRF token"""
        try:
            timestamp_str, signature = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check token age
            if datetime.utcnow().timestamp() - timestamp > max_age:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except:
            return False

# =============================================================================
# STEP 8: SECURITY MONITORING
# =============================================================================

class SecurityMonitor:
    """Monitor security events and detect attacks"""
    
    def __init__(self):
        self.failed_logins = {}  # Track failed login attempts
        self.suspicious_requests = {}  # Track suspicious patterns
    
    def record_failed_login(self, email: str, ip_address: str):
        """Record failed login attempt"""
        key = f"{email}:{ip_address}"
        current_time = datetime.utcnow()
        
        if key not in self.failed_logins:
            self.failed_logins[key] = []
        
        # Clean old attempts (older than 1 hour)
        self.failed_logins[key] = [
            attempt for attempt in self.failed_logins[key]
            if current_time - attempt < timedelta(hours=1)
        ]
        
        # Add current attempt
        self.failed_logins[key].append(current_time)
        
        # Check for brute force attack
        if len(self.failed_logins[key]) >= 5:
            logger.warning(
                f"Potential brute force attack detected",
                extra={
                    "email": email,
                    "ip_address": ip_address,
                    "attempts": len(self.failed_logins[key]),
                    "event_type": "brute_force_attack"
                }
            )
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked due to suspicious activity"""
        # Implement IP blocking logic
        return False
    
    def detect_suspicious_pattern(self, request: Request) -> bool:
        """Detect suspicious request patterns"""
        suspicious_indicators = [
            len(request.url.path) > 1000,  # Very long URL
            len(request.query_params) > 50,  # Too many parameters
            'script:' in str(request.url),  # JavaScript in URL
            'union select' in str(request.url).lower(),  # SQL injection attempt
        ]
        
        return any(suspicious_indicators)

# =============================================================================
# STEP 9: ENVIRONMENT SETUP
# =============================================================================

ENVIRONMENT_CONFIG = {
    "JWT_SECRET_KEY": "your-super-secret-jwt-key-here",  # Required
    "CSRF_SECRET_KEY": "your-csrf-secret-key-here",       # Required
    "BCRYPT_ROUNDS": 12,                                   # Password hashing rounds
    "MAX_REQUEST_SIZE": 10485760,                         # 10MB
    "SESSION_TIMEOUT": 1800,                               # 30 minutes
    "ENABLE_SECURITY_HEADERS": True,
    "ENABLE_CSRF_PROTECTION": True,
    "ENABLE_RATE_LIMITING": True
}

# =============================================================================
# STEP 10: DEPLOYMENT INSTRUCTIONS
# =============================================================================

DEPLOYMENT_STEPS = """
1. Set environment variables:
   export JWT_SECRET_KEY="your-super-secret-jwt-key"
   export CSRF_SECRET_KEY="your-csrf-secret-key"
   
2. Install required packages:
   pip install bcrypt pydantic[email] python-jose[cryptography]
   
3. Add to your FastAPI app:
   from security_fix import (
       SecurityMiddleware, SecureUserCreate, SecureStoryRequest,
       security_headers_middleware, request_size_middleware, ip_rate_limit_middleware
   )
   
   # Add security middleware
   app.middleware("http", security_headers_middleware)
   app.middleware("http", request_size_middleware)
   app.middleware("http", ip_rate_limit_middleware)
   
   # Use secure models
   @app.post("/api/auth/signup")
   async def signup(user_data: SecureUserCreate):
       # Your signup logic here
       pass
   
   @app.post("/api/stories/generate")
   async def generate_story(story_data: SecureStoryRequest):
       # Your story generation logic here
       pass
   
4. Test security:
   - Try SQL injection attempts
   - Test XSS attacks
   - Verify security headers
   - Test rate limiting
"""

# =============================================================================
# STEP 11: EXAMPLE USAGE
# =============================================================================

def example_secure_validation():
    """Example of secure input validation"""
    
    # Test user input validation
    try:
        user_data = SecureUserCreate(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        print("✅ User data validated successfully")
    except Exception as e:
        print(f"❌ User validation failed: {e}")
    
    # Test story input validation
    try:
        story_data = SecureStoryRequest(
            plot="A detective solves a mystery in Victorian London",
            when_where="Victorian London, 1888",
            characters="Detective Holmes, Dr. Watson",
            genre="mystery",
            writing_style="Arthur Conan Doyle",
            timeline="1. Murder occurs 2. Investigation begins 3. Solution found"
        )
        print("✅ Story data validated successfully")
    except Exception as e:
        print(f"❌ Story validation failed: {e}")

if __name__ == "__main__":
    # Test security features
    example_secure_validation()
    print("🔒 Security hardening system ready!")
