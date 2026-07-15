@echo off
chcp 65001 >nul
echo ========================================
echo   Habesha Bet V2 - Backend Server
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo       Install Python 3.12+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv\" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

echo [2/3] Installing dependencies...
venv\Scripts\pip install -e ".[dev]" --quiet

echo [3/3] Starting backend server...
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
