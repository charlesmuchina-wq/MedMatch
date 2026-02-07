"""
Global Rate Limiter with Redis Support
Provides consistent rate limiting across multiple pods/replicas
Designed for 1M+ users scale
"""
import asyncio
import time
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

# ============== Configuration ==============
@dataclass
class RateLimitConfig:
    """Rate limit configuration for different tiers"""
    requests_per_second: int
    requests_per_minute: int
    burst_multiplier: float = 2.0
    
    @property
    def burst_limit(self) -> int:
        return int(self.requests_per_second * self.burst_multiplier)

# Tier-based rate limits - OPTIMIZED to prevent 429 errors
RATE_LIMIT_TIERS = {
    "anonymous": RateLimitConfig(
        requests_per_second=50,
        requests_per_minute=500,
        burst_multiplier=3.0
    ),
    "free": RateLimitConfig(
        requests_per_second=200,
        requests_per_minute=2000,
        burst_multiplier=4.0
    ),
    "premium": RateLimitConfig(
        requests_per_second=1000,
        requests_per_minute=10000,
        burst_multiplier=5.0
    ),
    "enterprise": RateLimitConfig(
        requests_per_second=5000,
        requests_per_minute=50000,
        burst_multiplier=6.0
    ),
    "internal": RateLimitConfig(
        requests_per_second=20000,
        requests_per_minute=200000,
        burst_multiplier=10.0
    )
}

