#!/usr/bin/env bash
# ============================================================================
#  System Scanner — install.bash
#  Installs all dependencies and prepares the app on Ubuntu.
#  Run:  bash install.bash
# ============================================================================

set -e

APP_NAME="system-scanner"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
DESKTOP_FILE="$SCRIPT_DIR/packaging/system-scanner.desktop"
LOCAL_DESKTOP_DIR="$HOME/.local/share/applications"
LOCAL_ICON_DIR="$HOME/.local/share/icons"

echo "========================================"
echo "  System Scanner — Installer"
echo "========================================"
echo ""

# ── 1. Check Python 3 ─────────────────────────────────────────────────
echo "[1/7] Checking Python 3…"

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 7 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3.7+ is required but not found."
    echo "        Install it with:  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "  Found: $($PYTHON_CMD --version)"

# ── 2. Install system dependencies ────────────────────────────────────
echo ""
echo "[2/7] Checking system packages…"

PACKAGES_NEEDED=""

# Check for python3-venv
if ! $PYTHON_CMD -m venv --help &>/dev/null; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED python3-venv"
fi

# Check for pip
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED python3-pip"
fi

# PySide6 needs some Qt libs on Ubuntu
if ! dpkg -s libgl1-mesa-glx &>/dev/null 2>&1; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED libgl1-mesa-glx"
fi

if ! dpkg -s libegl1 &>/dev/null 2>&1; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED libegl1"
fi

if ! dpkg -s libxkbcommon0 &>/dev/null 2>&1; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED libxkbcommon0"
fi

if ! dpkg -s libdbus-1-3 &>/dev/null 2>&1; then
    PACKAGES_NEEDED="$PACKAGES_NEEDED libdbus-1-3"
fi

if [ -n "$PACKAGES_NEEDED" ]; then
    echo "  Installing system packages:$PACKAGES_NEEDED"
    sudo apt-get update -qq
    sudo apt-get install -y -qq $PACKAGES_NEEDED
else
    echo "  All system packages already present."
fi

# ── 3. Create virtual environment ─────────────────────────────────────
echo ""
echo "[3/7] Setting up virtual environment…"

if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment already exists at $VENV_DIR"
else
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "  Created virtual environment at $VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"

# ── 4. Upgrade pip ────────────────────────────────────────────────────
echo ""
echo "[4/7] Upgrading pip…"
pip install --upgrade pip --quiet

# ── 5. Install Python dependencies ───────────────────────────────────
echo ""
echo "[5/7] Installing Python dependencies…"
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo "  Dependencies installed."

# ── 6. Create data directory and make scripts executable ──────────────
echo ""
echo "[6/7] Setting up project…"

mkdir -p "$SCRIPT_DIR/data"
chmod +x "$SCRIPT_DIR/run.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/build.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/uninstall.bash" 2>/dev/null || true
echo "  Data directory ready. Scripts made executable."

# ── 7. Install desktop launcher ──────────────────────────────────────
echo ""
echo "[7/7] Installing desktop launcher…"

mkdir -p "$LOCAL_DESKTOP_DIR"
mkdir -p "$LOCAL_ICON_DIR"

# Copy icon
if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
    cp "$SCRIPT_DIR/assets/icon.png" "$LOCAL_ICON_DIR/system-scanner.png"
fi

# Generate .desktop file with correct paths
cat > "$LOCAL_DESKTOP_DIR/system-scanner.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=System Scanner
Comment=Network scanning and port detection utility
Exec=$SCRIPT_DIR/run.sh
Icon=$LOCAL_ICON_DIR/system-scanner.png
Terminal=false
Categories=Network;Utility;System;
StartupNotify=true
StartupWMClass=system-scanner
EOF

chmod +x "$LOCAL_DESKTOP_DIR/system-scanner.desktop"

# Update desktop database if available
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$LOCAL_DESKTOP_DIR" 2>/dev/null || true
fi

echo "  Desktop launcher installed."

# ── Done ──────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "  Installation complete!"
echo "========================================"
echo ""
echo "  To run the app:"
echo "    ./run.sh"
echo ""
echo "  Or launch 'System Scanner' from your desktop menu."
echo ""
echo "  To uninstall:"
echo "    bash uninstall.bash"
echo ""
