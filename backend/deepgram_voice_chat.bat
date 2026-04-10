@echo off
echo ========================================
echo   🎙️  Deepgram Voice Chat Agent
echo ========================================
echo.

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo [❌ ERROR] Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if deepgram_voice_chat.py exists
if not exist deepgram_voice_chat.py (
    echo [❌ ERROR] deepgram_voice_chat.py not found!
    echo Please run setup first: setup_deepgram.bat
    pause
    exit /b 1
)

REM Check API Key
echo [1/4] Checking Deepgram API Key...
py -c "from config import settings; exit(0 if settings.DEEPGRAM_API_KEY else 1)" 2>nul
if errorlevel 1 (
    echo [❌ ERROR] DEEPGRAM_API_KEY not found!
    echo.
    echo Please add your API key to .env file:
    echo   DEEPGRAM_API_KEY=your_key_here
    echo.
    echo Get your key: https://console.deepgram.com/signup
    echo.
    pause
    exit /b 1
)
echo [✅ API Key found]

REM Check audio
echo [2/4] Checking audio devices...
py -c "import pyaudio; p = pyaudio.PyAudio(); inp = sum(1 for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0); out = sum(1 for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxOutputChannels'] > 0); print(f'[✅ Microphones: {inp}, Speakers: {out}]'); p.terminate()" 2>nul
if errorlevel 1 (
    echo [⚠️] Warning: Could not verify audio devices
    echo Make sure microphone and speakers are connected
)

REM Check dependencies
echo [3/4] Checking dependencies...
py -c "import deepgram, pyaudio, websockets" 2>nul
if errorlevel 1 (
    echo [⚠️] Installing missing dependencies...
    py -m pip install deepgram-sdk pyaudio websockets aiohttp -q
)
echo [✅ Dependencies OK]

REM Start voice chat
echo [4/4] Starting Deepgram Voice Chat...
echo.
echo ========================================
echo.
echo 🎙️  Press ENTER when ready to speak
echo 🛑  Press Ctrl+C to exit
echo.
echo ========================================
echo.

py deepgram_voice_chat.py

echo.
echo [Voice chat ended]
pause
