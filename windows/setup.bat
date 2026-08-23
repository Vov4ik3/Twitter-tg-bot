@echo off
setlocal
cd /d "%~dp0.."

echo ===================================
echo  Twitter -^> Telegram bot: first-time setup
echo ===================================

REM --- 1. virtual environment ---
if not exist venv\Scripts\python.exe (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create venv. Is Python installed and on PATH?
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists.
)

REM --- 2. dependencies ---
echo [2/4] Installing dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

REM --- 3. .env ---
if not exist .env (
    echo [3/4] No .env found - creating one from .env.example.
    copy .env.example .env >nul
    echo.
    echo   Opening it in Notepad. Fill in BOT_TOKEN, TARGET_CHAT_ID,
    echo   and ALLOWED_USER_IDS, save, close it, then run this
    echo   script again to actually start the bot.
    echo.
    notepad .env
    pause
    exit /b 0
) else (
    echo [3/4] .env found.
)

REM --- 4. ffmpeg ---
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo [4/4] WARNING: ffmpeg not found on PATH.
    echo   Video merging will fail without it.
    echo   Install with: winget install ffmpeg
    echo   ^(then restart this script^)
    pause
) else (
    echo [4/4] ffmpeg found.
)

echo.
echo Setup complete. Starting the bot now...
call "%~dp0run.bat"
