"""
Cache Manager Service for Redis integration.

This module provides intelligent caching with connection pooling,
TTL management, and LRU eviction for medical knowledge, user sessions,
triage patterns, and medical codes.
"""

from typing import Any, Optional
import json
import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Intelligent cache manager with Redis backend.
    
    Implements cache-aside pattern with configurable TTL policies:
    - Medical knowledge: 6 hours (21600 seconds)
    - Triage patterns: 4 hours (14400 seconds)
    - User sessions: 15 minutes (900 seconds)
    - Medical codes: 24 hours (86400 seconds)
    
    Configuration:
    - Eviction Policy: allkeys-lru (evict least recently used when memory exceeds limit)
    - Max Memory: 2GB with 80% threshold for eviction
    - Persistence: RDB snapshots every 15 minutes
    """
    
    # Cache TTL policies (in seconds)
    TTL_MEDICAL_KNOWLEDGE = 21600  # 6 hours
    TTL_TRIAGE_PATTERNS = 14400    # 4 hours
    TTL_USER_SESSIONS = 900        # 15 minutes
    TTL_MEDICAL_CODES = 86400      # 24 hours
    
    def __init__(self):
        """Initialize Redis connection pool."""
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[aioredis.Redis] = None
        self._connected: bool = False
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0
        }
    
    async def connect(self):
        """
        Establish Redis connection with connection pooling.
        Gracefully degrades if Redis is unavailable.
        """
        if self._pool is None:
            try:
                self._pool = ConnectionPool(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password if settings.redis_password else None,
                    max_connections=settings.redis_max_connections,
                    socket_timeout=settings.redis_socket_timeout,
                    socket_connect_timeout=settings.redis_socket_connect_timeout,
                    decode_responses=False,
                    health_check_interval=30
                )
                self._redis = aioredis.Redis(connection_pool=self._pool)
                
                await self._redis.ping()
                self._connected = True
                logger.info(f"Redis connected successfully to {settings.redis_host}:{settings.redis_port}")
                
            except Exception as e:
                logger.warning(f"Redis unavailable, running without cache: {e}")
                self._pool = None
                self._redis = None
                self._connected = False
    
    async def disconnect(self):
        """Close Redis connection pool gracefully."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
        self._connected = False
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
            self._redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        if not self._connected:
            self._stats["misses"] += 1
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                self._stats["hits"] += 1
                return json.loads(value.decode('utf-8'))
            else:
                self._stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            self._stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            ttl: Time-to-live in seconds
        """
        if not self._connected:
            return
        
        try:
            # Serialize to JSON
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl, serialized)
            self._stats["sets"] += 1
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            raise
    
    async def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "knowledge:condition:*")
            
        Returns:
            Number of keys deleted
        """
        if not self._connected:
            return 0
        
        try:
            # Find matching keys
            cursor = 0
            deleted_count = 0
            
            while True:
                cursor, keys = await self._redis.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    deleted_count += await self._redis.delete(*keys)
                
                if cursor == 0:
                    break
            
            self._stats["invalidations"] += deleted_count
            logger.info(f"Invalidated {deleted_count} cache entries matching pattern '{pattern}'")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern '{pattern}': {e}")
            raise
    
    async def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - sets: Number of cache sets
            - invalidations: Number of invalidated entries
            - hit_rate: Cache hit rate percentage
            - redis_info: Redis server info
        """
        if not self._connected:
            return {**self._stats, "hit_rate": 0, "status": "disconnected"}
        
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        try:
            # Get Redis memory and stats info
            redis_info = await self._redis.info("memory")
            redis_stats = await self._redis.info("stats")
            
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "invalidations": self._stats["invalidations"],
                "hit_rate": round(hit_rate, 2),
                "redis_memory_used": redis_info.get("used_memory_human", "N/A"),
                "redis_memory_peak": redis_info.get("used_memory_peak_human", "N/A"),
                "redis_evicted_keys": redis_stats.get("evicted_keys", 0),
                "redis_keyspace_hits": redis_stats.get("keyspace_hits", 0),
                "redis_keyspace_misses": redis_stats.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "invalidations": self._stats["invalidations"],
                "hit_rate": round(hit_rate, 2),
                "error": str(e)
            }
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a specific key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        if not self._connected:
            return -2
        
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL check error for key '{key}': {e}")
            return -2


# Global cache manager instance
cache_manager = CacheManager()
