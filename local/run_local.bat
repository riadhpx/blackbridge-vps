@echo off
setlocal
echo ==============================================
echo   BlackBridge Local Client Starter
echo ==============================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Install Requirements
echo [1/2] Installing dependencies...
pip install -r requirements.txt -q

:: Run Client
echo [2/2] Starting Local Client on port 8001...
echo Open your browser at http://localhost:8001 to configure the tunnel.
python local_client.py

pause
