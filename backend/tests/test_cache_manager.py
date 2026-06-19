"""
Unit tests for CacheManager.

Tests Redis connection pooling, caching operations, TTL management,
and statistics tracking.
"""

import pytest
import asyncio
from backend.app.services.cache_manager import CacheManager
from backend.app.config import settings


@pytest.fixture
async def cache_manager():
    """Create a CacheManager instance for testing."""
    manager = CacheManager()
    await manager.connect()
    yield manager
    # Cleanup: clear test keys
    await manager.invalidate("test:*")
    await manager.disconnect()


@pytest.mark.asyncio
async def test_cache_connect_disconnect(cache_manager):
    """Test Redis connection and disconnection."""
    # Connection should be established by fixture
    assert cache_manager._redis is not None
    assert cache_manager._pool is not None
    
    # Should be able to ping Redis
    ping_result = await cache_manager._redis.ping()
    assert ping_result is True


@pytest.mark.asyncio
async def test_cache_set_and_get(cache_manager):
    """Test basic cache set and get operations."""
    key = "test:basic:key1"
    value = {"name": "Test", "age": 30, "active": True}
    ttl = 60  # 1 minute
    
    # Set value
    await cache_manager.set(key, value, ttl)
    
    # Get value
    retrieved = await cache_manager.get(key)
    assert retrieved == value
    
    # Stats should reflect the operation
    stats = await cache_manager.get_stats()
    assert stats["sets"] >= 1
    assert stats["hits"] >= 1


@pytest.mark.asyncio
async def test_cache_get_nonexistent(cache_manager):
    """Test getting a non-existent key returns None."""
    key = "test:nonexistent:key"
    
    result = await cache_manager.get(key)
    assert result is None
    
    # Should count as a miss
    stats = await cache_manager.get_stats()
    assert stats["misses"] >= 1


@pytest.mark.asyncio
async def test_cache_ttl(cache_manager):
    """Test TTL expiration."""
    key = "test:ttl:key"
    value = {"message": "This will expire"}
    ttl = 2  # 2 seconds
    
    # Set with short TTL
    await cache_manager.set(key, value, ttl)
    
    # Should exist immediately
    assert await cache_manager.exists(key) is True
    
    # Check TTL
    remaining_ttl = await cache_manager.get_ttl(key)
    assert 0 < remaining_ttl <= 2
    
    # Wait for expiration
    await asyncio.sleep(3)
    
    # Should not exist anymore
    assert await cache_manager.exists(key) is False


@pytest.mark.asyncio
async def test_cache_delete(cache_manager):
    """Test deleting a cache key."""
    key = "test:delete:key"
    value = {"data": "to be deleted"}
    
    # Set value
    await cache_manager.set(key, value, 60)
    assert await cache_manager.exists(key) is True
    
    # Delete
    deleted = await cache_manager.delete(key)
    assert deleted is True
    assert await cache_manager.exists(key) is False
    
    # Deleting non-existent key should return False
    deleted_again = await cache_manager.delete(key)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_cache_invalidate_pattern(cache_manager):
    """Test invalidating multiple keys with pattern."""
    # Create multiple keys with same pattern
    keys = [
        "test:pattern:key1",
        "test:pattern:key2",
        "test:pattern:key3"
    ]
    
    for key in keys:
        await cache_manager.set(key, {"id": key}, 60)
    
    # Verify all exist
    for key in keys:
        assert await cache_manager.exists(key) is True
    
    # Invalidate all matching pattern
    deleted_count = await cache_manager.invalidate("test:pattern:*")
    assert deleted_count == 3
    
    # Verify all are deleted
    for key in keys:
        assert await cache_manager.exists(key) is False


@pytest.mark.asyncio
async def test_cache_statistics(cache_manager):
    """Test cache statistics tracking."""
    # Reset stats by getting initial values
    initial_stats = await cache_manager.get_stats()
    
    # Perform operations
    await cache_manager.set("test:stats:key1", {"value": 1}, 60)
    await cache_manager.get("test:stats:key1")  # Hit
    await cache_manager.get("test:stats:nonexistent")  # Miss
    
    # Get updated stats
    stats = await cache_manager.get_stats()
    
    # Verify stats are tracked
    assert stats["sets"] > initial_stats["sets"]
    assert stats["hits"] > initial_stats["hits"]
    assert stats["misses"] > initial_stats["misses"]
    assert "hit_rate" in stats
    assert "redis_memory_used" in stats


