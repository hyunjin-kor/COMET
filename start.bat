@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

if exist "dist-electron\win-unpacked\CatPrice.exe" (
    start "" "dist-electron\win-unpacked\CatPrice.exe"
    exit /b 0
)

:: Find Python 3.11 / 3.12
set "PYTHON_EXE="
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    goto python_found
)
if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    goto python_found
)
where python >nul 2>&1
if %errorlevel% equ 0 ( set "PYTHON_EXE=python" & goto python_found )

echo [ERROR] Python not found. Install Python 3.11+ from https://python.org
pause
exit /b 1

:python_found

:: Fast path: everything already installed - launch silently, no window
if exist "node_modules\electron\dist\electron.exe" (
  if exist "frontend\dist\index.html" (
    call :ensure_backend
    set "NODE_ENV=production"
    set "CATPRICE_PYTHON=%PYTHON_EXE%"
    start "" "node_modules\electron\dist\electron.exe" .
    exit
  )
)

:: First-time setup (only runs once)
title CatPrice Setup
color 0B
echo.
echo   ==========================================
echo     CatPrice - First-time Setup
echo   ==========================================
echo.

"%PYTHON_EXE%" -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [1/3] Installing Python packages...
    "%PYTHON_EXE%" -m pip install -q .
    if %errorlevel% neq 0 ( echo   [ERROR] pip install failed & pause & exit /b 1 )
    echo   [1/3] Done.
)

if not exist "node_modules\electron\dist\electron.exe" (
    echo   [2/3] Installing Node packages (about 1 min)...
    call npm install --silent
    echo   [2/3] Done.
)

if not exist "frontend\node_modules" (
    echo   [3/3] Installing frontend packages...
    cd frontend & call npm install --silent & cd ..
    echo   [3/3] Done.
)

if not exist "frontend\dist\index.html" (
    echo   Building frontend...
    cd frontend & call npm run build & cd ..
    if not exist "frontend\dist\index.html" (
        echo   [ERROR] Frontend build failed
        pause & exit /b 1
    )
    echo   Build complete.
)

echo.
echo   Setup complete! Starting CatPrice...
echo.

call :ensure_backend
set "NODE_ENV=production"
set "CATPRICE_PYTHON=%PYTHON_EXE%"
start "" "node_modules\electron\dist\electron.exe" .
exit

:ensure_backend
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $resp = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/api/health' -TimeoutSec 2; if ($resp.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if %errorlevel% equ 0 goto :eof

powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -WindowStyle Hidden -FilePath '%PYTHON_EXE%' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8765','--log-level','warning' -WorkingDirectory '%CD%'"

for /l %%I in (1,1,20) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $resp = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/api/health' -TimeoutSec 2; if ($resp.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if !errorlevel! equ 0 goto :eof
  >nul timeout /t 1
)
goto :eof
