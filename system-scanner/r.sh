#!/bin/bash
# r.sh — build and run the CTF exploit in h/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
H_DIR="$SCRIPT_DIR/h"

if [ ! -d "$H_DIR" ]; then
    echo "[!] h/ directory not found at: $H_DIR"
    exit 1
fi

cd "$H_DIR"
echo "[*] Building in: $H_DIR"

make clean 2>/dev/null || true
make

BIN="$H_DIR/exploit"

if [ ! -x "$BIN" ]; then
    echo "[!] Build failed: exploit binary not found at $BIN"
    exit 1
fi

echo "[*] Running: $BIN"
echo "-----------------------------------"
"$BIN"

echo "-----------------------------------"
echo "[*] Exploit payload delivered. Terminal is now hooked to root shell."
echo "[*] (Do not close this window manually or the kernel may panic!)"
sleep 999999
