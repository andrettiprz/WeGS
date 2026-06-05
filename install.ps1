# WeGS Windows Installer
# Run in PowerShell: irm https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.ps1 | iex
$ErrorActionPreference = "Continue"
$TarballUrl = "https://github.com/andrettiprz/WeGS/archive/refs/heads/main.zip"
$InstallDir = "$env:USERPROFILE\.wegs"

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     WeGS v1.0 Installer                  ║" -ForegroundColor Cyan
Write-Host "║   Ground Station Web Visualizer         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    Get-Command python -ErrorAction Stop | Out-Null
    $ver = & python --version 2>&1
    Write-Host "  OK $ver" -ForegroundColor Green
} catch {
    Write-Host "  Python 3.8+ required. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Download and extract
if (Test-Path $InstallDir) {
    $ans = Read-Host "  WeGS already installed. Reinstall? (y/N)"
    if ($ans -ne "y") { exit 0 }
    Remove-Item -Recurse -Force $InstallDir
}

Write-Host "  Downloading..."
Invoke-WebRequest -Uri $TarballUrl -OutFile "$env:TEMP\wegs.zip"
Expand-Archive -Path "$env:TEMP\wegs.zip" -DestinationPath "$env:TEMP\wegs_extract" -Force
$d = Get-ChildItem "$env:TEMP\wegs_extract" | Select-Object -First 1
Move-Item $d.FullName $InstallDir -Force
Remove-Item "$env:TEMP\wegs.zip","$env:TEMP\wegs_extract" -Recurse -Force
Write-Host "  OK Installed" -ForegroundColor Green

# Install deps
Set-Location $InstallDir
python -m pip install --quiet -r requirements.txt 2>$null
Write-Host "  OK Dependencies" -ForegroundColor Green

# Setup wizard
Write-Host ""
python wegs/setup_wizard.py

# Done
Write-Host ""

# Make 'wegs' available globally (Windows PATH)
$batPath = "$InstallDir\wegs.bat"
Set-Content -Path $batPath -Value "@echo off`npython `"$InstallDir\wegs.py`" %*"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    $env:Path += ";$InstallDir"
    Write-Host "  OK Added to PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        WeGS is ready!                    ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                          ║" -ForegroundColor Green
Write-Host "║  wegs start       Start server           ║" -ForegroundColor Green
Write-Host "║  wegs dashboard   Open browser           ║" -ForegroundColor Green
Write-Host "║  wegs stop        Stop server            ║" -ForegroundColor Green
Write-Host "║  wegs status      Show status            ║" -ForegroundColor Green
Write-Host "║  wegs uninstall   Remove WeGS            ║" -ForegroundColor Green
Write-Host "║                                          ║" -ForegroundColor Green
Write-Host "║  Restart terminal to use 'wegs' command  ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
