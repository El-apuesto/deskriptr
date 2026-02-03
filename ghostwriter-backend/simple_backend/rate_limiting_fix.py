# RATE LIMITING - IMMEDIATE FIX
# Prevent API abuse and cost explosion with Redis-based rate limiting

import redis
import time
import json
from typing import Optional, Tuple
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: REDIS CONFIGURATION
# =============================================================================

class RedisManager:
    """Redis connection manager for rate limiting"""
    
    def __init__(self):
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD", None),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected for rate limiting")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            # Fallback to memory-based rate limiting (less reliable)
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Global Redis manager
redis_manager = RedisManager()

# =============================================================================
# STEP 2: RATE LIMITING ENGINE
# =============================================================================

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_manager.redis_client
        self.memory_store = {}  # Fallback when Redis unavailable
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        identifier: str = None
    ) -> Tuple[bool, int, int]:
        """
        Check if request is allowed
        
        Args:
            key: Rate limit key (e.g., "api_calls", "story_generation")
            limit: Maximum requests allowed
            window: Time window in seconds
            identifier: Unique identifier (user_id, IP, etc.)
        
        Returns:
            (allowed, remaining_requests, reset_time)
        """
        full_key = f"rate_limit:{key}:{identifier}" if identifier else f"rate_limit:{key}"
        current_time = int(time.time())
        window_start = current_time - window
        
        if self.redis and redis_manager.is_connected():
            return self._redis_rate_limit(full_key, limit, window, current_time, window_start)
        else:
            return self._memory_rate_limit(full_key, limit, window, current_time, window_start)
    
    def _redis_rate_limit(self, key: str, limit: int, window: int, current_time: int, window_start: int) -> Tuple[bool, int, int]:
        """Redis-based rate limiting with sliding window"""
        try:
            # Remove old entries outside the window
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_requests = self.redis.zcard(key)
            
            if current_requests >= limit:
                # Get oldest request to calculate reset time
                oldest = self.redis.zrange(key, 0, 0, withscores=True)
                reset_time = int(oldest[0][1]) + window if oldest else current_time + window
                return False, 0, reset_time
            
            # Add current request
            self.redis.zadd(key, {str(current_time): current_time})
            self.redis.expire(key, window)
            
            remaining = limit - current_requests - 1
            reset_time = current_time + window
            
            return True, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Redis rate limiting failed: {str(e)}")
            # Fallback to memory rate limiting
            return self._memory_rate_limit(key, limit, window, current_time, window_start)
    
    def _memory_rate_limit(self, key: str, limit: int, window: int, current_time: int, window_start: int) -> Tuple[bool, int, int]:
        """Memory-based rate limiting (fallback)"""
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old entries
        self.memory_store[key] = [req_time for req_time in self.memory_store[key] if req_time > window_start]
        
        if len(self.memory_store[key]) >= limit:
            reset_time = self.memory_store[key][0] + window
            return False, 0, reset_time
        
        # Add current request
        self.memory_store[key].append(current_time)
        
        remaining = limit - len(self.memory_store[key])
        reset_time = current_time + window
        
        return True, remaining, reset_time
    
    def get_usage_stats(self, key: str, identifier: str = None) -> dict:
        """Get current usage statistics"""
        full_key = f"rate_limit:{key}:{identifier}" if identifier else f"rate_limit:{key}"
        current_time = int(time.time())
        window_start = current_time - 3600  # Last hour
        
        if self.redis and redis_manager.is_connected():
            try:
                # Get requests in last hour
                self.redis.zremrangebyscore(full_key, 0, window_start)
                requests_last_hour = self.redis.zcard(full_key)
                
                # Get daily stats
                daily_key = f"daily:{full_key}:{current_time // 86400}"
                daily_requests = self.redis.get(daily_key) or 0
                
                return {
                    "requests_last_hour": requests_last_hour,
                    "requests_today": int(daily_requests),
                    "timestamp": current_time
                }
            except Exception as e:
                logger.error(f"Failed to get usage stats: {str(e)}")
        
        return {"requests_last_hour": 0, "requests_today": 0, "timestamp": current_time}

# =============================================================================
# STEP 3: RATE LIMITING RULES
# =============================================================================

