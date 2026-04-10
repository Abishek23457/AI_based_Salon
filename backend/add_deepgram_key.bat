@echo off
echo ========================================
echo   🔑 Adding Deepgram API Key
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [Creating .env file...]
    copy .env.example .env >nul 2>&1
    if errorlevel 1 (
        echo [Creating new .env from scratch...]
        echo # BookSmart AI Environment Configuration > .env
    )
)

echo [Adding Deepgram API Key...]

REM Check if key already exists
findstr /C:"DEEPGRAM_API_KEY" .env >nul 2>&1
if errorlevel 1 (
    echo. >> .env
    echo # ─── Deepgram Voice API ───────────────────────────────────────── >> .env
    echo # Get from https://console.deepgram.com/signup >> .env
    echo DEEPGRAM_API_KEY=c44db2a3420dc5108c116be541d85a6a38f5ce70 >> .env
    echo. >> .env
    echo [✅ Deepgram API Key added to .env!]
) else (
    echo [⚠️ DEEPGRAM_API_KEY already exists in .env]
    echo [Updating with new key...]
    
    REM Create temp file with updated key
    for /f "tokens=*" %%a in (.env) do (
        echo %%a | findstr /C:"DEEPGRAM_API_KEY=" >nul 2>&1
        if errorlevel 1 (
            echo %%a >> .env.tmp
        ) else (
            echo DEEPGRAM_API_KEY=c44db2a3420dc5108c116be541d85a6a38f5ce70 >> .env.tmp
        )
    )
    
    REM Replace original file
    del .env >nul 2>&1
    rename .env.tmp .env
    echo [✅ Deepgram API Key updated!]
)

echo.
echo [Verifying key...]
py -c "from config import settings; print(f'✅ Key loaded: {settings.DEEPGRAM_API_KEY[:10]}...') if settings.DEEPGRAM_API_KEY else print('❌ Key not loaded')" 2>nul

echo.
echo ========================================
echo   ✅ Deepgram API Key Configured!
echo ========================================
echo.
echo You can now run voice chat:
echo   deepgram_voice_chat.bat
echo.
pause
