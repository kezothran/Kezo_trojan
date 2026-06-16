#!/bin/bash
# uninstall.sh - Completely removes the System Scanner from Ubuntu

INSTALL_DIR="$HOME/.local/share/system-scanner"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "========================================"
echo "  Uninstalling System Scanner"
echo "========================================"

echo "[1/2] Removing application files..."
rm -rf "$INSTALL_DIR"

echo "[2/2] Removing desktop entry..."
rm -f "$DESKTOP_DIR/system-scanner.desktop"

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" || true
fi

echo ""
echo "========================================"
echo "  Uninstallation Complete!"
echo "========================================"
