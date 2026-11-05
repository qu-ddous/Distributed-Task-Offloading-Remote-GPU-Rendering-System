@echo off
title GPU Render Studio - Automatic Windows Firewall Fix
color 0b
echo ====================================================================
echo   GPU RENDER STUDIO - ONE-CLICK WINDOWS FIREWALL FIX
echo ====================================================================
echo.

:: Check for Administrator elevation and auto-elevate
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Administrator rights required to update firewall.
    echo Prompting for Windows UAC permission...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

echo [1/4] Removing conflicting Windows Defender block rules...
netsh advfirewall firewall delete rule name="gpuworkerserver.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="gpurenderstudio.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer" >nul 2>&1
netsh advfirewall firewall delete rule name="GPURenderStudio" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_UDP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_ICMP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPU Render Studio Server (Port 8000)" >nul 2>&1
netsh advfirewall firewall delete rule name="GPU Worker Server Port 8000" >nul 2>&1

echo [2/4] Allowing TCP Port 8000 on ALL profiles (Public, Private, Domain)...
netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1

echo [3/4] Allowing UDP Port 8002 for Auto-Discovery on ALL profiles...
netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport=8002 profile=any >nul 2>&1

echo [4/4] Allowing ICMPv4 (Ping) on direct Ethernet cable and LAN...
netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any >nul 2>&1

echo.
echo ====================================================================
echo [SUCCESS] Windows Firewall is now 100%% unblocked!
echo Both Direct Ethernet Cable (Public Profile) and Wi-Fi LAN are allowed.
echo You can now connect from Client Studio without any firewall block.
echo ====================================================================
echo.
pause

