@echo off
setlocal
cd /d "%~dp0\.."

echo =================================================================
echo   GPU RENDER STUDIO - ONE-CLICK INSTALLATION & SHORTCUT SETUP
echo =================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\setup_installer.ps1"

pause
