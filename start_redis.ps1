# Quick Start Script for Redis
# Starts Redis server with the configured settings

$redisPath = "$PSScriptRoot\redis"
$configPath = "$PSScriptRoot\redis.windows.conf"

# Check if Redis is installed
if (-not (Test-Path "$redisPath\redis-server.exe")) {
    Write-Host "Redis is not installed!" -ForegroundColor Red
    Write-Host "Please run install_redis.ps1 first to install Redis." -ForegroundColor Yellow
    Write-Host ""
    $install = Read-Host "Do you want to run the installer now? (y/n)"
    if ($install -eq "y") {
        & "$PSScriptRoot\install_redis.ps1"
    }
    exit
}

# Check if Redis is already running
$redisRunning = Get-Process redis-server -ErrorAction SilentlyContinue
if ($redisRunning) {
    Write-Host "Redis is already running (PID: $($redisRunning.Id))" -ForegroundColor Yellow
    $continue = Read-Host "Do you want to stop it and restart? (y/n)"
    if ($continue -eq "y") {
        Stop-Process -Name redis-server -Force
        Start-Sleep -Seconds 2
    } else {
        exit
    }
}

Write-Host "===== Starting Redis Server =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Redis Path: $redisPath" -ForegroundColor White
Write-Host "Config: $configPath" -ForegroundColor White
Write-Host ""
Write-Host "Redis will start with the following settings:" -ForegroundColor Green
Write-Host "  - Max Memory: 2GB" -ForegroundColor White
Write-Host "  - Eviction Policy: allkeys-lru" -ForegroundColor White
Write-Host "  - Persistence: RDB snapshots every 15 minutes" -ForegroundColor White
Write-Host "  - Port: 6379" -ForegroundColor White
Write-Host "  - Host: localhost (127.0.0.1)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop Redis" -ForegroundColor Yellow
Write-Host ""

# Start Redis with configuration
if (Test-Path $configPath) {
    & "$redisPath\redis-server.exe" $configPath
} else {
    Write-Host "Warning: Configuration file not found. Using defaults." -ForegroundColor Yellow
    & "$redisPath\redis-server.exe"
}
