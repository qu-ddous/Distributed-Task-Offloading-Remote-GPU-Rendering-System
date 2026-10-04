#!/usr/bin/env bash
# Start the Distributed Remote GPU Rendering Server (Linux/macOS)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."
export PYTHONPATH=".:$PYTHONPATH"
echo "[INFO] Starting FastAPI Daemon on 0.0.0.0:8000..."
python -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000
