@echo off
echo ========================================
echo   🎙️  Deepgram Voice Agent Setup
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

echo [1/5] Python found: 
py --version

REM Install dependencies
echo.
echo [2/5] Installing Deepgram SDK and dependencies...
py -m pip install deepgram-sdk websockets pyaudio aiohttp -q
if errorlevel 1 (
    echo [⚠️] Trying alternative installation...
    py -m pip install deepgram-sdk websockets aiohttp
    echo [⚠️] For pyaudio, you may need to:
    echo    1. Install Visual C++ Build Tools
    echo    2. Or download pyaudio wheel from:
    echo       https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
)

echo [3/5] Dependencies installed!

REM Check API Key
echo.
echo [4/5] Checking Deepgram API Key...
py -c "from config import settings; exit(0 if settings.DEEPGRAM_API_KEY else 1)" 2>nul
if errorlevel 1 (
    echo [❌ WARNING] DEEPGRAM_API_KEY not found in .env!
    echo.
    echo Please add your API key:
    echo   1. Go to https://console.deepgram.com/signup
    echo   2. Create a free account
    echo   3. Copy your API key
    echo   4. Add to .env file: DEEPGRAM_API_KEY=your_key_here
    echo.
    echo Create .env file now? (Y/N)
    choice /c YN /n
    if errorlevel 1 (
        echo DEEPGRAM_API_KEY= > .env
        echo [Created .env file - please edit and add your key]
        notepad .env
    )
) else (
    echo [✅ API Key found!]
)

REM Check audio
echo.
echo [5/5] Checking audio devices...
py -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Microphones: {sum(1 for i in range(p.get_device_count()) if p.get_device_info_by_index(i)[\"maxInputChannels\"] > 0)}'); print(f'Speakers: {sum(1 for i in range(p.get_device_count()) if p.get_device_info_by_index(i)[\"maxOutputChannels\"] > 0)}'); p.terminate()" 2>nul
if errorlevel 1 (
    echo [⚠️] Could not check audio devices
)

echo.
echo ========================================
echo   ✅ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Add DEEPGRAM_API_KEY to .env file
if not exist .env (
    echo      (Create .env file with your key)
)
echo   2. Run voice chat: deepgram_voice_chat.bat
echo   3. Or test TTS: py deepgram_voice_chat.py --test-tts
echo.

choice /c YN /n /m "Run voice chat now? (Y/N): "
if errorlevel 1 if not errorlevel 2 (
    echo.
    echo Starting Deepgram Voice Chat...
    py deepgram_voice_chat.py
)

echo.
pause
