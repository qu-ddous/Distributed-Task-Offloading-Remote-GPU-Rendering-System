@echo off
REM Launch Client Desktop CustomTkinter Application
cd /d "%~dp0\.."
set PYTHONPATH=.;%PYTHONPATH%
echo [INFO] Launching Client Desktop Application...
python client/app.py
pause
