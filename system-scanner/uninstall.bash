#!/usr/bin/env bash
# ============================================================================
#  System Scanner — uninstall.bash
#  Removes virtual environment, desktop launcher, and cached data.
#  Run:  bash uninstall.bash
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
LOCAL_DESKTOP="$HOME/.local/share/applications/system-scanner.desktop"
LOCAL_ICON="$HOME/.local/share/icons/system-scanner.png"

echo "========================================"
echo "  System Scanner — Uninstaller"
echo "========================================"
echo ""

# Remove virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "[1] Removing virtual environment…"
    rm -rf "$VENV_DIR"
    echo "    Removed $VENV_DIR"
else
    echo "[1] No virtual environment found. Skipping."
fi

# Remove desktop launcher
if [ -f "$LOCAL_DESKTOP" ]; then
    echo "[2] Removing desktop launcher…"
    rm -f "$LOCAL_DESKTOP"
    echo "    Removed $LOCAL_DESKTOP"
else
    echo "[2] No desktop launcher found. Skipping."
fi

# Remove icon
if [ -f "$LOCAL_ICON" ]; then
    echo "[3] Removing icon…"
    rm -f "$LOCAL_ICON"
    echo "    Removed $LOCAL_ICON"
else
    echo "[3] No icon found. Skipping."
fi

# Remove data directory
if [ -d "$SCRIPT_DIR/data" ]; then
    echo "[4] Removing scan history data…"
    rm -rf "$SCRIPT_DIR/data"
    echo "    Removed $SCRIPT_DIR/data"
else
    echo "[4] No data directory found. Skipping."
fi

# Update desktop database
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo ""
echo "========================================"
echo "  Uninstall complete."
echo "========================================"
echo ""
echo "  The source files remain in: $SCRIPT_DIR"
echo "  Delete that folder manually if you want a full cleanup."
echo ""
