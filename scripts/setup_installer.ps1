<#
.SYNOPSIS
    Automated Windows Installer & Setup Script for Distributed GPU Render Studio
.DESCRIPTION
    Checks Python environment, installs dependencies, builds desktop shortcuts,
    and configures the local workstation for client studio and worker daemon.
#>

param(
    [switch]$BuildExe = $false,
    [switch]$CreateShortcuts = $true
)

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   GPU RENDER STUDIO - DESKTOP SETUP & INSTALLATION ASSISTANT   " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

# 1. Verify Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pyVer = python --version
    Write-Host "  -> Found: $pyVer" -ForegroundColor Green
} catch {
    Write-Error "Python 3.11+ is required but was not found in PATH. Please install Python first."
}

# 2. Install Client & Server Dependencies
Write-Host "[2/5] Installing core dependencies..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r client/requirements.txt
python -m pip install --quiet -r server/requirements.txt
Write-Host "  -> Dependencies successfully installed." -ForegroundColor Green

# 3. Setup .env if missing
Write-Host "[3/5] Checking worker configuration (.env)..." -ForegroundColor Yellow
if (-not (Test-Path "$RootDir\server\.env")) {
    Copy-Item "$RootDir\server\.env.example" "$RootDir\server\.env"
    Write-Host "  -> Created server/.env from template." -ForegroundColor Green
} else {
    Write-Host "  -> Existing server/.env found." -ForegroundColor Green
}

# 4. Optional PyInstaller Executable Compilation
if ($BuildExe) {
    Write-Host "[4/5] Compiling standalone Windows executable with PyInstaller..." -ForegroundColor Yellow
    python -m pip install --quiet pyinstaller
    python -m PyInstaller --noconfirm GPURenderStudio.spec
    Write-Host "  -> Executable built at: dist\GPURenderStudio\GPURenderStudio.exe" -ForegroundColor Green
} else {
    Write-Host "[4/5] Skipping standalone binary compilation (use -BuildExe to build .exe)." -ForegroundColor Gray
}

# 5. Create Desktop & Start Menu Shortcuts
if ($CreateShortcuts) {
    Write-Host "[5/5] Generating Desktop Shortcuts..." -ForegroundColor Yellow
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)

    # Client Shortcut
    $ClientShortcut = $WshShell.CreateShortcut("$DesktopPath\GPU Render Studio.lnk")
    $ClientShortcut.TargetPath = "$RootDir\scripts\start_client.bat"
    $ClientShortcut.WorkingDirectory = "$RootDir"
    $ClientShortcut.Description = "Distributed Task Offloading & Remote GPU Rendering Studio"
    if (Test-Path "$RootDir\client\assets\icon.ico") {
        $ClientShortcut.IconLocation = "$RootDir\client\assets\icon.ico"
    }
    $ClientShortcut.Save()

    # Server Shortcut
    $ServerShortcut = $WshShell.CreateShortcut("$DesktopPath\GPU Worker Daemon.lnk")
    $ServerShortcut.TargetPath = "$RootDir\scripts\start_server.bat"
    $ServerShortcut.WorkingDirectory = "$RootDir"
    $ServerShortcut.Description = "Distributed GPU Rendering Server Daemon"
    $ServerShortcut.Save()

    Write-Host "  -> Created 'GPU Render Studio' desktop shortcut." -ForegroundColor Green
    Write-Host "  -> Created 'GPU Worker Daemon' desktop shortcut." -ForegroundColor Green
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION COMPLETE! READY TO LAUNCH.                      " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "To launch Client Studio:  Double-click 'GPU Render Studio' on Desktop"
Write-Host "To start Worker Daemon:   Double-click 'GPU Worker Daemon' on Desktop"
Write-Host "Or execute via terminal:  python client/app.py"
Write-Host ""
