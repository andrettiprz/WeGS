#!/usr/bin/env bash
set -euo pipefail

# ╔══════════════════════════════════════════╗
# ║         WeGS v1.0 Installer              ║
# ║   Ground Station Web Visualizer         ║
# ╚══════════════════════════════════════════╝

REPO="https://github.com/andrettiprz/WeGS.git"
INSTALL_DIR="$HOME/.wegs"
PYTHON=""
NODE=""
QUIET=false

# ── Help ──
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash"
    echo ""
    echo "Options (passed as environment variables):"
    echo "  WEGS_DIR=/custom/path    Install to custom directory (default: ~/.wegs)"
    echo "  WEGS_QUIET=true          Skip interactive config"
    exit 0
fi

# ── Args ──
INSTALL_DIR="${WEGS_DIR:-$INSTALL_DIR}"
QUIET="${WEGS_QUIET:-false}"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         WeGS v1.0 Installer              ║"
echo "║   Ground Station Web Visualizer         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check dependencies ──
find_python() {
    for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
                PYTHON="$cmd"
                echo "  ✓ $cmd ($ver)"
                return 0
            fi
        fi
    done
    return 1
}

find_node() {
    for cmd in node node20 node22; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+')
            if [ "$ver" -ge 18 ]; then
                NODE="$cmd"
                echo "  ✓ $cmd v$ver"
                return 0
            fi
        fi
    done
    return 1
}

echo "── Checking dependencies ──────────────────"
if ! find_python; then
    echo "  ✗ Python 3.8+ not found. Install it: https://python.org"
    exit 1
fi
if ! find_node; then
    echo "  ✗ Node.js 18+ not found. Install it: https://nodejs.org"
    exit 1
fi

# ── Clone ──
echo ""
echo "── Installing WeGS ────────────────────────"
if [ -d "$INSTALL_DIR" ]; then
    echo "  ⚠ $INSTALL_DIR already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull --ff-only origin main 2>/dev/null || true
else
    git clone --depth 1 "$REPO" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# ── Python deps ──
echo "  ⏳ Installing Python packages..."
$PYTHON -m pip install -r requirements.txt --quiet 2>&1 | tail -1

# ── Node deps ──
echo "  ⏳ Installing Node packages..."
cd "$INSTALL_DIR/web"
npm install --silent 2>&1 | tail -1
cd "$INSTALL_DIR"

# ── Config wizard ──
echo ""
if [ "$QUIET" = false ]; then
    $PYTHON wegs/setup_wizard.py
else
    echo "  ⚡ Skipping config (WEGS_QUIET=true)"
    if [ ! -f "$INSTALL_DIR/config.json" ]; then
        cp config.example.json config.json
    fi
fi

# ── Start ──
echo ""
echo "── Starting WeGS ──────────────────────────"
$PYTHON wegs.py start &

sleep 3
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        ✅  WeGS is ready!                ║"
echo "║                                          ║"
echo "║   🛰️  Watchdog: running                  ║"
echo "║   🌐 Web UI:    http://localhost:5173    ║"
echo "║   ⚙️  Config:    $INSTALL_DIR/config.json ║"
echo "║                                          ║"
echo "║   Commands:                              ║"
echo "║     wegs start       Start services      ║"
echo "║     wegs stop        Stop services       ║"
echo "║     wegs add telegram  Add Telegram bot  ║"
echo "║     wegs add supabase  Add Supabase      ║"
echo "║     wegs reconfigure  Reconfigure        ║"
echo "║     wegs status       Show status        ║"
echo "╚══════════════════════════════════════════╝"
echo ""
