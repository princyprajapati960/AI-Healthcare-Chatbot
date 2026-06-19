# Redis Setup Guide for AI Healthcare Chatbot

This guide walks through setting up Redis 7+ with the required configuration for the AI Healthcare Chatbot system.

## Requirements

- **Redis Version**: 7.0 or higher
- **Memory**: 2GB dedicated for Redis
- **Operating System**: Windows, Linux, or macOS

## Installation

### Windows

1. **Download Redis for Windows**
   - Download from: https://github.com/tporadowski/redis/releases
   - Get the latest Redis 7.x `.msi` installer
   - Run the installer and follow the setup wizard

2. **Install as Windows Service**
   - During installation, check "Add Redis to PATH"
   - Check "Install as Windows Service"

3. **Verify Installation**
   ```bash
   redis-server --version
   ```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Redis 7+
sudo apt install redis-server

# Verify installation
redis-server --version
```

### macOS

```bash
# Using Homebrew
brew install redis

# Verify installation
redis-server --version
```

## Configuration

### 1. Copy Configuration File

Copy the provided `redis.conf` to your Redis installation directory or a known location:

```bash
# Linux/macOS
sudo cp redis.conf /etc/redis/redis.conf

# Windows
copy redis.conf "C:\Program Files\Redis\redis.conf"
```

### 2. Key Configuration Settings

The `redis.conf` file includes the following critical settings:

- **Max Memory**: 2GB limit
- **Eviction Policy**: `allkeys-lru` (evicts least recently used keys when memory exceeds 80%)
- **Persistence**: RDB snapshots every 15 minutes (900 seconds with at least 1 change)
- **Port**: 6379 (default)
- **Host**: localhost (127.0.0.1)

### 3. Security Settings (Production)

For production environments, edit `redis.conf`:

```bash
# Set a strong password
requirepass your_very_strong_password_here

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

Then update your `.env` file:
```env
REDIS_PASSWORD=your_very_strong_password_here
```

## Starting Redis

### Windows (Service)

```bash
# Start Redis service
net start Redis

# Stop Redis service
net stop Redis

# Start with custom config
redis-server "C:\Program Files\Redis\redis.conf"
```

### Linux

```bash
# Start Redis with custom config
sudo systemctl start redis-server

# Enable Redis to start on boot
sudo systemctl enable redis-server

# Or start manually with config file
redis-server /etc/redis/redis.conf
```

### macOS

```bash
# Start Redis as background service
brew services start redis

# Or start manually with config file
redis-server /usr/local/etc/redis.conf
```

## Verification

### 1. Check Redis is Running

```bash
redis-cli ping
# Expected output: PONG
```

### 2. Verify Configuration

```bash
# Connect to Redis CLI
redis-cli

# Check max memory setting
127.0.0.1:6379> CONFIG GET maxmemory
# Expected: "2147483648" (2GB in bytes)

# Check eviction policy
127.0.0.1:6379> CONFIG GET maxmemory-policy
# Expected: "allkeys-lru"

# Check RDB save configuration
127.0.0.1:6379> CONFIG GET save
# Expected: "900 1 300 10 60 10000"

# Exit CLI
127.0.0.1:6379> exit
```

### 3. Monitor Redis

```bash
# View memory usage
redis-cli INFO memory

# View statistics
redis-cli INFO stats

# Monitor real-time commands
redis-cli MONITOR

# Check evicted keys
redis-cli INFO stats | grep evicted_keys
```

## Connection Pooling

The application uses `redis-py` async client with connection pooling:

- **Max Connections**: 50
- **Socket Timeout**: 5 seconds
- **Health Check**: Every 30 seconds

These settings are configured in the `CacheManager` class.

## Cache Policies

The system implements the following TTL policies:

| Data Type | TTL | Key Pattern | Purpose |
|-----------|-----|-------------|---------|
| Medical Knowledge | 6 hours | `knowledge:condition:*` | Medical condition information |
| Triage Patterns | 4 hours | `triage:pattern:*` | Symptom analysis patterns |
| User Sessions | 15 minutes | `session:*` | Active user session data |
| Medical Codes | 24 hours | `code:*` | ICD-10, SNOMED CT codes |

## Monitoring Cache Performance

The application provides a cache statistics endpoint:

```bash
# Get cache statistics
curl http://localhost:8000/api/cache/stats
```

Expected metrics:
- Cache hit rate: Target 70%+
- Evicted keys: Monitor for memory pressure
- Used memory: Should stay below 2GB

## Troubleshooting

### Redis Won't Start

1. Check if another instance is running:
   ```bash
   # Windows
   netstat -ano | findstr :6379
   
   # Linux/macOS
   netstat -tuln | grep 6379
   ```

2. Check Redis logs:
   ```bash
   # Linux
   sudo tail -f /var/log/redis/redis-server.log
   
   # Windows (Event Viewer)
   # Check Application logs for Redis entries
   ```

### Connection Refused

1. Verify Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check firewall settings (if connecting remotely)

3. Verify connection settings in `.env` file

### High Memory Usage

1. Check evicted keys:
   ```bash
   redis-cli INFO stats | grep evicted_keys
   ```

2. Monitor memory:
   ```bash
   redis-cli INFO memory | grep used_memory_human
   ```

3. Reduce TTLs or increase max memory if needed

### Low Cache Hit Rate

1. Check cache statistics endpoint
2. Review TTL policies for your use case
3. Monitor frequently accessed keys:
   ```bash
   redis-cli --hotkeys
   ```

## Performance Tuning

### For High-Traffic Scenarios

1. **Increase Max Memory**: Adjust in `redis.conf`
   ```
   maxmemory 4gb
   ```

2. **Tune Connection Pool**: Update `.env`
   ```
   REDIS_MAX_CONNECTIONS=100
   ```

3. **Enable AOF Persistence** (optional, for durability):
   ```
   appendonly yes
   appendfsync everysec
   ```

### For Low-Latency Requirements

1. Disable disk persistence (loses durability):
   ```
   save ""
   ```

2. Use pipelining for bulk operations

3. Keep data sizes small (< 1MB per key)

## Testing Redis Setup

Run the included test script to verify Redis configuration:

```bash
# From backend directory
python -m pytest tests/test_cache_manager.py -v
```

## Additional Resources

- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Redis Security](https://redis.io/docs/manual/security/)
- [Redis Monitoring](https://redis.io/docs/manual/admin/)

## Support

For issues with Redis setup, check:
1. Redis logs for error messages
2. Application logs for connection errors
3. Firewall and network configuration
4. Redis server status and resource usage
