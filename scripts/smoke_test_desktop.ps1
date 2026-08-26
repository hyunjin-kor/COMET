param(
    [int]$TimeoutSeconds = 45,
    [switch]$LeaveRunning
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$packagedExe = Join-Path $projectRoot "dist-electron\win-unpacked\COMET.exe"
$logPath = Join-Path $env:APPDATA "COMET\comet-launcher.log"
# Port 8765 must match BACKEND_PORT in electron/main.js (single source of truth).
$healthUrl = "http://127.0.0.1:8765/api/health"
$pricesUrl = "http://127.0.0.1:8765/api/prices"
$calculateUrl = "http://127.0.0.1:8765/api/calculate"

function Wait-ForHttpOk {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                return $response
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    throw "Timed out waiting for $Url"
}

function Assert-ProcessRunning {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $processes = Get-Process -Name $Name -ErrorAction SilentlyContinue
    if (-not $processes) {
        throw "Expected process '$Name' to be running."
    }
    return $processes
}

function Wait-ForMainWindow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [int]$TimeoutSeconds = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $processes = @(Get-Process -Name $Name -ErrorAction SilentlyContinue)
        $count = @($processes | Where-Object { $_.MainWindowHandle -ne 0 }).Count
        if ($count -gt 0) {
            return $count
        }
        Start-Sleep -Milliseconds 500
    }

    return 0
}

function Assert-PortFree {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            throw "A backend is already responding on $Url before the smoke test starts. Stop the external server and rerun the packaged smoke test."
        }
    } catch {
        if ($_.Exception.Message -like "A backend is already responding*") {
            throw
        }
    }
}

Set-Location $projectRoot

if (-not (Test-Path $packagedExe)) {
    throw "Packaged desktop executable not found: $packagedExe"
}

& (Join-Path $PSScriptRoot "stop_comet_processes.ps1") -Quiet
Remove-Item $logPath -ErrorAction SilentlyContinue
Assert-PortFree -Url $healthUrl

Write-Host "[COMET] Launching packaged desktop app..."
Start-Process -FilePath $packagedExe | Out-Null

$health = Wait-ForHttpOk -Url $healthUrl -TimeoutSeconds $TimeoutSeconds
$healthData = $health.Content | ConvertFrom-Json

$processes = @(Assert-ProcessRunning -Name "COMET")
$windowCount = Wait-ForMainWindow -Name "COMET"

Write-Host "[COMET] Re-launching app to verify single-instance recovery..."
Start-Process -FilePath $packagedExe | Out-Null
Start-Sleep -Seconds 3

$pricesResponse = Wait-ForHttpOk -Url $pricesUrl -TimeoutSeconds 10

$payload = @{
    components = @(
        @{ role = "active_metal"; name = "Ni"; wt_pct = 20; price_per_lb = 7.46 },
        @{ role = "support"; name = "Al2O3"; wt_pct = 80; price_per_lb = 1.10 }
    )
    steps = @("mixer_slurry", "incipient_wetness", "reactor_simple")
    order_size_tons = 20
} | ConvertTo-Json -Depth 6

$calcResponse = Invoke-WebRequest `
    -Uri $calculateUrl `
    -Method Post `
    -UseBasicParsing `
    -TimeoutSec 15 `
    -ContentType "application/json" `
    -Body $payload

$calcData = $calcResponse.Content | ConvertFrom-Json

if (-not (Test-Path $logPath)) {
    throw "Launcher log not found: $logPath"
}

$logTail = Get-Content $logPath | Select-Object -Last 20
$packagedBackendStart = $logTail | Where-Object { $_ -match "Starting packaged backend sidecar" }
$reusedBackend = $logTail | Where-Object { $_ -match "Reusing existing backend server" }
if (-not $packagedBackendStart -and $reusedBackend) {
    throw "Smoke test reused an existing backend instead of launching the packaged sidecar."
}
$relaunchLogged = $logTail | Where-Object { $_ -match "Received second-instance event|Showing main window \(second-instance\)|Showing splash window for second-instance" }
if (-not $relaunchLogged) {
    throw "Second-instance recovery was not recorded in the launcher log."
}

[pscustomobject]@{
    Status = "ok"
    Version = $healthData.version
    MainWindowCount = $windowCount
    PricesStatus = $pricesResponse.StatusCode
    CalculateStatus = $calcResponse.StatusCode
    EstimatedPricePerKg = $calcData.summary.estimated_price_per_kg
    LauncherLog = $logPath
} | Format-List

if (-not $LeaveRunning) {
    & (Join-Path $PSScriptRoot "stop_comet_processes.ps1") -Quiet
}
