<# :
@echo off
setlocal
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to configure Host Ethernet IP...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/k `\"%~f0`\"' -Verb RunAs"
    exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0'))"
exit /b %errorlevel%
#>

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "       HOST / SERVER PC - CAT6 ETHERNET ONE-CLICK SETUP                  " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

function Get-EthernetAdapters {
    $result = @()
    try {
        $result = @(Get-NetAdapter -ErrorAction Stop | Where-Object {
            $_.InterfaceAlias -notmatch 'Wi-Fi|Wireless|WLAN|Virtual|vEthernet|Loopback|Bluetooth|Tailscale|ZeroTier|TAP|TUN|Cellular' -and
            $_.InterfaceDescription -notmatch 'Virtual|Hyper-V|VMware|Loopback|Bluetooth|TAP|TUN|Cellular'
        })
    } catch {
        try {
            $lines = netsh interface show interface
            foreach ($line in $lines) {
                if ($line -match 'Dedicated' -and $line -notmatch 'Wi-Fi|Wireless|Loopback|Cellular') {
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
    Write-Host "Attempting fallback configuration on interface name 'Ethernet'..." -ForegroundColor Yellow
    $alias = "Ethernet"
} else {
    $target = $adapters | Where-Object { ($_.InterfaceAlias -match 'Ethernet|LAN') -and $_.Status -eq 'Up' } | Select-Object -First 1
    if (-not $target) { $target = $adapters | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1 }
    if (-not $target) { $target = $adapters | Where-Object { $_.InterfaceAlias -match 'Ethernet|LAN' } | Select-Object -First 1 }
    if (-not $target) { $target = $adapters[0] }
    $alias = $target.InterfaceAlias
}

Write-Host "Configuring Ethernet adapter: '$alias'..." -ForegroundColor Yellow

# Configure static IP 192.168.2.1 with mask 255.255.255.0 and NO gateway (keeps Wi-Fi internet active)
try {
    netsh interface ipv4 set address name="$alias" static 192.168.2.1 255.255.255.0 | Out-Null
} catch {}

try {
    Remove-NetIPAddress -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
    Remove-NetRoute -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
    New-NetIPAddress -InterfaceAlias $alias -IPAddress "192.168.2.1" -PrefixLength 24 -ErrorAction SilentlyContinue | Out-Null
} catch {}

# Open Windows Firewall Port 8000
try {
    netsh advfirewall firewall delete rule name="GPU Worker Server Port 8000" | Out-Null
    netsh advfirewall firewall add rule name="GPU Worker Server Port 8000" dir=in action=allow protocol=TCP localport=8000 | Out-Null
} catch {}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "  ✔ SUCCESS: Host PC is configured and ready!" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "  • Adapter:       $alias"
Write-Host "  • Host IP:       192.168.2.1"
Write-Host "  • Subnet Mask:   255.255.255.0"
Write-Host "  • Gateway:       None (Wi-Fi Internet remains active)"
Write-Host "  • Firewall:      Port 8000 is OPEN in Windows Defender Firewall"
Write-Host ""
Write-Host "You can now launch GPUWorkerServer.exe on this PC." -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host ""
