Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function Resolve-Python {
    if ($env:CATPRICE_PYTHON -and (Test-Path $env:CATPRICE_PYTHON)) {
        return $env:CATPRICE_PYTHON
    }

    $candidates = @(
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python312\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return "python"
}

$python = Resolve-Python

Write-Host "[CatPrice] Using Python: $python"

cmd /c """$python"" -c ""import PyInstaller"" >nul 2>nul"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[CatPrice] Installing PyInstaller..."
    & $python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller"
    }
}

$distPath = "build/backend-sidecar"
$workPath = "build/pyinstaller-work"
$specPath = "build/pyinstaller-spec"
$dataPath = Join-Path $projectRoot "backend\data"
$entryPoint = Join-Path $projectRoot "backend\launcher.py"

Get-Process CatPriceBackend -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

cmd /c "if exist ""$distPath"" rd /s /q ""$distPath"""
cmd /c "if exist ""$workPath"" rd /s /q ""$workPath"""
cmd /c "if exist ""$specPath"" rd /s /q ""$specPath"""

Write-Host "[CatPrice] Building backend sidecar..."

& $python -m PyInstaller `
    --noconfirm `
    --onedir `
    --name CatPriceBackend `
    --paths . `
    --distpath $distPath `
    --workpath $workPath `
    --specpath $specPath `
    --collect-submodules backend `
    --collect-submodules uvicorn `
    --collect-submodules apscheduler `
    --collect-submodules sqlmodel `
    --collect-submodules sqlalchemy `
    --collect-submodules pydantic `
    --collect-submodules pydantic_settings `
    --collect-submodules httpx `
    --collect-submodules numpy `
    --add-data "$dataPath;backend/data" `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller backend bundle failed"
}

Write-Host "[CatPrice] Backend sidecar ready at $distPath\CatPriceBackend"
