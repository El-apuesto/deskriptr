# ERROR HANDLING & LOGGING - IMMEDIATE FIX
# Replace basic error handling with comprehensive logging system

import logging
import sys
import traceback
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# =============================================================================
# STEP 1: STRUCTURED LOGGING SETUP
# =============================================================================

def setup_production_logging():
    """Setup structured JSON logging for production"""
    
    # Remove default handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    
    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    
    # JSON formatter for structured logs
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add extra fields if available
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'story_id'):
                log_entry['story_id'] = record.story_id
            if hasattr(record, 'error_code'):
                log_entry['error_code'] = record.error_code
                
            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": traceback.format_exception(*record.exc_info)
                }
            
            return json.dumps(log_entry)
    
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    
    return logger

# =============================================================================
# STEP 2: SENTRY ERROR TRACKING
# =============================================================================

def setup_sentry():
    """Setup Sentry for error tracking and alerting"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration()
            ],
            traces_sample_rate=0.1,  # Sample 10% of requests for performance
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("APP_VERSION", "1.0.0")
        )
        print("✅ Sentry initialized for error tracking")
    else:
        print("⚠️ SENTRY_DSN not found, error tracking disabled")

# =============================================================================
# STEP 3: CUSTOM EXCEPTION CLASSES
# =============================================================================

class StoryGeneratorException(Exception):
    """Base exception for story generator"""
    def __init__(self, message: str, error_code: str = None, user_id: int = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.user_id = user_id
        super().__init__(self.message)

class InsufficientCreditsError(StoryGeneratorException):
    """User doesn't have enough credits"""
    def __init__(self, user_id: int = None):
        super().__init__(
            "Insufficient credits for story generation. Please upgrade your plan.",
            "INSUFFICIENT_CREDITS",
            user_id
        )

class StoryGenerationError(StoryGeneratorException):
    """Story generation failed"""
    def __init__(self, message: str = "Failed to generate story", user_id: int = None, story_id: int = None):
        super().__init__(message, "GENERATION_FAILED", user_id)
        self.story_id = story_id

class DatabaseError(StoryGeneratorException):
    """Database operation failed"""
    def __init__(self, message: str = "Database operation failed", user_id: int = None):
        super().__init__(message, "DATABASE_ERROR", user_id)

class ValidationError(StoryGeneratorException):
    """Input validation failed"""
    def __init__(self, message: str = "Invalid input data", field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field

class RateLimitError(StoryGeneratorException):
    """Rate limit exceeded"""
    def __init__(self, user_id: int = None):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            "RATE_LIMIT_EXCEEDED",
            user_id
        )

class ExternalAPIError(StoryGeneratorException):
    """External API (Groq) failed"""
    def __init__(self, message: str = "External service unavailable", api_name: str = None):
        super().__init__(message, "EXTERNAL_API_ERROR")
        self.api_name = api_name

# =============================================================================
# STEP 4: LOGGING DECORATORS
# =============================================================================

import functools
import uuid

