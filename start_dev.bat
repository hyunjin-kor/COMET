@echo off
title CatPrice - Dev Mode
color 0A
cd /d "%~dp0"

echo.
echo   CatPrice - Development Mode
echo.

set "PYTHON_EXE="
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo   Installing Python packages...
    "%PYTHON_EXE%" -m pip install -q .
)

if not exist "frontend\node_modules" (
    cd frontend & call npm install --silent & cd ..
)
if not exist "node_modules\electron\dist\electron.exe" (
    call npm install --silent
)

echo   Starting backend (port 8765)...
start "CatPrice Backend" /min cmd /c "cd /d %~dp0 && "%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload"

echo   Starting frontend dev server (port 5173)...
start "CatPrice Frontend" /min cmd /c "cd /d %~dp0\frontend && set VITE_BACKEND_PORT=8765 && npm run dev"

echo   Waiting for services (8s)...
timeout /t 8 /nobreak >nul

echo   Launching Electron...
set "NODE_ENV=development"
set "CATPRICE_PYTHON=%PYTHON_EXE%"
start "" "node_modules\electron\dist\electron.exe" .
exit
