"""
Cache Management API Routes.

Provides endpoints for cache statistics and monitoring.
"""

from fastapi import APIRouter, HTTPException
from backend.app.services.cache_manager import cache_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_stats():
    """
    Get cache statistics and performance metrics.
    
    Returns:
        Dictionary containing:
        - hits: Number of cache hits
        - misses: Number of cache misses
        - sets: Number of cache sets
        - invalidations: Number of invalidated entries
        - hit_rate: Cache hit rate percentage
        - redis_memory_used: Redis memory usage (human-readable)
        - redis_memory_peak: Peak Redis memory usage
        - redis_evicted_keys: Number of evicted keys
        - redis_keyspace_hits: Total keyspace hits
        - redis_keyspace_misses: Total keyspace misses
    """
    try:
        stats = await cache_manager.get_stats()
        return {
            "status": "ok",
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@router.post("/invalidate/{pattern}")
async def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching the given pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "knowledge:condition:*")
        
    Returns:
        Number of keys invalidated
        
    Examples:
        POST /api/cache/invalidate/knowledge:condition:*
        POST /api/cache/invalidate/session:*
        POST /api/cache/invalidate/code:icd10:*
    """
    try:
        deleted_count = await cache_manager.invalidate(pattern)
        return {
            "status": "ok",
            "pattern": pattern,
            "deleted_count": deleted_count,
            "message": f"Invalidated {deleted_count} cache entries"
        }
    except Exception as e:
        logger.error(f"Error invalidating cache with pattern '{pattern}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invalidate cache: {str(e)}")


@router.delete("/{key}")
async def delete_cache_key(key: str):
    """
    Delete a specific cache key.
    
    Args:
        key: Cache key to delete
        
    Returns:
        Success status
    """
    try:
        deleted = await cache_manager.delete(key)
        if deleted:
            return {
                "status": "ok",
                "key": key,
                "message": "Cache key deleted successfully"
            }
        else:
            return {
                "status": "not_found",
                "key": key,
                "message": "Cache key not found"
            }
    except Exception as e:
        logger.error(f"Error deleting cache key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete cache key: {str(e)}")


@router.get("/health")
async def cache_health():
    """
    Check cache/Redis health status.
    
    Returns:
        Health status and basic connection info
    """
    try:
        # Try to get stats which will verify connection
        stats = await cache_manager.get_stats()
        return {
            "status": "healthy",
            "message": "Redis connection is operational",
            "hit_rate": stats.get("hit_rate", 0)
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
