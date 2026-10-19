@echo off
:: Batch script to open Port 8000 in Windows Defender Firewall for GPU Render Studio
title GPU Render Studio - Firewall Configuration

echo ====================================================================
echo    GPU Render Studio: Opening Inbound TCP Port 8000 in Firewall
echo ====================================================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required.
    echo Please right-click this file and select 'Run as Administrator'.
    echo.
    pause
    exit /b 1
)

echo Adding Windows Firewall Inbound Rule for TCP Port 8000...
netsh advfirewall firewall delete rule name="GPU Render Studio Server (Port 8000)" >nul 2>&1
netsh advfirewall firewall add rule name="GPU Render Studio Server (Port 8000)" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Port 8000 has been successfully opened in Windows Firewall!
    echo External PCs and wired connections can now reach the GPU Worker Server.
) else (
    echo.
    echo [FAILED] Could not add firewall rule. Please check your antivirus or group policy.
)

echo.
pause
