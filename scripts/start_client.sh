#!/usr/bin/env bash
# Launch Client Desktop Application (Linux/macOS)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."
export PYTHONPATH=".:$PYTHONPATH"
echo "[INFO] Launching Client Desktop Application..."
python client/app.py
