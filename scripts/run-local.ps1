# BranchOS Local Development Startup Script
# Activates venv, starts API backend and Streamlit dashboard

param(
    [string]$ApiPort = "8000",
    [string]$DashboardPort = "8502"
)

Write-Host "🚀 BranchOS Local Development Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment found" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Check if required packages are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
$pythonCheck = & python -c "import uvicorn, streamlit, fastapi" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Missing dependencies. Installing..." -ForegroundColor Red
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Dependencies verified" -ForegroundColor Green
Write-Host ""

# Start API backend in background
Write-Host "🌐 Starting FastAPI backend on port $ApiPort..." -ForegroundColor Yellow
$apiJob = Start-Job -ScriptBlock {
    param($port)
    & python -m uvicorn branchberg.app.main:app --reload --port $port
} -ArgumentList $ApiPort

# Wait a moment for API to start
Start-Sleep -Seconds 3

# Check if API started successfully
$apiState = Get-Job -Id $apiJob.Id
if ($apiState.State -eq "Running") {
    Write-Host "✅ API backend started (Job ID: $($apiJob.Id))" -ForegroundColor Green
    Write-Host "   URL: http://localhost:$ApiPort" -ForegroundColor Cyan
    Write-Host "   Docs: http://localhost:$ApiPort/docs" -ForegroundColor Cyan
} else {
    Write-Host "❌ API backend failed to start" -ForegroundColor Red
    Receive-Job -Id $apiJob.Id
    Remove-Job -Id $apiJob.Id
    exit 1
}

Write-Host ""

# Start Streamlit dashboard in background
Write-Host "📊 Starting Streamlit dashboard on port $DashboardPort..." -ForegroundColor Yellow
$dashboardJob = Start-Job -ScriptBlock {
    param($port)
    & streamlit run branchberg/dashboard/streamlit_app.py --server.port $port --server.headless true
} -ArgumentList $DashboardPort

# Wait a moment for dashboard to start
Start-Sleep -Seconds 3

# Check if dashboard started successfully
$dashboardState = Get-Job -Id $dashboardJob.Id
if ($dashboardState.State -eq "Running") {
    Write-Host "✅ Dashboard started (Job ID: $($dashboardJob.Id))" -ForegroundColor Green
    Write-Host "   URL: http://localhost:$DashboardPort" -ForegroundColor Cyan
} else {
    Write-Host "❌ Dashboard failed to start" -ForegroundColor Red
    Receive-Job -Id $dashboardJob.Id
    Remove-Job -Id $dashboardJob.Id
    Stop-Job -Id $apiJob.Id
    Remove-Job -Id $apiJob.Id
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✨ All services running!" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Quick Links:" -ForegroundColor Cyan
Write-Host "   API:       http://localhost:$ApiPort" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:$ApiPort/docs" -ForegroundColor White
Write-Host "   Dashboard: http://localhost:$DashboardPort" -ForegroundColor White
Write-Host ""
Write-Host "📝 Job IDs:" -ForegroundColor Cyan
Write-Host "   API:       $($apiJob.Id)" -ForegroundColor White
Write-Host "   Dashboard: $($dashboardJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "To stop services, run:" -ForegroundColor Yellow
Write-Host "   Stop-Job -Id $($apiJob.Id), $($dashboardJob.Id)" -ForegroundColor White
Write-Host "   Remove-Job -Id $($apiJob.Id), $($dashboardJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to exit (services will continue in background)" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# Keep script running to show that services are active
# User can Ctrl+C to exit without stopping the background jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ""
    Write-Host "Script terminated. Services are still running in background." -ForegroundColor Yellow
}
