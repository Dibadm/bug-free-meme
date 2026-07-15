@echo off
chcp 65001 >nul
echo ========================================
echo   Habesha Bet V2 - Telegram Bot
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo Starting Telegram bot...
cd /d "%~dp0"
python -m app.bot.runner

pause
