# Quick Start Script - Launches all services
# Run this after running deploy.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting MediVoice AI Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if setup was run
if (!(Test-Path "venv")) {
    Write-Host "[!] Setup not complete. Please run .\deploy.ps1 first" -ForegroundColor Red
    exit 1
}

# Start Redis if available
try {
    redis-server --version 2>&1 | Out-Null
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    Start-Process -FilePath "redis-server" -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "[✓] Redis started" -ForegroundColor Green
} catch {
    Write-Host "[!] Redis not found - continuing without cache" -ForegroundColor Yellow
}

# Start Backend
Write-Host "Starting Backend API..." -ForegroundColor Yellow
$backendPath = Join-Path $scriptPath ""
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv\Scripts\Activate.ps1; uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "[✓] Backend starting on http://localhost:8000" -ForegroundColor Green

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $scriptPath "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "[✓] Frontend starting on http://localhost:5173" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Application Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop services" -ForegroundColor Yellow
Write-Host ""

# Wait and open browser
Write-Host "Opening application in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"
