# Redis Installation Script for Windows
# This script downloads and sets up Redis 7+ for the AI Healthcare Chatbot

Write-Host "===== Redis Installation for AI Healthcare Chatbot =====" -ForegroundColor Cyan
Write-Host ""

# Configuration
$redisVersion = "5.0.14.1"
$downloadUrl = "https://github.com/tporadowski/redis/releases/download/v$redisVersion/Redis-x64-$redisVersion.zip"
$installPath = "$PSScriptRoot\redis"
$zipFile = "$PSScriptRoot\redis.zip"

# Check if Redis is already installed
if (Test-Path "$installPath\redis-server.exe") {
    Write-Host "Redis is already installed at $installPath" -ForegroundColor Yellow
    $response = Read-Host "Do you want to reinstall? (y/n)"
    if ($response -ne "y") {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit
    }
}

# Download Redis
Write-Host "Downloading Redis $redisVersion..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Failed to download Redis: $_" -ForegroundColor Red
    exit 1
}

# Extract Redis
Write-Host "Extracting Redis..." -ForegroundColor Green
try {
    if (Test-Path $installPath) {
        Remove-Item -Path $installPath -Recurse -Force
    }
    Expand-Archive -Path $zipFile -DestinationPath $installPath -Force
    Remove-Item -Path $zipFile
    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "Failed to extract Redis: $_" -ForegroundColor Red
    exit 1
}

# Copy configuration file
Write-Host "Copying Redis configuration..." -ForegroundColor Green
if (Test-Path "$PSScriptRoot\redis.conf") {
    Copy-Item "$PSScriptRoot\redis.conf" "$installPath\redis.windows.conf" -Force
    Write-Host "Configuration file copied!" -ForegroundColor Green
} else {
    Write-Host "Warning: redis.conf not found. Using default configuration." -ForegroundColor Yellow
}

# Add to PATH (current session)
$env:PATH += ";$installPath"

Write-Host ""
Write-Host "===== Redis Installation Complete! =====" -ForegroundColor Green
Write-Host ""
Write-Host "Redis has been installed to: $installPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start Redis with custom configuration:" -ForegroundColor Yellow
Write-Host "  .\redis\redis-server.exe .\redis\redis.windows.conf" -ForegroundColor White
Write-Host ""
Write-Host "To start Redis with default configuration:" -ForegroundColor Yellow
Write-Host "  .\redis\redis-server.exe" -ForegroundColor White
Write-Host ""
Write-Host "To test Redis connection:" -ForegroundColor Yellow
Write-Host "  .\redis\redis-cli.exe ping" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Redis will run in the current terminal window." -ForegroundColor Cyan
Write-Host "      Keep the window open while using the application." -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start Redis now
$startNow = Read-Host "Do you want to start Redis now? (y/n)"
if ($startNow -eq "y") {
    Write-Host ""
    Write-Host "Starting Redis server..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop Redis" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if custom config exists
    if (Test-Path "$installPath\redis.windows.conf") {
        & "$installPath\redis-server.exe" "$installPath\redis.windows.conf"
    } else {
        & "$installPath\redis-server.exe"
    }
}