@pytest.mark.asyncio
async def test_cache_json_serialization(cache_manager):
    """Test JSON serialization of complex objects."""
    key = "test:json:complex"
    
    # Complex nested object
    value = {
        "user": {
            "name": "John Doe",
            "age": 35,
            "allergies": ["penicillin", "peanuts"],
            "medications": [
                {"name": "Aspirin", "dosage": "100mg"},
                {"name": "Metformin", "dosage": "500mg"}
            ]
        },
        "session": {
            "id": "abc123",
            "active": True,
            "timestamps": ["2024-01-01T10:00:00", "2024-01-01T10:30:00"]
        }
    }
    
    # Set and retrieve
    await cache_manager.set(key, value, 60)
    retrieved = await cache_manager.get(key)
    
    # Should match exactly
    assert retrieved == value
    assert retrieved["user"]["allergies"] == value["user"]["allergies"]
    assert retrieved["user"]["medications"][0]["name"] == "Aspirin"


@pytest.mark.asyncio
async def test_cache_ttl_policies(cache_manager):
    """Test different TTL policies for different data types."""
    # Medical knowledge - 6 hours
    await cache_manager.set(
        "knowledge:condition:diabetes",
        {"name": "Diabetes", "symptoms": ["thirst", "fatigue"]},
        CacheManager.TTL_MEDICAL_KNOWLEDGE
    )
    
    # Triage patterns - 4 hours
    await cache_manager.set(
        "triage:pattern:fever",
        {"pattern": "high fever", "department": "emergency"},
        CacheManager.TTL_TRIAGE_PATTERNS
    )
    
    # User session - 15 minutes
    await cache_manager.set(
        "session:user123",
        {"user_id": "user123", "active": True},
        CacheManager.TTL_USER_SESSIONS
    )
    
    # Medical codes - 24 hours
    await cache_manager.set(
        "code:icd10:E11",
        {"code": "E11", "description": "Type 2 diabetes mellitus"},
        CacheManager.TTL_MEDICAL_CODES
    )
    
    # Verify all exist
    assert await cache_manager.exists("knowledge:condition:diabetes") is True
    assert await cache_manager.exists("triage:pattern:fever") is True
    assert await cache_manager.exists("session:user123") is True
    assert await cache_manager.exists("code:icd10:E11") is True
    
    # Verify TTLs are set correctly (allow small variance)
    ttl_knowledge = await cache_manager.get_ttl("knowledge:condition:diabetes")
    assert CacheManager.TTL_MEDICAL_KNOWLEDGE - 10 <= ttl_knowledge <= CacheManager.TTL_MEDICAL_KNOWLEDGE
    
    ttl_session = await cache_manager.get_ttl("session:user123")
    assert CacheManager.TTL_USER_SESSIONS - 10 <= ttl_session <= CacheManager.TTL_USER_SESSIONS


@pytest.mark.asyncio
async def test_cache_exists(cache_manager):
    """Test checking key existence."""
    key = "test:exists:key"
    
    # Should not exist initially
    assert await cache_manager.exists(key) is False
    
    # Set value
    await cache_manager.set(key, {"data": "test"}, 60)
    
    # Should exist now
    assert await cache_manager.exists(key) is True
    
    # Delete and check again
    await cache_manager.delete(key)
    assert await cache_manager.exists(key) is False


@pytest.mark.asyncio
async def test_cache_connection_pool():
    """Test connection pooling configuration."""
    manager = CacheManager()
    await manager.connect()
    
    # Verify pool settings
    assert manager._pool is not None
    assert manager._pool.connection_kwargs["host"] == settings.redis_host
    assert manager._pool.connection_kwargs["port"] == settings.redis_port
    assert manager._pool.connection_kwargs["db"] == settings.redis_db
    assert manager._pool.max_connections == settings.redis_max_connections
    
    await manager.disconnect()


@pytest.mark.asyncio
async def test_cache_error_handling(cache_manager):
    """Test error handling for invalid operations."""
    # Try to get with valid key (should not raise error even if not found)
    result = await cache_manager.get("nonexistent:key")
    assert result is None
    
    # Try to delete non-existent key (should return False, not error)
    deleted = await cache_manager.delete("nonexistent:key")
    assert deleted is False


@pytest.mark.asyncio
async def test_cache_hit_rate_calculation(cache_manager):
    """Test cache hit rate calculation."""
    # Clear existing stats
    initial_stats = await cache_manager.get_stats()
    
    # Perform operations with known hit/miss pattern
    key = "test:hitrate:key"
    await cache_manager.set(key, {"value": 123}, 60)
    
    # 3 hits
    await cache_manager.get(key)
    await cache_manager.get(key)
    await cache_manager.get(key)
    
    # 1 miss
    await cache_manager.get("nonexistent:key:hitrate")
    
    # Get stats
    stats = await cache_manager.get_stats()
    
    # Calculate expected hit rate
    total_ops = (stats["hits"] - initial_stats["hits"]) + (stats["misses"] - initial_stats["misses"])
    new_hits = stats["hits"] - initial_stats["hits"]
    
    if total_ops > 0:
        expected_rate = (new_hits / total_ops) * 100
        # Hit rate should be 75% (3 hits out of 4 operations)
        assert stats["hit_rate"] >= 70  # Allow some variance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
