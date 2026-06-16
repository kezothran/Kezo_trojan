#!/usr/bin/env bash
# ============================================================================
#  System Scanner — build.sh
#  Builds a standalone binary using PyInstaller.
#  Output goes to dist/system-scanner/
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "========================================"
echo "  System Scanner — Build"
echo "========================================"
echo ""

# Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || { echo "[!] Failed to create venv. Make sure python3-venv is installed."; exit 1; }
fi

echo "[INFO] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[INFO] Installing dependencies..."
pip install --upgrade pip
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi
pip install pyinstaller

echo "[1/3] Cleaning previous builds…"
rm -rf "$SCRIPT_DIR/build" "$SCRIPT_DIR/dist" "$SCRIPT_DIR/*.spec"

echo "[2/3] Building with PyInstaller…"
pyinstaller \
    --name "system-scanner" \
    --onedir \
    --windowed \
    --icon "$SCRIPT_DIR/assets/icon.png" \
    --add-data "$SCRIPT_DIR/assets:assets" \
    --add-data "$SCRIPT_DIR/scanner:scanner" \
    --add-data "$SCRIPT_DIR/r.sh:." \
    --add-data "$SCRIPT_DIR/h:h" \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    --noconfirm \
    "$SCRIPT_DIR/app.py"

# Create data dir inside dist
mkdir -p "$SCRIPT_DIR/dist/system-scanner/data"

echo "[3/3] Build complete."
echo ""
echo "========================================"
echo "  Binary output: dist/system-scanner/"
echo "========================================"
echo ""
echo "  Run it with:"
echo "    ./dist/system-scanner/system-scanner"
echo ""
echo "  To create a portable tarball:"
echo "    cd dist && tar czf system-scanner-linux.tar.gz system-scanner/"
echo ""
