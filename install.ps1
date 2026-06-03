# WeGS Windows Installer
# Run in PowerShell: irm https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/andrettiprz/WeGS.git"
$InstallDir = "$env:USERPROFILE\.wegs"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   WeGS v1.0 Installer (Windows)" -ForegroundColor Cyan
Write-Host "   Ground Station Web Visualizer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $py = (Get-Command python -ErrorAction Stop).Source
    $ver = & python --version 2>&1
    Write-Host "  OK $ver" -ForegroundColor Green
} catch {
    Write-Host "  ERROR Python 3.8+ not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $node = (Get-Command node -ErrorAction Stop).Source
    $nver = & node --version 2>&1
    Write-Host "  OK Node $nver" -ForegroundColor Green
} catch {
    Write-Host "  ERROR Node.js 18+ not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Clone or update
if (Test-Path $InstallDir) {
    Write-Host "  Updating existing install..."
    Set-Location $InstallDir
    git pull origin main 2>$null
} else {
    Write-Host "  Cloning WeGS..."
    git clone --depth 1 $Repo $InstallDir 2>$null
}
Set-Location $InstallDir

# Install deps
Write-Host "  Installing Python packages..."
python -m pip install -r requirements.txt --quiet 2>$null

Write-Host "  Installing Node packages..."
Set-Location "$InstallDir\web"
npm install --silent 2>$null
Set-Location $InstallDir

# Config wizard
Write-Host ""
python wegs/setup_wizard.py

# Start
Write-Host ""
Write-Host "  Starting WeGS..." -ForegroundColor Cyan
Start-Process python -ArgumentList "wegs.py", "start" -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "   WeGS is running!" -ForegroundColor Green
Write-Host "   http://localhost:5173" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
