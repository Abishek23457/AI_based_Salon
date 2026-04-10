@echo off
echo Starting Ngrok for BookSmart AI Frontend...
echo.
echo This will expose your React frontend (port 3000) to the internet
echo.
echo After starting, you'll get a public URL like:
echo https://random-string.ngrok.io
echo.
echo Make sure your frontend server is running on port 3000 first!
echo.
echo Press Ctrl+C to stop ngrok
echo.

ngrok http 3000

pause
