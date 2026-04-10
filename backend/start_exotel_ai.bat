@echo off
chcp 65001 >nul
echo ================================================
echo   Exotel AI Calling - Quick Start
echo ================================================
echo.

REM Check if running from correct directory
if not exist "main.py" (
    echo ERROR: Please run this script from the backend directory
    echo Current: %CD%
    pause
    exit /b 1
)

echo [1/3] Starting BookSmart AI Backend...
echo        URL: http://localhost:8000
echo        API Docs: http://localhost:8000/docs
start "BookSmart AI Backend" cmd /k "python main.py"

timeout /t 5 >nul

echo.
echo [2/3] Starting Ngrok Tunnel...
echo        This creates a public URL for Exotel webhooks
start "Ngrok Tunnel" cmd /k "ngrok http 8000"

timeout /t 3 >nul

echo.
echo ================================================
echo [3/3] Setup Instructions:
echo ================================================
echo.
echo 1. WAIT for both windows to fully start
echo.
echo 2. In the Ngrok window, copy the HTTPS URL
echo    Example: https://abc123.ngrok.io
echo.
echo 3. Go to Exotel Dashboard:
echo    https://my.exotel.com/
echo.
echo 4. Navigate to: Numbers ^> Your Exophone ^> Edit
echo.
echo 5. Configure these URLs (replace with your ngrok URL):
echo.
echo    Call Request URL:
echo    https://YOUR-NGROK.ngrok.io/exotel/incoming
echo.
echo    Status Callback URL:
echo    https://YOUR-NGROK.ngrok.io/exotel/status
echo.
echo    Recording URL:
echo    https://YOUR-NGROK.ngrok.io/exotel/recording
echo.
echo 6. Click SAVE
echo.
echo 7. Call your Exotel number: %EXOTEL_PHONE_NUMBER%
echo    The AI will answer and take your booking!
echo.
echo ================================================
echo.
echo Press any key to open Exotel Dashboard...
pause >nul
start https://my.exotel.com/
