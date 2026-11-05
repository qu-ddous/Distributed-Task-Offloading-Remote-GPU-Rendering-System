@echo off
:: Elevated Firewall Fix for Direct Ethernet Cable / LAN Connection
title GPU Render Studio - Ethernet Firewall Configuration
echo ====================================================================
echo   Configuring Windows Firewall for Direct Ethernet Cable & LAN
echo ====================================================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Administrator privileges required. Requesting UAC elevation...
    powershell -Command "Start-Process '%~dp0fix_ethernet_firewall.bat' -Verb RunAs"
    exit /b 0
)

echo [1/5] Terminating any stuck server processes to allow update...
taskkill /F /IM GPUWorkerServer.exe >nul 2>&1

echo [2/5] Removing conflicting block rules...
netsh advfirewall firewall delete rule name="gpuworkerserver.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="gpu_server_studio" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_UDP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_ICMP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_Port8000" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_Port8002" >nul 2>&1
netsh advfirewall firewall delete rule name="GPU Render Studio Server (Port 8000)" >nul 2>&1

echo [3/5] Allowing TCP Port 8000 on ALL profiles (Public, Private, Domain)...
netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1

echo [4/5] Allowing UDP Port 8002 for Auto-Discovery on ALL profiles...
netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport=8002 profile=any >nul 2>&1

echo [5/5] Allowing ICMPv4 (Ping) on Ethernet cable...
netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any >nul 2>&1

echo.
echo ====================================================================
echo [SUCCESS] Windows Firewall is now fully configured for Ethernet cable!
echo Inbound connections from direct Ethernet wire (Public Profile) allowed.
echo ====================================================================
echo.
pause
