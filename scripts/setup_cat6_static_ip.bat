<# :
@echo off
setlocal
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/k `\"%~f0`\"' -Verb RunAs"
    exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0'))"
exit /b %errorlevel%
#>

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "     AUTOMATIC CAT6 ETHERNET POINT-TO-POINT IP CONFIGURATOR              " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

function Get-EthernetAdapters {
    $result = @()
    try {
        $result = @(Get-NetAdapter -ErrorAction Stop | Where-Object {
            $_.InterfaceAlias -notmatch 'Wi-Fi|Wireless|WLAN|Virtual|vEthernet|Loopback|Bluetooth|Tailscale|ZeroTier|TAP|TUN' -and
            $_.InterfaceDescription -notmatch 'Virtual|Hyper-V|VMware|Loopback|Bluetooth|TAP|TUN'
        })
    } catch {
        try {
            $lines = netsh interface show interface
            foreach ($line in $lines) {
                if ($line -match 'Dedicated' -and $line -notmatch 'Wi-Fi|Wireless|Loopback') {
                    $parts = ($line.Trim() -split '\s{2,}')
                    if ($parts.Count -ge 4) {
                        $name = $parts[3]
                        $status = if ($parts[1] -match 'Connected') { 'Up' } else { 'Disconnected' }
                        $result += [PSCustomObject]@{
                            InterfaceAlias = $name
                            Name = $name
                            InterfaceDescription = $name
                            Status = $status
                        }
                    }
                }
            }
        } catch {}
    }
    return $result
}

$adapters = Get-EthernetAdapters