class RateLimitingRules:
    """Define rate limiting rules for different user tiers and operations"""
    
    RULES = {
        # Free tier limits
        "free": {
            "story_generation": {"limit": 10, "window": 3600},      # 10 per hour
            "api_calls": {"limit": 100, "window": 3600},           # 100 per hour
            "file_upload": {"limit": 5, "window": 3600},           # 5 per hour
            "exports": {"limit": 20, "window": 3600},              # 20 per hour
        },
        
        # Basic tier limits
        "basic": {
            "story_generation": {"limit": 100, "window": 3600},     # 100 per hour
            "api_calls": {"limit": 1000, "window": 3600},          # 1000 per hour
            "file_upload": {"limit": 50, "window": 3600},           # 50 per hour
            "exports": {"limit": 200, "window": 3600},              # 200 per hour
        },
        
        # Pro tier limits
        "pro": {
            "story_generation": {"limit": 1000, "window": 3600},    # 1000 per hour
            "api_calls": {"limit": 10000, "window": 3600},         # 10000 per hour
            "file_upload": {"limit": 500, "window": 3600},          # 500 per hour
            "exports": {"limit": 2000, "window": 3600},             # 2000 per hour
        },
        
        # Enterprise tier limits
        "enterprise": {
            "story_generation": {"limit": 10000, "window": 3600},   # 10000 per hour
            "api_calls": {"limit": 100000, "window": 3600},        # 100000 per hour
            "file_upload": {"limit": 5000, "window": 3600},         # 5000 per hour
            "exports": {"limit": 20000, "window": 3600},            # 20000 per hour
        }
    }
    
    # IP-based limits for anonymous users
    ANONYMOUS_LIMITS = {
        "story_generation": {"limit": 3, "window": 3600},           # 3 per hour
        "api_calls": {"limit": 20, "window": 3600},                # 20 per hour
        "signup": {"limit": 5, "window": 3600},                    # 5 signups per hour
    }
    
    @classmethod
    def get_limits(cls, user_tier: str, operation: str) -> dict:
        """Get rate limits for user tier and operation"""
        return cls.RULES.get(user_tier.lower(), cls.RULES["free"]).get(operation, {"limit": 10, "window": 3600})
    
    @classmethod
    def get_anonymous_limits(cls, operation: str) -> dict:
        """Get rate limits for anonymous users"""
        return cls.ANONYMOUS_LIMITS.get(operation, {"limit": 5, "window": 3600})

# =============================================================================
# STEP 4: RATE LIMITING MIDDLEWARE
# =============================================================================

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for all requests"""
    
    # Get user info from JWT or IP for anonymous
    user_id = getattr(request.state, 'user_id', None)
    user_tier = getattr(request.state, 'subscription_tier', 'free')
    ip_address = request.client.host
    
    # Determine operation type from path
    path = request.url.path
    operation = "api_calls"  # Default
    
    if "/stories/generate" in path:
        operation = "story_generation"
    elif "/upload" in path:
        operation = "file_upload"
    elif "/export" in path:
        operation = "exports"
    elif "/auth/signup" in path:
        operation = "signup"
    
    # Get appropriate limits
    if user_id:
        limits = RateLimitingRules.get_limits(user_tier, operation)
        identifier = f"user:{user_id}"
    else:
        limits = RateLimitingRules.get_anonymous_limits(operation)
        identifier = f"ip:{ip_address}"
    
    # Check rate limit
    allowed, remaining, reset_time = rate_limiter.is_allowed(
        operation, 
        limits["limit"], 
        limits["window"],
        identifier
    )
    
    if not allowed:
        # Log rate limit violation
        logger.warning(
            f"Rate limit exceeded for {operation}",
            extra={
                "operation": operation,
                "identifier": identifier,
                "user_id": user_id,
                "ip_address": ip_address,
                "limit": limits["limit"],
                "window": limits["window"],
                "reset_time": reset_time
            }
        )
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded for {operation}. Please try again later.",
                "limit": limits["limit"],
                "window": limits["window"],
                "reset_time": reset_time,
                "retry_after": max(0, reset_time - int(time.time()))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limits["limit"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    return response

# =============================================================================
# STEP 5: ADVANCED RATE LIMITING FEATURES
# =============================================================================

class AdvancedRateLimiter:
    """Advanced rate limiting with burst protection and intelligent throttling"""
    
    def __init__(self):
        self.limiter = RateLimiter()
    
    def check_burst_protection(self, identifier: str) -> bool:
        """Check for burst attacks (many requests in short time)"""
        # Check for more than 10 requests in 10 seconds
        allowed, _, _ = self.limiter.is_allowed(
            "burst_protection", 10, 10, identifier
        )
        return allowed
    
    def check_daily_limits(self, user_id: int, operation: str, user_tier: str) -> Tuple[bool, int]:
        """Check daily usage limits"""
        daily_key = f"daily:{operation}:user:{user_id}"
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get daily limits (10x hourly limits)
        hourly_limits = RateLimitingRules.get_limits(user_tier, operation)
        daily_limit = hourly_limits["limit"] * 10
        
        allowed, remaining, _ = self.limiter.is_allowed(
            daily_key, daily_limit, 86400, f"{user_id}:{current_date}"
        )
        
        return allowed, remaining
    
    def get_user_usage_report(self, user_id: int, user_tier: str) -> dict:
        """Get comprehensive usage report for user"""
        report = {
            "user_id": user_id,
            "tier": user_tier,
            "timestamp": datetime.utcnow().isoformat(),
            "usage": {}
        }
        
        operations = ["story_generation", "api_calls", "file_upload", "exports"]
        
        for operation in operations:
            limits = RateLimitingRules.get_limits(user_tier, operation)
            stats = self.limiter.get_usage_stats(operation, f"user:{user_id}")
            
            report["usage"][operation] = {
                "current_hour": stats["requests_last_hour"],
                "daily": stats["requests_today"],
                "limit_hourly": limits["limit"],
                "limit_daily": limits["limit"] * 10,
                "remaining_hourly": max(0, limits["limit"] - stats["requests_last_hour"]),
                "remaining_daily": max(0, (limits["limit"] * 10) - stats["requests_today"])
            }
        
        return report
    
    def detect_suspicious_activity(self, identifier: str) -> dict:
        """Detect suspicious usage patterns"""
        suspicious = {
            "is_suspicious": False,
            "reasons": [],
            "confidence": 0.0
        }
        
        # Check for rapid requests
        if not self.check_burst_protection(identifier):
            suspicious["is_suspicious"] = True
            suspicious["reasons"].append("burst_attack")
            suspicious["confidence"] += 0.4
        
        # Check for unusual timing patterns
        # This would require more sophisticated analysis
        
        return suspicious

# =============================================================================
# STEP 6: COST CONTROL FEATURES
# =============================================================================

class CostController:
    """Control API costs based on usage"""
    
    # Estimated costs per operation (in USD)
    OPERATION_COSTS = {
        "story_generation": 0.01,  # $0.01 per story
        "file_upload": 0.001,      # $0.001 per upload
        "export": 0.0005,          # $0.0005 per export
        "api_call": 0.0001         # $0.0001 per API call
    }
    
    def __init__(self):
        self.limiter = AdvancedRateLimiter()
    
    def check_monthly_budget(self, user_id: int, user_tier: str) -> Tuple[bool, float]:
        """Check if user is within monthly budget"""
        # Get monthly cost limits based on tier
        budget_limits = {
            "free": 10.0,      # $10/month
            "basic": 100.0,    # $100/month
            "pro": 1000.0,     # $1000/month
            "enterprise": 10000.0  # $10000/month
        }
        
        monthly_budget = budget_limits.get(user_tier, 10.0)
        
        # Calculate current month's cost
        current_month = datetime.now().strftime("%Y-%m")
        cost_key = f"monthly_cost:{user_id}:{current_month}"
        
        # This would require tracking costs in Redis/database
        # For now, return within budget
        return True, monthly_budget
    
    def track_operation_cost(self, user_id: int, operation: str, count: int = 1):
        """Track cost of operation"""
        cost = self.OPERATION_COSTS.get(operation, 0) * count
        
        # Store cost in Redis/database
        # This would be implemented with actual Redis operations
        
        logger.info(
            f"Operation cost tracked",
            extra={
                "user_id": user_id,
                "operation": operation,
                "count": count,
                "cost": cost
            }
        )

# =============================================================================
# STEP 7: ENVIRONMENT SETUP
# =============================================================================

ENVIRONMENT_CONFIG = {
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_PASSWORD": None,  # Set for production
    "RATE_LIMITING_ENABLED": True,
    "COST_CONTROL_ENABLED": True
}

# =============================================================================
# STEP 8: DEPLOYMENT INSTRUCTIONS
# =============================================================================

DEPLOYMENT_STEPS = """
1. Install Redis:
   brew install redis  # Mac
   sudo apt-get install redis-server  # Ubuntu
   
