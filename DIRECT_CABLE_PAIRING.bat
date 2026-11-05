@echo off
setlocal enabledelayedexpansion
title DIRECT PC-TO-PC CABLE NETWORK CONFIGURATOR
:: Ensure running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~dpnx0\"' -Verb RunAs"
    exit /b
)

cls
echo =====================================================================
echo       DIRECT ETHERNET CABLE (PC-TO-PC) PAIRING CONFIGURATOR
echo =====================================================================
echo.
echo   This tool configures an instant, 100%% guaranteed direct cable
echo   connection between your Server PC (GPU) and Client Laptop.
echo   No router or internet needed!
echo.
echo   [1] CONFIGURE AS SERVER PC (GPU Worker)
echo       - Sets Static IP: 192.168.99.1
echo       - Unblocks Windows Defender Firewall on all profiles
echo.
echo   [2] CONFIGURE AS CLIENT LAPTOP
echo       - Sets Static IP: 192.168.99.2
echo.
echo   [3] RESET TO AUTOMATIC (DHCP / Default Windows APIPA)
echo.
echo   [4] Exit
echo.
set /p choice="Enter choice (1, 2, 3, or 4): "

if "%choice%"=="1" goto SET_SERVER
if "%choice%"=="2" goto SET_CLIENT
if "%choice%"=="3" goto SET_DHCP
exit /b

:SET_SERVER
echo.
echo Configuring Ethernet adapter as SERVER (192.168.99.1)...
for /f "tokens=4,*" %%A in ('netsh interface show interface ^| findstr "Connected" ^| findstr /i "Ethernet"') do set IFNAME=%%B
if "%IFNAME%"=="" (
    for /f "tokens=4,*" %%A in ('netsh interface show interface ^| findstr /i "Ethernet"') do set IFNAME=%%B
)
if "%IFNAME%"=="" set IFNAME=Ethernet
echo Detected Interface: "%IFNAME%"
netsh interface ip set address name="%IFNAME%" static 192.168.99.1 255.255.255.0 none >nul 2>&1
echo [+] Static IP set: 192.168.99.1 (Subnet: 255.255.255.0)
echo [+] Unblocking Firewall rules...
netsh advfirewall firewall delete rule name="gpuworkerserver.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="GPUWorkerServer_UDP" >nul 2>&1
netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1
netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport=8002 profile=any >nul 2>&1
netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any >nul 2>&1
echo.
echo =====================================================================
echo  SERVER READY! Run GPUWorkerServer.exe.
echo  Client PC should connect to: 192.168.99.1:8000
echo =====================================================================
echo.
pause
exit /b

:SET_CLIENT
echo.
echo Configuring Ethernet adapter as CLIENT (192.168.99.2)...
for /f "tokens=4,*" %%A in ('netsh interface show interface ^| findstr "Connected" ^| findstr /i "Ethernet"') do set IFNAME=%%B
if "%IFNAME%"=="" (
    for /f "tokens=4,*" %%A in ('netsh interface show interface ^| findstr /i "Ethernet"') do set IFNAME=%%B
)
if "%IFNAME%"=="" set IFNAME=Ethernet
echo Detected Interface: "%IFNAME%"
netsh interface ip set address name="%IFNAME%" static 192.168.99.2 255.255.255.0 none >nul 2>&1
echo [+] Static IP set: 192.168.99.2 (Subnet: 255.255.255.0)
echo.
echo =====================================================================
echo  CLIENT READY! Open GPURenderStudio.exe.
echo  Set Worker IP to: 192.168.99.1 and Port: 8000
echo =====================================================================
echo.
pause
exit /b

:SET_DHCP
echo.
echo Resetting Ethernet adapter to Automatic (DHCP)...
for /f "tokens=4,*" %%A in ('netsh interface show interface ^| findstr /i "Ethernet"') do set IFNAME=%%B
if "%IFNAME%"=="" set IFNAME=Ethernet
netsh interface ip set address name="%IFNAME%" dhcp >nul 2>&1
echo [+] Interface reset to Automatic DHCP.
echo.
pause
exit /b

