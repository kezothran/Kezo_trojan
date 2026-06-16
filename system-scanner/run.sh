#!/usr/bin/env bash
# ============================================================================
#  System Scanner — run.sh
#  Launches the application.
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Use venv Python if available, else system Python
if [ -f "$VENV_DIR/bin/python" ]; then
    exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/app.py" "$@"
else
    exec python3 "$SCRIPT_DIR/app.py" "$@"
fi
