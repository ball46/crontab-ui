#!/bin/bash
# install.sh — crontab-ui installer
# Supports one-liner:
#   curl -sSL https://raw.githubusercontent.com/yourname/crontab-ui/main/install.sh | bash

set -e

REPO_RAW="https://raw.githubusercontent.com/yourname/crontab-ui/main"
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_NAME="crontab-ui"
MIN_PYTHON_MINOR=8

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'
GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}ℹ️  $*${NC}"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
error()   { echo -e "${RED}❌ $*${NC}"; exit 1; }

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}       crontab-ui  installer             ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── 1. Detect OS ──────────────────────────────────────────────────────────────
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID="$ID"
        OS_LIKE="${ID_LIKE:-}"
    elif [ "$(uname)" = "Darwin" ]; then
        OS_ID="macos"; OS_LIKE=""
    else
        OS_ID="unknown"; OS_LIKE=""
    fi
}
detect_os
info "Detected OS: $OS_ID"

# ── 2. Check / Install Python ─────────────────────────────────────────────────
PYTHON_BIN=""

find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command -v "$cmd" &>/dev/null; then
            VER=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
            if [ "$VER" -ge "$MIN_PYTHON_MINOR" ] 2>/dev/null; then
                PYTHON_BIN="$cmd"; return 0
            fi
        fi
    done
    return 1
}

install_python_ubuntu_debian() {
    info "Installing Python 3 via apt..."
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv
}

install_python_latest_ppa() {
    info "Adding deadsnakes PPA for Python 3.13..."
    sudo apt-get install -y software-properties-common -qq
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update -qq
    sudo apt-get install -y python3.13 python3.13-pip python3.13-venv
}

install_python_fedora() {
    info "Installing Python 3 via dnf..."
    sudo dnf install -y python3 python3-pip
}

install_python_arch() {
    info "Installing Python 3 via pacman..."
    sudo pacman -Sy --noconfirm python python-pip
}

install_python_macos() {
    if command -v brew &>/dev/null; then
        info "Installing Python 3 via Homebrew..."
        brew install python3
    else
        error "Homebrew not found.\nInstall it first: https://brew.sh\nOr download Python from: https://python.org"
    fi
}

if find_python; then
    success "Found Python: $PYTHON_BIN ($($PYTHON_BIN --version))"
else
    warn "Python 3.${MIN_PYTHON_MINOR}+ not found — installing automatically..."

    if [ -t 0 ]; then
        echo ""
        echo "  Choose Python installation method:"
        echo "  [1] Python from distro package manager (recommended, fast)"
        echo "  [2] Python 3.13 latest via deadsnakes PPA (Ubuntu only)"
        echo ""
        read -rp "  Choose [1/2] (default: 1): " PY_CHOICE
        PY_CHOICE="${PY_CHOICE:-1}"
    else
        PY_CHOICE="1"
    fi

    case "$OS_ID" in
        ubuntu|debian|linuxmint|pop)
            [ "$PY_CHOICE" = "2" ] && install_python_latest_ppa || install_python_ubuntu_debian ;;
        fedora|rhel|centos|rocky|almalinux)
            install_python_fedora ;;
        arch|manjaro|endeavouros)
            install_python_arch ;;
        macos)
            install_python_macos ;;
        *)
            if   command -v apt-get &>/dev/null; then install_python_ubuntu_debian
            elif command -v dnf     &>/dev/null; then install_python_fedora
            elif command -v pacman  &>/dev/null; then install_python_arch
            else error "OS not supported for auto-install.\nPlease install Python 3.8+ manually: https://python.org"
            fi ;;
    esac

    find_python || error "Python installation failed. Please install manually: https://python.org"
    success "Python installed: $PYTHON_BIN ($($PYTHON_BIN --version))"
fi

# ── 3. Download / copy script ─────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"
SCRIPT_PATH="$INSTALL_DIR/$SCRIPT_NAME"
SCRIPT_SOURCE="$(dirname "$0")/crontab_ui.py"

if [ -f "$SCRIPT_SOURCE" ]; then
    info "Copying local crontab_ui.py..."
    cp "$SCRIPT_SOURCE" "$SCRIPT_PATH"
else
    info "Downloading crontab_ui.py from GitHub..."
    if command -v curl &>/dev/null; then
        curl -sSL "$REPO_RAW/crontab_ui.py" -o "$SCRIPT_PATH"
    elif command -v wget &>/dev/null; then
        wget -qO "$SCRIPT_PATH" "$REPO_RAW/crontab_ui.py"
    else
        error "curl or wget not found.\nInstall curl: sudo apt install curl"
    fi
fi

sed -i "1s|.*|#!$(command -v $PYTHON_BIN)|" "$SCRIPT_PATH"
chmod +x "$SCRIPT_PATH"
success "Installed to $SCRIPT_PATH"

# ── 4. PATH check ─────────────────────────────────────────────────────────────
EXPORT_LINE='export PATH="$HOME/.local/bin:$PATH"'

get_shell_rc() {
    case "${SHELL:-}" in
        */zsh)  echo "$HOME/.zshrc" ;;
        */fish) echo "$HOME/.config/fish/config.fish" ;;
        *)      echo "$HOME/.bashrc" ;;
    esac
}

if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    SHELL_RC=$(get_shell_rc)
    if ! grep -q '.local/bin' "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# added by crontab-ui installer" >> "$SHELL_RC"
        echo "$EXPORT_LINE" >> "$SHELL_RC"
    fi
    warn "Added PATH to $SHELL_RC — run: source $SHELL_RC (or open a new terminal)"
fi

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
success "crontab-ui installed successfully!"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Usage:"
echo -e "  ${CYAN}crontab-ui${NC}            # auto-detect language"
echo -e "  ${CYAN}crontab-ui --lang en${NC}  # English"
echo -e "  ${CYAN}crontab-ui --lang th${NC}  # Thai"
echo ""
echo "  (textual will be installed automatically on first run)"
echo ""
