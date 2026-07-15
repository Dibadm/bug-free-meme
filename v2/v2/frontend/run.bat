@echo off
chcp 65001 >nul
echo ========================================
echo   Habesha Bet V2 - Frontend Dev Server
echo ========================================
echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo       Install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo Installing dependencies...
call npm install --quiet

echo Starting development server...
call npm run dev

pause
