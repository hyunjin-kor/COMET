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

if (-not $Quiet) {
    if ($stoppedAny) {
        Write-Host "[CatPrice] Desktop processes stopped."
    } else {
        Write-Host "[CatPrice] No CatPrice desktop processes were running."
    }
}
