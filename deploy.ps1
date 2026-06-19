# AI Healthcare Deployment Script for Windows
# This script helps deploy the MediVoice AI application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MediVoice AI - Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[✓] Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Redis
$redisInstalled = $false
try {
    redis-server --version 2>&1 | Out-Null
    $redisInstalled = $true
    Write-Host "[✓] Redis installed" -ForegroundColor Green
} catch {
    Write-Host "[!] Redis not found" -ForegroundColor Yellow
    Write-Host "    Redis is required for caching. Options:" -ForegroundColor Yellow
    Write-Host "    1. Install with Chocolatey: choco install redis-64" -ForegroundColor Cyan
    Write-Host "    2. Download from: https://github.com/tporadowski/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    
    $installRedis = Read-Host "Do you want to continue without Redis? (y/N)"
    if ($installRedis -ne 'y' -and $installRedis -ne 'Y') {
        Write-Host "Please install Redis and run this script again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 1: Backend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[✓] Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[✗] Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Train ML model if not exists
if (!(Test-Path "backend\models\triage_model.pkl")) {
    Write-Host "Training ML model..." -ForegroundColor Yellow
    python -m backend.train_model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] ML model trained" -ForegroundColor Green
    } else {
        Write-Host "[✗] Failed to train model" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[✓] ML model already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 2: Frontend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Install frontend dependencies
Write-Host "Installing frontend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
Push-Location frontend
if (!(Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[✗] Failed to install frontend dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "[✓] Frontend dependencies already installed" -ForegroundColor Green
}
Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 3: Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start Redis if installed
if ($redisInstalled) {
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    Start-Process -FilePath "redis-server" -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "[✓] Redis started" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Backend (Terminal 1):" -ForegroundColor Yellow
Write-Host "   cd 'd:\Coding\AI healthcare'" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. Frontend (Terminal 2):" -ForegroundColor Yellow
Write-Host "   cd 'd:\Coding\AI healthcare\frontend'" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Or run the quick start script: .\start.ps1" -ForegroundColor Yellow
Write-Host ""
