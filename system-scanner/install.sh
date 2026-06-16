#!/bin/bash
# install.sh - Installs the System Scanner on Ubuntu as a native app

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/system-scanner"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "========================================"
echo "  Installing System Scanner"
echo "========================================"

# Step 1: Ensure PyInstaller is available and Build the app
echo "[1/3] Building the application..."
if [ ! -f "$SCRIPT_DIR/build.sh" ]; then
    echo "[!] Error: build.sh not found!"
    exit 1
fi
chmod +x "$SCRIPT_DIR/build.sh"
bash "$SCRIPT_DIR/build.sh"

# Step 2: Copy to local share
echo "[2/3] Copying files to $INSTALL_DIR..."
# Clean old installation if it exists
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/dist/system-scanner/"* "$INSTALL_DIR/"

# Ensure the executable has execute permissions
chmod +x "$INSTALL_DIR/system-scanner"

# Step 3: Create Desktop Entry
echo "[3/3] Creating desktop entry..."
mkdir -p "$DESKTOP_DIR"

cat << EOF > "$DESKTOP_DIR/system-scanner.desktop"
[Desktop Entry]
Name=System Scanner
Comment=Network Utility & Scanner
Exec=$INSTALL_DIR/system-scanner
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=Network;Security;Utility;
EOF

chmod +x "$DESKTOP_DIR/system-scanner.desktop"

# Refresh the desktop application list
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" || true
fi

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "  You can now launch 'System Scanner' directly from your Ubuntu app menu."
echo "========================================"
