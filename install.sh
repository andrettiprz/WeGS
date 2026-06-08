#!/usr/bin/env bash
# WeGS v1.0 -- One-Line Installer
# curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash
# curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash -s -- -y
set -euo pipefail

REPO_URL="https://github.com/andrettiprz/WeGS.git"
INSTALL_DIR="${WEGS_DIR:-$HOME/.wegs}"
AUTO_YES=false

# Parse flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes) AUTO_YES=true; shift;;
        --dir) INSTALL_DIR="$2"; shift 2;;
        --help|-h) echo "Usage: curl ... | bash [-s -- -y]"; exit 0;;
        *) shift;;
    esac
done

# ── Colors ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'
ok()   { printf "  ${GREEN}[OK]${NC} %s\n" "$1"; }
warn() { printf "  ${YELLOW}[!!]${NC} %s\n" "$1"; }
err()  { printf "  ${RED}[XX]${NC} %s\n" "$1"; }
step() { printf "\n${CYAN}=== %s ===${NC}\n" "$1"; }

# ── Banner ──
printf "${CYAN}\n"
printf "  WeGS v1.0 -- Ground Station Web Visualizer\n"
printf "  One-line installer\n"
printf "${NC}\n"

# ── Detect OS ──
OS="unknown"
case "$(uname -s)" in
    Linux*)  OS="linux";;
    Darwin*) OS="macos";;
    MINGW*|MSYS*|CYGWIN*) OS="windows";;
esac

# ─────────────────────────────────────────────
# Step 1: Python
# ─────────────────────────────────────────────
step "Checking Python"
PYTHON=""
# Allow explicit override: WEGS_PYTHON=python3.12 curl ... | bash
if [ -n "${WEGS_PYTHON:-}" ]; then
    if command -v "$WEGS_PYTHON" &>/dev/null && "$WEGS_PYTHON" -c "import xml.parsers.expat, ssl" &>/dev/null 2>&1; then
        ver=$("$WEGS_PYTHON" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        PYTHON="$WEGS_PYTHON"; ok "WEGS_PYTHON: $WEGS_PYTHON $ver"
    else
        warn "WEGS_PYTHON=$WEGS_PYTHON not found or pip broken, auto-detecting..."
    fi
fi
if [ -z "$PYTHON" ]; then
    for cmd in python3 python python3.12 python3.11 python3.10 python3.9 python3.13; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2 2>/dev/null || echo 0)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            # Verify Python actually works (catches broken installs like bad expat)
            if "$cmd" -c "import xml.parsers.expat" &>/dev/null && "$cmd" -c "import ssl" &>/dev/null; then
                    PYTHON="$cmd"; ok "$cmd $ver"; break
                else
                    warn "$cmd $ver found but pip is broken -- skipping"
                fi
            fi
        fi
    done
    if [ -z "$PYTHON" ]; then
        err "No working Python 3.8+ found with pip."
        if $AUTO_YES; then
            case "$OS" in
                macos) brew install python@3.12 2>/dev/null || { err "brew install failed"; exit 1; };;
                linux) sudo apt-get install -y python3 python3-pip 2>/dev/null || { err "apt-get failed"; exit 1; };;
            esac
            PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "")
            [ -n "$PYTHON" ] && ok "Python installed: $PYTHON" || { err "Python install failed"; exit 1; }
        else
            echo "  Install Python 3.8+ then re-run: https://python.org"
            exit 1
        fi
    fi
fi

# ─────────────────────────────────────────────
# Step 2: Clone / update
# ─────────────────────────────────────────────
step "Installing WeGS"
if [ -d "$INSTALL_DIR" ]; then
    if [ -d "$INSTALL_DIR/.git" ]; then
        warn "WeGS exists. Updating..."
        git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null && ok "Updated" || ok "Already up to date"
    else
        warn "$INSTALL_DIR exists and is not a git repo."
        if $AUTO_YES; then
            rm -rf "$INSTALL_DIR"
        else
            printf "  Overwrite? [y/N] "; read -r answer
            if [ "${answer:-n}" = "y" ] || [ "${answer:-n}" = "Y" ]; then
                rm -rf "$INSTALL_DIR"
            else
                err "Aborted."; exit 0
            fi
        fi
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>&1 | tail -1
    ok "Cloned"
fi

# ─────────────────────────────────────────────
# Step 3: Python deps
# ─────────────────────────────────────────────
step "Python packages"
if [ "$OS" = "macos" ]; then
    $PYTHON -m pip install --quiet --break-system-packages -r "$INSTALL_DIR/requirements.txt" 2>&1 | tail -3
else
    $PYTHON -m pip install --quiet -r "$INSTALL_DIR/requirements.txt" 2>&1 | tail -3
fi
ok "Python dependencies"

# ─────────────────────────────────────────────
# Step 4: Node.js + build web UI
# ─────────────────────────────────────────────
step "Building Web UI"

