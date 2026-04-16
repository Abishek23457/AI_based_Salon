@echo off
echo Starting Ngrok for BookSmart AI Backend...
echo.
echo This will expose your FastAPI backend (port 8000) to the internet
echo.
echo After starting, you'll get a public URL like:
echo https://random-string.ngrok.io
echo.
echo You can access:
echo - Swagger UI: https://random-string.ngrok.io/docs
echo - API Root: https://random-string.ngrok.io/
echo.
echo Press Ctrl+C to stop ngrok
echo.

ngrok http 8000

pause