# ============== In-Memory Rate Limiter ==============
class InMemoryRateLimiter:
    """
    Sliding window rate limiter using in-memory storage.
    Use this when Redis is not available.
    """
    
    def __init__(self):
        self.windows: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
        
    def _get_key(self, identifier: str, window_type: str) -> str:
        return f"{identifier}:{window_type}"
    
    def _clean_old_entries(self, entries: list, window_seconds: int) -> list:
        """Remove entries older than the window"""
        cutoff = time.time() - window_seconds
        return [t for t in entries if t > cutoff]
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        tier: str = "free"
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit.
        Returns (allowed, headers_dict)
        """
        config = RATE_LIMIT_TIERS.get(tier, RATE_LIMIT_TIERS["free"])
        now = time.time()
        
        async with self.lock:
            # Check per-second limit
            sec_key = self._get_key(identifier, "second")
            self.windows[sec_key] = self._clean_old_entries(self.windows[sec_key], 1)
            
            # Check per-minute limit
            min_key = self._get_key(identifier, "minute")
            self.windows[min_key] = self._clean_old_entries(self.windows[min_key], 60)
            
            sec_count = len(self.windows[sec_key])
            min_count = len(self.windows[min_key])
            
            # Check burst limit (allows temporary spikes)
            burst_allowed = sec_count < config.burst_limit
            sustained_allowed = sec_count < config.requests_per_second
            minute_allowed = min_count < config.requests_per_minute
            
            headers = {
                "X-RateLimit-Limit": str(config.requests_per_minute),
                "X-RateLimit-Remaining": str(max(0, config.requests_per_minute - min_count)),
                "X-RateLimit-Reset": str(int(now) + 60),
                "X-RateLimit-Tier": tier
            }
            
            # Allow if within burst OR within sustained limits
            if (burst_allowed or sustained_allowed) and minute_allowed:
                self.windows[sec_key].append(now)
                self.windows[min_key].append(now)
                return True, headers
            
            # Calculate retry-after
            if not minute_allowed:
                retry_after = 60 - (now - self.windows[min_key][0]) if self.windows[min_key] else 60
            else:
                retry_after = 1 - (now - self.windows[sec_key][0]) if self.windows[sec_key] else 1
            
            headers["Retry-After"] = str(int(max(1, retry_after)))
            headers["X-RateLimit-Remaining"] = "0"
            
            return False, headers
    
    async def get_usage(self, identifier: str) -> Dict:
        """Get current usage for an identifier"""
        async with self.lock:
            sec_key = self._get_key(identifier, "second")
            min_key = self._get_key(identifier, "minute")
            
            self.windows[sec_key] = self._clean_old_entries(self.windows[sec_key], 1)
            self.windows[min_key] = self._clean_old_entries(self.windows[min_key], 60)
            
            return {
                "requests_last_second": len(self.windows[sec_key]),
                "requests_last_minute": len(self.windows[min_key])
            }
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total_keys = len(self.windows)
        total_entries = sum(len(v) for v in self.windows.values())
        return {
            "type": "in-memory",
            "unique_identifiers": total_keys // 2,  # sec + min keys
            "total_tracked_requests": total_entries,
            "tiers": list(RATE_LIMIT_TIERS.keys())
        }

# ============== Redis Rate Limiter ==============
class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.
    Provides consistent limits across multiple pods.
    """
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.environ.get('REDIS_URL')
        self.redis = None
        self._connected = False
        
    async def connect(self):
        """Connect to Redis"""
        if self._connected:
            return
            
        try:
            import redis.asyncio as aioredis
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            self._connected = True
            logger.info("Redis rate limiter connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self._connected = False
    
    async def check_rate_limit(
        self,
        identifier: str,
        tier: str = "free"
    ) -> Tuple[bool, Dict]:
        """Check rate limit using Redis sliding window"""
        if not self._connected:
            raise Exception("Redis not connected")
            
        config = RATE_LIMIT_TIERS.get(tier, RATE_LIMIT_TIERS["free"])
        now = time.time()
        now_ms = int(now * 1000)
        
        # Keys for sliding windows
        sec_key = f"ratelimit:{identifier}:sec"
        min_key = f"ratelimit:{identifier}:min"
        
        pipe = self.redis.pipeline()
        
        # Remove old entries and count current
        pipe.zremrangebyscore(sec_key, 0, now_ms - 1000)
        pipe.zremrangebyscore(min_key, 0, now_ms - 60000)
        pipe.zcard(sec_key)
        pipe.zcard(min_key)
        
        results = await pipe.execute()
        sec_count = results[2]
        min_count = results[3]
        
        headers = {
            "X-RateLimit-Limit": str(config.requests_per_minute),
            "X-RateLimit-Remaining": str(max(0, config.requests_per_minute - min_count)),
            "X-RateLimit-Reset": str(int(now) + 60),
            "X-RateLimit-Tier": tier
        }
        
        # Check limits with burst tolerance
        burst_allowed = sec_count < config.burst_limit
        minute_allowed = min_count < config.requests_per_minute
        
        if burst_allowed and minute_allowed:
            # Add new entry
            pipe = self.redis.pipeline()
            pipe.zadd(sec_key, {str(now_ms): now_ms})
            pipe.zadd(min_key, {str(now_ms): now_ms})
            pipe.expire(sec_key, 2)
            pipe.expire(min_key, 120)
            await pipe.execute()
            
            return True, headers
        
        # Calculate retry-after
        retry_after = 1 if not burst_allowed else 60
        headers["Retry-After"] = str(retry_after)
        headers["X-RateLimit-Remaining"] = "0"
        
        return False, headers
    
    async def get_usage(self, identifier: str) -> Dict:
        """Get current usage from Redis"""
        if not self._connected:
            return {"error": "Redis not connected"}
            
        now_ms = int(time.time() * 1000)
        
        pipe = self.redis.pipeline()
        pipe.zcount(f"ratelimit:{identifier}:sec", now_ms - 1000, now_ms)
        pipe.zcount(f"ratelimit:{identifier}:min", now_ms - 60000, now_ms)
        results = await pipe.execute()
        
        return {
            "requests_last_second": results[0],
            "requests_last_minute": results[1]
        }
    
    def get_stats(self) -> Dict:
        return {
            "type": "redis",
            "connected": self._connected,
            "url": self.redis_url[:20] + "..." if self.redis_url else None,
            "tiers": list(RATE_LIMIT_TIERS.keys())
        }

# ============== Global Rate Limiter Factory ==============
class GlobalRateLimiter:
    """
    Factory that provides the best available rate limiter.
    Falls back to in-memory if Redis is not available.
    """
    
    def __init__(self):
        self.redis_limiter: Optional[RedisRateLimiter] = None
        self.memory_limiter = InMemoryRateLimiter()
        self._use_redis = False
        
    async def initialize(self, redis_url: str = None):
        """Initialize with Redis if available"""
        if redis_url or os.environ.get('REDIS_URL'):
            self.redis_limiter = RedisRateLimiter(redis_url)
            try:
                await self.redis_limiter.connect()
                self._use_redis = True
                logger.info("Using Redis for global rate limiting")
            except Exception:
                logger.info("Redis not available, using in-memory rate limiting")
                self._use_redis = False
        else:
            logger.info("No Redis URL configured, using in-memory rate limiting")
    
    async def check_rate_limit(
        self,
        identifier: str,
        tier: str = "free"
    ) -> Tuple[bool, Dict]:
        """Check rate limit using best available backend"""
        if self._use_redis and self.redis_limiter:
            try:
                return await self.redis_limiter.check_rate_limit(identifier, tier)
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}")
                # Fallback to memory
                
        return await self.memory_limiter.check_rate_limit(identifier, tier)
    
    async def get_usage(self, identifier: str) -> Dict:
        """Get usage from best available backend"""
        if self._use_redis and self.redis_limiter:
            try:
                return await self.redis_limiter.get_usage(identifier)
            except Exception:
                pass
        return await self.memory_limiter.get_usage(identifier)
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        if self._use_redis and self.redis_limiter:
            return self.redis_limiter.get_stats()
        return self.memory_limiter.get_stats()
    
    def get_tier_info(self) -> Dict:
        """Get information about rate limit tiers"""
        return {
            tier: {
                "requests_per_second": config.requests_per_second,
                "requests_per_minute": config.requests_per_minute,
                "burst_limit": config.burst_limit
            }
            for tier, config in RATE_LIMIT_TIERS.items()
        }

# ============== Global Instance ==============
global_rate_limiter = GlobalRateLimiter()

# ============== Utility Functions ==============
def get_client_identifier(request) -> str:
    """Extract client identifier from request"""
    # Try to get user ID first (authenticated requests)
    user = getattr(request.state, 'user', None)
    if user and user.get('user_id'):
        return f"user:{user['user_id']}"
    
    # Fall back to IP address
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.client.host if request.client else 'unknown'
    
    return f"ip:{ip}"

def get_user_tier(request) -> str:
    """Determine user's rate limit tier"""
    user = getattr(request.state, 'user', None)
    
    if not user:
        return "anonymous"
    
    membership = user.get('membership', {})
    plan = membership.get('plan', 'free')
    
    if plan == 'enterprise':
        return "enterprise"
    elif plan == 'premium':
        return "premium"
    else:
        return "free"

# ============== Export ==============
__all__ = [
    'GlobalRateLimiter',
    'global_rate_limiter',
    'RATE_LIMIT_TIERS',
    'get_client_identifier',
    'get_user_tier'
]