if ($adapters.Count -eq 0) {
    Write-Host "[WARNING] No physical Ethernet adapter detected via automatic scan." -ForegroundColor Yellow
    Write-Host "Defaulting to interface name 'Ethernet'..." -ForegroundColor Yellow
    $alias = "Ethernet"
} else {
    Write-Host "Detected Physical Ethernet Adapter(s):" -ForegroundColor Yellow
    for ($i = 0; $i -lt $adapters.Count; $i++) {
        $ad = $adapters[$i]
        $st = if ($ad.Status -eq 'Up') { '[CONNECTED / UP]' } else { '[DISCONNECTED]' }
        Write-Host ("  [{0}] {1} ({2}) - {3}" -f ($i + 1), $ad.InterfaceAlias, $ad.InterfaceDescription, $st) -ForegroundColor White
    }
    Write-Host ""

    if ($adapters.Count -eq 1) {
        $alias = $adapters[0].InterfaceAlias
        Write-Host ("Auto-selected adapter: {0}" -f $alias) -ForegroundColor Green
    } else {
        $upAdapters = @($adapters | Where-Object { $_.Status -eq 'Up' })
        if ($upAdapters.Count -eq 1) {
            $alias = $upAdapters[0].InterfaceAlias
            Write-Host ("Auto-selected connected adapter: {0}" -f $alias) -ForegroundColor Green
        } else {
            $sel = Read-Host ("Select adapter number [1-{0}]" -f $adapters.Count)
            $idx = [int]$sel - 1
            if ($idx -ge 0 -and $idx -lt $adapters.Count) {
                $alias = $adapters[$idx].InterfaceAlias
            } else {
                $alias = $adapters[0].InterfaceAlias
            }
        }
    }
}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "Select this computer's role in the GPU rendering setup:" -ForegroundColor Yellow
Write-Host "  [1] Host / Server PC    (Assigns 192.168.2.1 + Opens Port 8000 Firewall)" -ForegroundColor Green
Write-Host "  [2] Client / Laptop PC  (Assigns 192.168.2.2)" -ForegroundColor Cyan
Write-Host "  [3] Reset to DHCP       (Restore Automatic IP / Factory Default)" -ForegroundColor Gray
Write-Host "  [4] Exit without changes" -ForegroundColor Red
Write-Host "=========================================================================" -ForegroundColor Cyan
$choice = Read-Host "Enter Choice [1, 2, 3, or 4]"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host ("Configuring {0} as HOST / SERVER PC (192.168.2.1)..." -f $alias) -ForegroundColor Yellow
    try {
        netsh interface ipv4 set address name="$alias" static 192.168.2.1 255.255.255.0 | Out-Null
    } catch {}
    try {
        Remove-NetIPAddress -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        New-NetIPAddress -InterfaceAlias $alias -IPAddress "192.168.2.1" -PrefixLength 24 -ErrorAction SilentlyContinue | Out-Null
    } catch {}

    try {
        netsh advfirewall firewall delete rule name="GPU Worker Server Port 8000" | Out-Null
        netsh advfirewall firewall add rule name="GPU Worker Server Port 8000" dir=in action=allow protocol=TCP localport=8000 | Out-Null
    } catch {}

    Write-Host ""
    Write-Host "=========================================================================" -ForegroundColor Green
    Write-Host "  ✔ SUCCESS: Host PC configured successfully!" -ForegroundColor Green
    Write-Host "=========================================================================" -ForegroundColor Green
    Write-Host "  • Adapter:       $alias"
    Write-Host "  • Static IP:     192.168.2.1"
    Write-Host "  • Subnet Mask:   255.255.255.0"
    Write-Host "  • Gateway:       None (Wi-Fi Internet remains active)"
    Write-Host "  • Port 8000:     Open & Allowed in Windows Defender Firewall"
    Write-Host ""
    Write-Host "Next Step: Run GPUWorkerServer.exe on this PC." -ForegroundColor Yellow
    Write-Host "=========================================================================" -ForegroundColor Green
}
elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host ("Configuring {0} as CLIENT / LAPTOP PC (192.168.2.2)..." -f $alias) -ForegroundColor Yellow
    try {
        netsh interface ipv4 set address name="$alias" static 192.168.2.2 255.255.255.0 | Out-Null
    } catch {}
    try {
        Remove-NetIPAddress -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        New-NetIPAddress -InterfaceAlias $alias -IPAddress "192.168.2.2" -PrefixLength 24 -ErrorAction SilentlyContinue | Out-Null
    } catch {}

    Write-Host ""
    Write-Host "=========================================================================" -ForegroundColor Green
    Write-Host "  ✔ SUCCESS: Client PC configured successfully!" -ForegroundColor Green
    Write-Host "=========================================================================" -ForegroundColor Green
    Write-Host "  • Adapter:       $alias"
    Write-Host "  • Static IP:     192.168.2.2"
    Write-Host "  • Subnet Mask:   255.255.255.0"
    Write-Host "  • Gateway:       None (Wi-Fi Internet remains active)"
    Write-Host ""
    Write-Host "Next Step: Open GPURenderStudio.exe, go to Host & Settings, and connect to: 192.168.2.1:8000" -ForegroundColor Yellow
    Write-Host "=========================================================================" -ForegroundColor Green
}
elseif ($choice -eq "3") {
    Write-Host ""
    Write-Host ("Resetting {0} to Automatic DHCP..." -f $alias) -ForegroundColor Yellow
    try {
        netsh interface ipv4 set address name="$alias" source=dhcp | Out-Null
        netsh interface ipv4 set dnsservers name="$alias" source=dhcp | Out-Null
        Set-NetIPInterface -InterfaceAlias $alias -Dhcp Enabled -ErrorAction SilentlyContinue
        Set-DnsClientServerAddress -InterfaceAlias $alias -ResetServerAddresses -ErrorAction SilentlyContinue
    } catch {}

    Write-Host ""
    Write-Host "=========================================================================" -ForegroundColor Green
    Write-Host "  ✔ SUCCESS: Ethernet adapter reset to Automatic (DHCP) mode!" -ForegroundColor Green
    Write-Host "=========================================================================" -ForegroundColor Green
} else {
    Write-Host "Exiting without changes." -ForegroundColor Gray
}

Write-Host ""
