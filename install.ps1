# WeGS Windows Installer
# Run in PowerShell: irm https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.ps1 | iex

$ErrorActionPreference = "Continue"
$RepoUrl = "https://github.com/andrettiprz/WeGS.git"
$TarballUrl = "https://github.com/andrettiprz/WeGS/archive/refs/heads/main.zip"
$InstallDir = "$env:USERPROFILE\.wegs"

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     WeGS v1.0 — Windows Installer        ║" -ForegroundColor Cyan
Write-Host "║   Ground Station Web Visualizer         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

function ok { Write-Host "  ✓ $args" -ForegroundColor Green }
function warn { Write-Host "  ⚠ $args" -ForegroundColor Yellow }
function err { Write-Host "  ✗ $args" -ForegroundColor Red }

# ── Check Python ──
Write-Host "── Checking dependencies ──────────────────" -ForegroundColor Cyan
$python = $null
try {
    $python = Get-Command python -ErrorAction Stop | Select-Object -ExpandProperty Source
    $ver = & python --version 2>&1
    ok "$ver"
} catch {
    err "Python 3.8+ not found"
    $answer = Read-Host "  Install Python now? (Y/n)"
    if ($answer -ne "n" -and $answer -ne "N") {
        Write-Host "  Opening https://python.org/downloads/ ..."
        Start-Process "https://python.org/downloads/"
        Write-Host "  After installing, run this script again."
        exit 0
    }
    err "Python is required. Exiting."
    exit 1
}

# ── Check Git ──
$git = $null
try { $git = Get-Command git -ErrorAction Stop | Select-Object -ExpandProperty Source; ok "git found" }
catch {
    warn "Git not found — will download via ZIP"
}

# ── Check Node ──
$node = $null
try {
    $node = Get-Command node -ErrorAction Stop | Select-Object -ExpandProperty Source
    $nver = & node --version 2>&1
    ok "Node.js $nver"
} catch {
    warn "Node.js not found"
    $answer = Read-Host "  Install Node.js now? (Y/n)"
    if ($answer -ne "n" -and $answer -ne "N") {
        Write-Host "  Opening https://nodejs.org ..."
        Start-Process "https://nodejs.org/"
        Write-Host "  After installing, run this script again."
        exit 0
    }
    warn "Skipping Node.js — web UI will use pre-built version"
}

# ── Download WeGS ──
Write-Host ""
Write-Host "── Installing WeGS ────────────────────────" -ForegroundColor Cyan

if (Test-Path "$InstallDir\.git") {
    warn "Already installed. Updating..."
    Set-Location $InstallDir
    git pull origin main 2>$null
    ok "Updated"
} elseif (Test-Path $InstallDir) {
    Write-Host "  $InstallDir already exists."
    $answer = Read-Host "  Overwrite? (y/N)"
    if ($answer -eq "y" -or $answer -eq "Y") {
        Remove-Item -Recurse -Force $InstallDir
    } else {
        err "Aborted."; exit 0
    }
}

if (!(Test-Path $InstallDir)) {
    if ($git) {
        git clone --depth 1 $RepoUrl $InstallDir 2>$null
        ok "Cloned via git"
    } else {
        Write-Host "  Downloading..."
        Invoke-WebRequest -Uri $TarballUrl -OutFile "$env:TEMP\wegs.zip"
        Expand-Archive -Path "$env:TEMP\wegs.zip" -DestinationPath "$env:TEMP\wegs_extract" -Force
        $extracted = Get-ChildItem "$env:TEMP\wegs_extract" | Select-Object -First 1
        Move-Item $extracted.FullName $InstallDir -Force
        Remove-Item "$env:TEMP\wegs.zip" -Force
        Remove-Item "$env:TEMP\wegs_extract" -Recurse -Force
        ok "Downloaded via ZIP"
    }
}

Set-Location $InstallDir

# ── Install deps ──
Write-Host "  Installing Python packages..."
python -m pip install --quiet -r requirements.txt 2>$null
ok "Python packages"

if ($node) {
    Set-Location "$InstallDir\web"
    npm install --silent 2>$null
    npm run build 2>$null
    Set-Location $InstallDir
    ok "Web UI built"
} else {
    ok "Web UI (pre-built)"
}

# ── Wizard ──
Write-Host ""
python wegs/setup_wizard.py

# ── Create auto-start services ──
Write-Host ""
Write-Host "── Setting up auto-start ──────────────────" -ForegroundColor Cyan
$batContent = @"
@echo off
cd /d $InstallDir
start "" python -m http.server 5173 --directory web\dist
start "" python -m wegs.monitor
timeout /T 31536000 /NOBREAK >nul
exit
"@
Set-Content -Path "$InstallDir\start_services.bat" -Value $batContent
ok "Service script created"

# Create scheduled task for auto-start on boot
schtasks /Create /SC ONSTART /TN "WeGS_Startup" /TR "$InstallDir\start_services.bat" /F 2>$null | Out-Null
ok "Auto-start configured"

# Start services now
schtasks /Run /TN "WeGS_Startup" 2>$null | Out-Null
ok "Services started"

# ── Desktop shortcut ──
$desktopContent = "@echo off`nstart http://localhost:5173`nexit"
Set-Content -Path "$env:USERPROFILE\Desktop\Start_WeGS.bat" -Value $desktopContent
ok "Desktop shortcut created"

# ── Open browser ──
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

# ── Done ──
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        ✅  WeGS is running!              ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                          ║" -ForegroundColor Green
Write-Host "║   🌐  http://localhost:5173              ║" -ForegroundColor Green
Write-Host "║   🖥️  Desktop: Start_WeGS.bat            ║" -ForegroundColor Green
Write-Host "║   ⚙️  Config: $InstallDir\config.json    ║" -ForegroundColor Green
Write-Host "║                                          ║" -ForegroundColor Green
Write-Host "║   Auto-starts with Windows               ║" -ForegroundColor Green
Write-Host "║   wegs add telegram | supabase | deploy  ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
