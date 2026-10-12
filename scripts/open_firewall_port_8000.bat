@echo off
:: Self-elevate to Administrator if not already elevated
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Administrator privileges to configure Windows Firewall...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo =========================================================================
echo    GPU WORKER SERVER - WINDOWS DEFENDER FIREWALL CONFIGURATION
echo =========================================================================
echo.
echo Opening Inbound TCP Port 8000 on Domain, Private, and Public profiles...
echo.

:: Remove existing rule if any to prevent duplicates
netsh advfirewall firewall delete rule name="GPU Worker Server Port 8000" >nul 2>&1

:: Add firewall rule allowing incoming TCP traffic on port 8000
netsh advfirewall firewall add rule name="GPU Worker Server Port 8000" dir=in action=allow protocol=TCP localport=8000 profile=any

if %errorlevel% EQU 0 (
    echo.
    echo =========================================================================
    echo [SUCCESS] Port 8000 is now OPEN in Windows Defender Firewall!
    echo =========================================================================
    echo Client machines can now connect via Cat6 Ethernet cable or Wi-Fi.
    echo You can now close this window and launch GPUWorkerServer.exe.
    echo =========================================================================
) else (
    echo.
    echo [ERROR] Failed to add Windows Firewall rule. Please run this script as Administrator.
)

echo.
pause
