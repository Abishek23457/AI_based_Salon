@echo off
echo ========================================
echo   🎙️  BookSmart AI - Voice Chat
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [❌ ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check required packages
echo [1/4] Checking Python packages...
python -c "import pyaudio" 2>nul
if errorlevel 1 (
    echo [⚠️] Installing required packages (pyaudio, google-genai)...
    pip install pyaudio google-genai -q
)

REM Check audio devices
echo [2/4] Checking audio devices...
python -c "import pyaudio; p = pyaudio.PyAudio(); print('✅ Audio system OK'); p.terminate()" 2>nul
if errorlevel 1 (
    echo [❌ ERROR] No audio devices found!
    echo Please connect microphone and speakers.
    pause
    exit /b 1
)

REM Check API key
echo [3/4] Checking API key...
python -c "from config import settings; exit(0 if settings.GEMINI_API_KEY else 1)" 2>nul
if errorlevel 1 (
    echo [❌ ERROR] GEMINI_API_KEY not found in .env!
    echo.
    echo Please add your API key to .env file:
    echo   GEMINI_API_KEY=your_key_here
    echo.
    echo Get your key from: https://makersuite.google.com/app/apikey
    pause
    exit /b 1
)

echo [4/4] Starting Voice Chat Agent...
echo.
echo ========================================
echo   🎙️  SPEAK WITH AI AGENT LIVE
echo ========================================
echo.
echo Instructions:
echo   • Speak naturally when you see '🎤 LIVE'
echo   • The AI will respond with voice
echo   • Press Ctrl+C to end the call
echo.

python voice_chat_agent.py

echo.
echo [Voice session ended]
pause
