@echo off
:: Batch script to open Port 8000 in Windows Defender Firewall for GPU Render Studio
title GPU Render Studio - Firewall Configuration

echo ====================================================================
echo    GPU Render Studio: Opening Inbound TCP Port 8000 & UDP 8002
echo ====================================================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required.
    echo Please right-click this file and select 'Run as Administrator'.
    echo.
    powershell -Command "Start-Process '%~dp0allow_firewall_port_8000.bat' -Verb RunAs"
    exit /b 0
)

echo Removing conflicting firewall rules...
netsh advfirewall firewall delete rule name="gpuworkerserver.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_UDP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPU Render Studio Server (Port 8000)" >nul 2>&1

echo Adding Windows Firewall Inbound Rules for Port 8000 and 8002 (All Profiles)...
netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1
netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport=8002 profile=any >nul 2>&1
netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any >nul 2>&1

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Port 8000 and 8002 have been successfully opened in Windows Firewall!
    echo External PCs and direct Ethernet wired connections can now reach the GPU Worker Server.
) else (
    echo.
    echo [FAILED] Could not add firewall rule. Please check your antivirus or group policy.
)

echo.
pause
