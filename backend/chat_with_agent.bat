@echo off
echo ========================================
echo   BookSmart AI - Terminal Chat Agent
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if backend is running
echo [1/3] Checking backend connection...
curl -s http://localhost:8000/chat/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend is not running!
    echo.
    echo Would you like to:
    echo   1. Start backend first (will open new window)
    echo   2. Exit and start manually
    echo.
    choice /c 12 /n /m "Select option (1 or 2): "
    if errorlevel 2 (
        echo.
        echo To start backend manually:
        echo   python main.py
        echo.
        pause
        exit /b 1
    ) else (
        echo [Starting backend in new window...]
        start "BookSmart Backend" cmd /k "python main.py"
        echo [Waiting for backend to start...]
        timeout /t 5 /nobreak >nul
    )
)

echo [2/3] Backend is running!
echo [3/3] Starting terminal chat agent...
echo.
echo ========================================
echo   Starting Live Chat Session...
echo ========================================
echo.

python terminal_chat_agent.py

echo.
echo [Chat session ended]
pause
