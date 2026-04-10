@echo off
echo ========================================
echo   Gemini 2.0 Flash Voice Chat
echo ========================================
echo.

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

REM Check API Key
echo [1/3] Checking Gemini API Key...
py -c "from config import settings; exit(0 if settings.GEMINI_API_KEY else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] GEMINI_API_KEY not found in .env!
    echo.
    echo Please add your key to .env file:
    echo   GEMINI_API_KEY=your_key_here
    echo.
    echo Get free API key from: https://makersuite.google.com/app/apikey
    pause
    exit /b 1
)
echo [OK] API Key found

REM Check audio
echo [2/3] Checking audio devices...
py -c "import pyaudio; p = pyaudio.PyAudio(); print('[OK] Audio devices found'); p.terminate()" 2>nul
if errorlevel 1 (
    echo [WARNING] PyAudio issue - checking if install needed...
    py -m pip install pyaudio -q
)

REM Check google-genai
echo [3/3] Checking google-genai...
py -c "import google.genai" 2>nul
if errorlevel 1 (
    echo [Installing google-genai...]
    py -m pip install google-genai -q
)
echo [OK] Ready

echo.
echo ========================================
echo   Starting Gemini Voice Chat...
echo ========================================
echo.
echo Instructions:
echo   - Speak naturally when you see 'LIVE'
echo   - AI responds with voice immediately
echo   - Press Ctrl+C to exit
echo.

py gemini_voice_chat_fixed.py

echo.
echo [Session ended]
pause