def log_operation(operation_name: str):
    """Decorator to log operations with context"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = datetime.utcnow()
            
            logger = logging.getLogger(func.__module__)
            
            # Log operation start
            logger.info(
                f"Starting {operation_name}",
                extra={
                    "operation": operation_name,
                    "request_id": request_id,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log operation success
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(
                    f"Completed {operation_name}",
                    extra={
                        "operation": operation_name,
                        "request_id": request_id,
                        "duration_seconds": duration,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                # Log operation failure
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(
                    f"Failed {operation_name}: {str(e)}",
                    extra={
                        "operation": operation_name,
                        "request_id": request_id,
                        "duration_seconds": duration,
                        "success": False,
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator

def log_user_action(user_id: int, action: str):
    """Decorator to log user actions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            logger.info(
                f"User action: {action}",
                extra={
                    "user_id": user_id,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            try:
                result = func(*args, **kwargs)
                
                logger.info(
                    f"User action completed: {action}",
                    extra={
                        "user_id": user_id,
                        "action": action,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    f"User action failed: {action} - {str(e)}",
                    extra={
                        "user_id": user_id,
                        "action": action,
                        "success": False,
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator

# =============================================================================
# STEP 5: GLOBAL ERROR HANDLERS
# =============================================================================

logger = setup_production_logging()

async def story_generator_exception_handler(request: Request, exc: StoryGeneratorException):
    """Handle custom story generator exceptions"""
    
    # Log the error with context
    logger.error(
        f"Story generator error: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "path": str(request.url),
            "method": request.method,
            "user_id": getattr(exc, 'user_id', None),
            "story_id": getattr(exc, 'story_id', None),
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
    )
    
    # Return appropriate error response
    status_code = 400
    if exc.error_code == "INSUFFICIENT_CREDITS":
        status_code = 402  # Payment Required
    elif exc.error_code == "RATE_LIMIT_EXCEEDED":
        status_code = 429  # Too Many Requests
    elif exc.error_code == "DATABASE_ERROR":
        status_code = 503  # Service Unavailable
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    
    # Log the error with full context
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # Don't expose internal errors to users
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
    )

# =============================================================================
# STEP 6: REQUEST LOGGING MIDDLEWARE
# =============================================================================

async def request_logging_middleware(request: Request, call_next):
    """Log all incoming requests"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = datetime.utcnow()
    
    # Log request start
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
    )
    
    try:
        response = await call_next(request)
        
        # Log request completion
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": duration,
                "success": response.status_code < 400
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Log request failure
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"Request failed: {request.method} {request.url.path} - {str(e)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_seconds": duration,
                "success": False,
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        raise

# =============================================================================
# STEP 7: HEALTH CHECK WITH LOGGING
# =============================================================================

async def health_check_with_logging():
    """Health check that logs system status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        # Add your database check here
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check external APIs
    try:
        # Add your API checks here
        health_status["checks"]["external_apis"] = "healthy"
    except Exception as e:
        health_status["checks"]["external_apis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Log health check
    logger.info(
        f"Health check completed: {health_status['status']}",
        extra={
            "health_status": health_status["status"],
            "checks": health_status["checks"]
        }
    )
    
    return health_status

# =============================================================================
# STEP 8: ENVIRONMENT SETUP
# =============================================================================

ENVIRONMENT_CONFIG = {
    "SENTRY_DSN": "https://your-sentry-dsn-here",
    "ENVIRONMENT": "production",  # development, staging, production
    "APP_VERSION": "1.0.0",
    "LOG_LEVEL": "INFO"  # DEBUG, INFO, WARNING, ERROR
}

# =============================================================================
# STEP 9: DEPLOYMENT INSTRUCTIONS
# =============================================================================

DEPLOYMENT_STEPS = """
1. Install required packages:
   pip install sentry-sdk[fastapi] python-json-logger
   
2. Set environment variables:
   export SENTRY_DSN="your-sentry-dsn"
   export ENVIRONMENT="production"
   export APP_VERSION="1.0.0"
   
3. Add to your FastAPI app:
   from error_handling_fix import (
       setup_production_logging, setup_sentry,
       story_generator_exception_handler, general_exception_handler,
       request_logging_middleware
   )
   
   # Setup logging and Sentry
   setup_production_logging()
   setup_sentry()
   
   # Add middleware
   app.middleware("http", request_logging_middleware)
   
   # Add exception handlers
   app.add_exception_handler(StoryGeneratorException, story_generator_exception_handler)
   app.add_exception_handler(Exception, general_exception_handler)
   
4. Test error handling:
   - Trigger different error types
   - Check logs for structured output
   - Verify Sentry captures errors
"""

# =============================================================================
# STEP 10: EXAMPLE USAGE
# =============================================================================

@log_operation("story_generation")
@log_user_action(user_id=123, action="generate_story")
def example_story_generation(story_data: dict):
    """Example function with comprehensive logging"""
    logger = logging.getLogger(__name__)
    
    try:
        # Your story generation logic here
        logger.info("Starting Groq API call", extra={"story_length": len(story_data.get("plot", ""))})
        
        # Simulate API call
        if not story_data.get("plot"):
            raise ValidationError("Plot is required", "plot")
        
        # Simulate success
        result = {"story": "Generated story content..."}
        
        logger.info("Story generated successfully", extra={"story_id": 456})
        return result
        
    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error("Story generation failed", extra={"error_details": str(e)}, exc_info=True)
        raise StoryGenerationError(f"Failed to generate story: {str(e)}")

if __name__ == "__main__":
    # Test the logging setup
    setup_production_logging()
    setup_sentry()
    
    # Test error handling
    try:
        raise StoryGenerationError("Test error", user_id=123)
    except StoryGeneratorException as e:
        print(f"✅ Custom exception working: {e.error_code} - {e.message}")
    
    print("🎉 Error handling and logging system ready!")