if command -v node &>/dev/null; then
    ver=$(node --version 2>&1 | grep -oE '[0-9]+' | head -1)
    if [ -n "$ver" ] && [ "$ver" -ge 18 ] 2>/dev/null; then
        ok "Node.js $(node --version)"
        cd "$INSTALL_DIR/web"
        npm install --silent 2>&1 | tail -1
        npm run build 2>&1 | tail -3
        cd "$INSTALL_DIR"
        ok "Web UI built"
    else
        warn "Node.js >= 18 required. Trying to install..."
        if $AUTO_YES; then
            case "$OS" in
                macos) brew install node 2>/dev/null;;
                linux) curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs;;
            esac
        fi
        if command -v node &>/dev/null; then
            cd "$INSTALL_DIR/web" && npm install --silent && npm run build && cd "$INSTALL_DIR"
            ok "Web UI built (2nd attempt)"
        else
            warn "Skipping web UI -- install Node.js 18+ manually then: cd ~/.wegs/web && npm install && npm run build"
        fi
    fi
else
    warn "Node.js not found. Install Node.js 18+ then:"
    echo "  cd ~/.wegs/web && npm install && npm run build"
fi

# ─────────────────────────────────────────────
# Step 5: Config
# ─────────────────────────────────────────────
step "Configuration"

CONFIG_FILE="$INSTALL_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    if $AUTO_YES; then
        OUTPUT="${WEGS_OUTPUT:-}"
        if [ -z "$OUTPUT" ]; then
            OUTPUT="$HOME/Documents/live_output"
        fi
        mkdir -p "$OUTPUT" 2>/dev/null || warn "Cannot create $OUTPUT"
        $PYTHON -c "
import json
cfg = {
    'station_name': 'My Ground Station',
    'output_folder': '${OUTPUT//\'/\'\\\'\'}'.replace('\\\\', '/'),
    'telegram': {'enabled': False, 'bot_token': '', 'chat_id': ''},
    'supabase': {'enabled': False, 'url': '', 'anon_key': ''},
    'processing': {'wait_seconds': 1200, 'thumbnail_width': 400, 'thumbnail_quality': 70, 'timezone': 'UTC'},
    'sdr_map': {}
}
json.dump(cfg, open('$CONFIG_FILE', 'w'), indent=4)
"
        ok "Config created: $CONFIG_FILE"
        echo "  output_folder = $OUTPUT"
    else
        $PYTHON "$INSTALL_DIR/wegs/setup_wizard.py"
    fi
else
    ok "Config already exists"
fi

# ─────────────────────────────────────────────
# Step 6: Global 'wegs' command
# ─────────────────────────────────────────────
step "Global command"

create_symlink() {
    local target="$1"
    if [ -L "$target" ] || [ -f "$target" ]; then
        rm -f "$target" 2>/dev/null
    fi
    # Create wrapper script
    cat > "$target" << 'WRAPPER'
#!/usr/bin/env bash
INSTALL_DIR="${WEGS_DIR:-$HOME/.wegs}"
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
exec "$PYTHON" "$INSTALL_DIR/wegs.py" "$@"
WRAPPER
    chmod +x "$target"
}

LINKED=false

# Try /usr/local/bin (macOS/Linux, in default PATH)
if [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    create_symlink "/usr/local/bin/wegs"
    ok "wegs -> /usr/local/bin/wegs"
    LINKED=true
fi

# Try ~/.local/bin (Linux user PATH)
if ! $LINKED; then
    LOCAL_BIN="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN" 2>/dev/null
    if [ -d "$LOCAL_BIN" ] && [ -w "$LOCAL_BIN" ]; then
        create_symlink "$LOCAL_BIN/wegs"
        ok "wegs -> $LOCAL_BIN/wegs"
        # Add to PATH if needed
        if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
            case "$SHELL" in
                */zsh)  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc";;
                */bash) echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc";;
            esac
            echo "  Added $LOCAL_BIN to PATH. Restart terminal or: source ~/.zshrc"
        fi
        LINKED=true
    fi
fi

if ! $LINKED; then
    warn "Cannot create global 'wegs' command."
    echo "  Add alias manually: alias wegs='python3 $INSTALL_DIR/wegs.py'"
    echo "  Or run directly:   python3 $INSTALL_DIR/wegs.py start"
fi

# ─────────────────────────────────────────────
# Step 7: Done
# ─────────────────────────────────────────────
step "Done"
echo ""
printf "${GREEN}  WeGS is installed!${NC}\n"
echo ""
if $LINKED; then
    echo "  Run:   wegs start"
    echo "  Web:   http://localhost:5173"
else
    echo "  Run:   cd $INSTALL_DIR && python3 wegs.py start"
    echo "  Web:   http://localhost:5173"
fi
echo "  Config: $CONFIG_FILE"
echo ""
