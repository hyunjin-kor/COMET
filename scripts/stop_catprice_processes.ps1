param(
    [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$processNames = @("CatPrice", "CatPriceBackend")
$stoppedAny = $false

foreach ($name in $processNames) {
    $processes = Get-Process -Name $name -ErrorAction SilentlyContinue
    if (-not $processes) {
        continue
    }

    foreach ($process in $processes) {
        if (-not $Quiet) {
            Write-Host "[CatPrice] Stopping $($process.ProcessName) (PID $($process.Id))"
        }

        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $stoppedAny = $true
    }
}

# Also free port 8765 (sidecar port). A leftover dev `uvicorn` from a
# previous session shows up as `python.exe`, which the loop above won't
# match by process name. Find by listening port instead.
$port = 8765
try {
    $owners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $owners) {
        $owner = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if (-not $owner) { continue }
        if (-not $Quiet) {
            Write-Host "[CatPrice] Releasing port $port from $($owner.ProcessName) (PID $($owner.Id))"
        }
        Stop-Process -Id $owner.Id -Force -ErrorAction SilentlyContinue
        $stoppedAny = $true
    }
} catch {
    if (-not $Quiet) {
        Write-Host "[CatPrice] Could not query port $port owner: $($_.Exception.Message)"
    }
}

if (-not $Quiet) {
    if ($stoppedAny) {
        Write-Host "[CatPrice] Desktop processes stopped."
    } else {
        Write-Host "[CatPrice] No CatPrice desktop processes were running."
    }
}
