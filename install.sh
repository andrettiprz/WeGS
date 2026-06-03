#!/usr/bin/env bash
# ╔══════════════════════════════════════════╗
# ║     WeGS v1.0 — One-Line Installer       ║
# ║   Ground Station Web Visualizer         ║
# ╚══════════════════════════════════════════╝
# curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
REPO_URL="https://github.com/andrettiprz/WeGS.git"
TARBALL_URL="https://github.com/andrettiprz/WeGS/archive/refs/heads/main.tar.gz"
INSTALL_DIR="${WEGS_DIR:-$HOME/.wegs}"
PYTHON=""; NODE=""; GIT=""

prompt() { printf "  ${CYAN}%s${NC} " "$1"; read -r answer; echo "$answer"; }
ok() { printf "  ${GREEN}✓${NC} %s\n" "$1"; }
warn() { printf "  ${YELLOW}⚠${NC}  %s\n" "$1"; }
err() { printf "  ${RED}✗${NC} %s\n" "$1"; }
section() { printf "\n${CYAN}── %s${NC}\n" "$1"; }

# ── Banner ──
clear 2>/dev/null || true
printf "${CYAN}"
printf "╔══════════════════════════════════════════╗\n"
printf "║     WeGS v1.0 — One-Line Installer       ║\n"
printf "║   Ground Station Web Visualizer         ║\n"
printf "╚══════════════════════════════════════════╝\n"
printf "${NC}\n"

# ── Detect OS ──
OS="unknown"
case "$(uname -s)" in
    Linux*)  OS="linux";;
    Darwin*) OS="macos";;
    MINGW*|MSYS*|CYGWIN*) OS="windows";;
esac

# ─────────────────────────────────────────────
# Step 1: Check & install dependencies
# ─────────────────────────────────────────────
section "Checking dependencies"

# ── Python ──
found_python=false
for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2 2>/dev/null || echo 0)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            PYTHON="$cmd"; found_python=true; ok "$cmd $ver"
            break
        fi
    fi
done
if ! $found_python; then
    err "Python 3.8+ not found — WeGS requires it."
    answer=$(prompt "Install Python now? (Y/n)")
    if [ "${answer:-y}" != "n" ] && [ "${answer:-y}" != "N" ]; then
        case "$OS" in
            macos)
                if command -v brew &>/dev/null; then brew install python@3.12
                else err "Install Homebrew first: https://brew.sh"; exit 1; fi ;;
            linux)
                if command -v apt-get &>/dev/null; then sudo apt-get install -y python3 python3-pip
                elif command -v dnf &>/dev/null; then sudo dnf install -y python3 python3-pip
                elif command -v pacman &>/dev/null; then sudo pacman -S --noconfirm python python-pip
                else err "Cannot auto-install Python. Install it: https://python.org"; exit 1; fi ;;
            windows) err "Install Python from https://python.org (check 'Add to PATH')"; exit 1 ;;
        esac
        # Re-detect
        PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "")
        [ -n "$PYTHON" ] && ok "Python installed: $PYTHON" || { err "Python install failed"; exit 1; }
    else
        err "Python is required. Exiting."; exit 1
    fi
fi

# ── Git ──
if command -v git &>/dev/null; then
    GIT="git"; ok "git $(git --version | grep -oE '[0-9.]+' | head -1)"
else
    warn "Git not found — will download WeGS via tarball (slower updates)"
fi

# ── Node.js ──
found_node=false
for cmd in node node20 node22 node18; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+')
        if [ "$ver" -ge 18 ]; then
            NODE="$cmd"; found_node=true; ok "Node.js v$ver"
            break
        fi
    fi
done
if ! $found_node; then
    warn "Node.js 18+ not found — the web UI needs it to build."
    answer=$(prompt "Install Node.js now? (Y/n)")
    if [ "${answer:-y}" != "n" ] && [ "${answer:-y}" != "N" ]; then
        case "$OS" in
            macos) brew install node || err "brew install node failed";;
            linux)
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null && sudo apt-get install -y nodejs 2>/dev/null || \
                curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash - 2>/dev/null && sudo dnf install -y nodejs 2>/dev/null || \
                err "Auto-install failed. Install Node from https://nodejs.org";;
            windows) err "Install Node.js from https://nodejs.org (LTS version)";;
        esac
        NODE=$(command -v node 2>/dev/null || echo "")
        [ -n "$NODE" ] && ok "Node.js installed" || warn "Node install may have failed. Try manually."
    fi
fi

# ─────────────────────────────────────────────
# Step 2: Get WeGS
# ─────────────────────────────────────────────
section "Installing WeGS"

if [ -d "$INSTALL_DIR/.git" ]; then
    warn "WeGS already installed. Updating..."
    cd "$INSTALL_DIR" && git pull --ff-only origin main 2>/dev/null || ok "Already up to date"
elif [ -d "$INSTALL_DIR" ]; then
    warn "$INSTALL_DIR exists but is not a git repo. Overwrite?"
    answer=$(prompt "Overwrite? (y/N)")
    if [ "${answer:-n}" = "y" ] || [ "${answer:-n}" = "Y" ]; then
        rm -rf "$INSTALL_DIR"
    else
        err "Aborted."; exit 0
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    if [ -n "$GIT" ]; then
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>&1 | tail -1
        ok "Cloned via git"
    else
        mkdir -p "$INSTALL_DIR"
        curl -fsSL "$TARBALL_URL" | tar -xz --strip-components=1 -C "$INSTALL_DIR" 2>/dev/null
        ok "Downloaded via tarball"
    fi
fi
cd "$INSTALL_DIR"

# ─────────────────────────────────────────────
# Step 3: Install dependencies
# ─────────────────────────────────────────────
section "Installing dependencies"
$PYTHON -m pip install --quiet -r requirements.txt 2>&1 | tail -1
ok "Python packages"

if [ -n "$NODE" ]; then
    cd "$INSTALL_DIR/web"
    npm install --silent 2>&1 | tail -1
    cd "$INSTALL_DIR"
    ok "Node packages"
    # Build web
    npm run build 2>&1 | tail -1
    ok "Web UI built"
fi

# ─────────────────────────────────────────────
# Step 4: Configuration wizard
# ─────────────────────────────────────────────
section "Configuration"
$PYTHON wegs/setup_wizard.py

# ─────────────────────────────────────────────
# Step 5: Ready
# ─────────────────────────────────────────────
section "Ready"
echo ""
printf "${GREEN}╔══════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║        ✅  WeGS is installed!            ║${NC}\n"
printf "${GREEN}╠══════════════════════════════════════════╣${NC}\n"
printf "${GREEN}║                                          ║${NC}\n"
printf "${GREEN}║   Start:  cd %s && python wegs.py start   ${NC}\n" "$INSTALL_DIR"
printf "${GREEN}║   Web:    http://localhost:5173          ║${NC}\n"
printf "${GREEN}║   Config: %s/config.json${NC}\n" "$INSTALL_DIR"
printf "${GREEN}║                                          ║${NC}\n"
printf "${GREEN}║   Commands:                              ║${NC}\n"
printf "${GREEN}║     python wegs.py start                 ║${NC}\n"
printf "${GREEN}║     python wegs.py add telegram          ║${NC}\n"
printf "${GREEN}║     python wegs.py add supabase          ║${NC}\n"
printf "${GREEN}║     python wegs.py reconfigure           ║${NC}\n"
printf "${GREEN}╚══════════════════════════════════════════╝${NC}\n"
echo ""
