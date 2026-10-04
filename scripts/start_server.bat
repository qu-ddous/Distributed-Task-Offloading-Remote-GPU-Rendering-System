@echo off
REM Start the Distributed Remote GPU Rendering Server
cd /d "%~dp0\..\server"
set PYTHONPATH=..;%PYTHONPATH%
echo [INFO] Starting FastAPI Daemon on 0.0.0.0:8000...
python -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000
pause