2. Start Redis:
   redis-server
   
3. Set environment variables:
   export REDIS_HOST="localhost"
   export REDIS_PORT="6379"
   export REDIS_PASSWORD="your_password"  # Production only
   
4. Add to your FastAPI app:
   from rate_limiting_fix import rate_limit_middleware
   
   # Add rate limiting middleware (add BEFORE other middleware)
   app.middleware("http", rate_limit_middleware)
   
5. Test rate limiting:
   - Make multiple requests quickly
   - Verify 429 responses after limits
   - Check rate limit headers
   
6. Monitor Redis:
   redis-cli monitor
   redis-cli info memory
"""

# =============================================================================
# STEP 9: EXAMPLE USAGE
# =============================================================================

def example_rate_limited_function(user_id: int, user_tier: str):
    """Example of rate limiting in a function"""
    
    # Check specific operation limit
    limits = RateLimitingRules.get_limits(user_tier, "story_generation")
    allowed, remaining, reset_time = rate_limiter.is_allowed(
        "story_generation",
        limits["limit"],
        limits["window"],
        f"user:{user_id}"
    )
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again after {reset_time - int(time.time())} seconds"
        )
    
    # Proceed with operation
    return {"message": "Story generated successfully", "remaining": remaining}

if __name__ == "__main__":
    # Test rate limiting
    print("🚀 Testing rate limiting...")
    
    # Test basic rate limiting
    for i in range(5):
        allowed, remaining, reset_time = rate_limiter.is_allowed(
            "test_operation", 3, 10, "test_user"
        )
        print(f"Request {i+1}: Allowed={allowed}, Remaining={remaining}")
    
    print("✅ Rate limiting system ready!")
