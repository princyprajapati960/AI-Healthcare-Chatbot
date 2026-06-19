# Quick Start: Redis Cache Setup

## Fast Setup (5 minutes)

### Step 1: Install Redis (Windows)
```powershell
# Run the installer script
.\install_redis.ps1
```

When prompted, type `y` to start Redis immediately.

### Step 2: Verify Redis is Running
Open a new PowerShell window:
```powershell
# Test Redis connection
.\redis\redis-cli.exe ping
```

Expected output: `PONG`

### Step 3: Check Configuration
```powershell
# Verify max memory (should be 2GB = 2147483648 bytes)
.\redis\redis-cli.exe CONFIG GET maxmemory

# Verify eviction policy (should be allkeys-lru)
.\redis\redis-cli.exe CONFIG GET maxmemory-policy
```

### Step 4: Install Python Dependencies
```powershell
pip install redis==5.2.1 pydantic-settings
```

### Step 5: Test the Application
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

### Step 6: Test Cache Endpoints

Open your browser or use curl:

**Check Cache Health:**
```
http://localhost:8000/api/cache/health
```

**View Cache Statistics:**
```
http://localhost:8000/api/cache/stats
```

## What's Configured?

✅ **Redis 5.0+** with Windows-optimized settings  
✅ **2GB Memory Limit** - automatically evicts old data when full  
✅ **allkeys-lru** - smart eviction of least recently used data  
✅ **RDB Persistence** - saves to disk every 15 minutes  
✅ **Connection Pool** - 50 concurrent connections for high performance  

## Cache Policies

| Data Type | How Long? | Example Use |
|-----------|-----------|-------------|
| Medical Knowledge | 6 hours | Condition information, treatments |
| Triage Patterns | 4 hours | Symptom analysis results |
| User Sessions | 15 minutes | Active conversation data |
| Medical Codes | 24 hours | ICD-10, SNOMED CT codes |

## Starting Redis Next Time

```powershell
# Quick start
.\start_redis.ps1

# Or manually
.\redis\redis-server.exe .\redis.windows.conf
```

Keep the Redis window open while using the application.

## Stopping Redis

In the Redis window, press `Ctrl+C`

Or from another terminal:
```powershell
# Find Redis process
Get-Process redis-server

# Stop it
Stop-Process -Name redis-server
```

## Troubleshooting

### Port Already in Use?
```powershell
# Find what's using port 6379
netstat -ano | findstr :6379

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Can't Connect to Redis?
1. Check if Redis is running: `Get-Process redis-server`
2. Verify port in `.env` matches Redis port (6379)
3. Check firewall isn't blocking localhost connections

### Need More Help?
See the full guide: `REDIS_SETUP.md`

## Monitoring

```powershell
# Watch Redis in real-time
.\redis\redis-cli.exe MONITOR

# Check memory usage
.\redis\redis-cli.exe INFO memory

# View statistics
.\redis\redis-cli.exe INFO stats
```

## Next Steps

Now that Redis is configured:

1. ✅ Task 1.1 Complete - Redis cache configured
2. ➡️ Task 1.2 - Enhance PostgreSQL schema
3. ➡️ Task 3.1 - Implement Context Manager (will use Redis)
4. ➡️ Task 4.2 - Implement Knowledge Base (will use Redis)

---

**Need detailed information?** See `REDIS_SETUP.md` and `TASK_1.1_COMPLETION.md`
