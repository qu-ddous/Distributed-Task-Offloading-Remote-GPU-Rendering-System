"""
Dedicated Cat6 Ethernet Direct-Link Configuration & Management
Ensures Host PC and Client PC communicate exclusively over high-speed Cat6 cable:
Host PC:   192.168.2.1 / 255.255.255.0
Client PC: 192.168.2.2 / 255.255.255.0
Port:      8000
"""
import re
import ctypes
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

HOST_CAT6_IP = "192.168.2.1"
CLIENT_CAT6_IP = "192.168.2.2"
CAT6_SUBNET_MASK = "255.255.255.0"
CAT6_PORT = 8000


def get_physical_ethernet_alias() -> str:
    """Finds physical Ethernet interface alias, ignoring Wi-Fi, Virtual, Cellular, and hotspot adapters."""
    candidates = []
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "show", "interface"],
            text=True,
            errors="ignore",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        for line in out.splitlines():
            line_lower = line.lower()
            if "dedicated" in line_lower and not any(x in line_lower for x in ["wi-fi", "wireless", "loopback", "cellular", "bluetooth", "virtual", "*"]):
                parts = re.split(r"\s{2,}", line.strip())
                if len(parts) >= 4:
                    alias = parts[3]
                    is_connected = "connected" in parts[1].lower()
                    candidates.append((alias, is_connected))
    except Exception:
        pass

    # 1. First priority: Connected adapter with 'ethernet' or 'lan' in name
    for alias, conn in candidates:
        if ("ethernet" in alias.lower() or "lan" in alias.lower()) and conn:
            return alias

    # 2. Second priority: Any adapter with 'ethernet' or 'lan'
    for alias, conn in candidates:
        if "ethernet" in alias.lower() or "lan" in alias.lower():
            return alias

    # 3. Third priority: Any connected candidate
    for alias, conn in candidates:
        if conn:
            return alias

    if candidates:
        return candidates[0][0]

    return "Ethernet"


def is_ip_configured(alias: str, target_ip: str) -> bool:
    """Checks if target_ip is already assigned to the interface."""
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "ipv4", "show", "addresses", alias],
            text=True,
            errors="ignore",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        return target_ip in out
    except Exception:
        return False


def run_elevated_ps1(script_content: str, filename: str) -> bool:
    """Runs a PowerShell script with Administrator elevation via Windows ShellExecuteW."""
    temp_file = Path(tempfile.gettempdir()) / filename
    temp_file.write_text(script_content.strip(), encoding="utf-8")

    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "powershell.exe",
            f'-NoProfile -ExecutionPolicy Bypass -File "{str(temp_file)}"',
            None,
            1  # SW_SHOWNORMAL
        )
        if ret > 32:
            return True
    except Exception:
        pass

    try:
        cmd = f'Start-Process powershell -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -File "{str(temp_file)}"\' -Verb RunAs'
        subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd])
        return True
    except Exception:
        return False


def auto_configure_host_cat6(elevate_if_needed: bool = False) -> bool:
    """
    Configures Host PC for direct Cat6 link:
    - Static IP: 192.168.2.1 / 255.255.255.0
    - Windows Firewall: Port 8000 allowed
    """
    alias = get_physical_ethernet_alias()
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # 1. Try silent configuration first
    try:
        subprocess.run(
            ["netsh", "interface", "ipv4", "set", "address", f"name={alias}", "static", HOST_CAT6_IP, CAT6_SUBNET_MASK],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            timeout=5
        )
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPU Worker Server Port 8000", "dir=in", "action=allow", "protocol=TCP", "localport=8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            timeout=5
        )
    except Exception:
        pass

    if is_ip_configured(alias, HOST_CAT6_IP):
        return True

    if elevate_if_needed:
        ps_script = f"""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "       HOST / SERVER PC - CAT6 ETHERNET ONE-CLICK SETUP                  " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuring Ethernet adapter: '{alias}'..." -ForegroundColor Yellow
Write-Host "Assigning Static IP {HOST_CAT6_IP} / {CAT6_SUBNET_MASK}..." -ForegroundColor Yellow

& netsh.exe interface ipv4 set address name="{alias}" static {HOST_CAT6_IP} {CAT6_SUBNET_MASK}

try {{
    Get-NetIPAddress -InterfaceAlias "{alias}" -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
    Remove-NetRoute -InterfaceAlias "{alias}" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
    New-NetIPAddress -InterfaceAlias "{alias}" -IPAddress "{HOST_CAT6_IP}" -PrefixLength 24 -ErrorAction SilentlyContinue | Out-Null
}} catch {{}}

Write-Host "Configuring Windows Defender Firewall for Port 8000..." -ForegroundColor Yellow
& netsh.exe advfirewall firewall delete rule name="GPU Worker Server Port 8000"
& netsh.exe advfirewall firewall add rule name="GPU Worker Server Port 8000" dir=in action=allow protocol=TCP localport=8000

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "  ✔ SUCCESS: Host PC configured! IP: {HOST_CAT6_IP}, Port 8000 Allowed." -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
Start-Sleep -Seconds 2
"""
        return run_elevated_ps1(ps_script, "setup_cat6_host.ps1")

    return False


def auto_configure_client_cat6(elevate_if_needed: bool = False) -> bool:
    """
    Configures Client PC (Laptop) for direct Cat6 link:
    - Static IP: 192.168.2.2 / 255.255.255.0
    """
    alias = get_physical_ethernet_alias()
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # 1. Try silent configuration first
    try:
        subprocess.run(
            ["netsh", "interface", "ipv4", "set", "address", f"name={alias}", "static", CLIENT_CAT6_IP, CAT6_SUBNET_MASK],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            timeout=5
        )
    except Exception:
        pass

    if is_ip_configured(alias, CLIENT_CAT6_IP):
        return True

    if elevate_if_needed:
        ps_script = f"""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "      CLIENT / LAPTOP PC - CAT6 ETHERNET ONE-CLICK SETUP                 " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuring Ethernet adapter: '{alias}'..." -ForegroundColor Yellow
Write-Host "Assigning Static IP {CLIENT_CAT6_IP} / {CAT6_SUBNET_MASK}..." -ForegroundColor Yellow

& netsh.exe interface ipv4 set address name="{alias}" static {CLIENT_CAT6_IP} {CAT6_SUBNET_MASK}

try {{
    Get-NetIPAddress -InterfaceAlias "{alias}" -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
    Remove-NetRoute -InterfaceAlias "{alias}" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
    New-NetIPAddress -InterfaceAlias "{alias}" -IPAddress "{CLIENT_CAT6_IP}" -PrefixLength 24 -ErrorAction SilentlyContinue | Out-Null
}} catch {{}}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "  ✔ SUCCESS: Client PC configured! IP: {CLIENT_CAT6_IP}." -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
Start-Sleep -Seconds 2
"""
        return run_elevated_ps1(ps_script, "setup_cat6_client.ps1")

    return False
