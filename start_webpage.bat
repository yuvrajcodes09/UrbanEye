@echo off
title Launching UrbanEye Dashboard
echo ========================================================
echo Starting UrbanEye Smart Road Monitoring Web Platform...
echo ========================================================

cd /d "C:\Users\Krishna Verma\.gemini\antigravity\scratch\Gaddhamukt"

echo Starting FastAPI Backend on Port 8000...
start "UrbanEye Backend API (Port 8000)" /min python -m uvicorn src.backend.app:app --host 127.0.0.1 --port 8000

echo Starting GIS Dashboard on Port 3000...
start "UrbanEye Dashboard Server (Port 3000)" /min python -m http.server 3000 --directory src/dashboard

timeout /t 2 >nul

echo Opening Dashboard in your default browser...
start http://127.0.0.1:3000

echo.
echo ========================================================
echo UrbanEye Dashboard is now running!
echo - Web Dashboard: http://127.0.0.1:3000
echo - Swagger API:   http://127.0.0.1:8000/docs
echo ========================================================
echo Keep this window open. Press any key when you want to stop the servers.
pause >nul

echo Stopping servers...
taskkill /fi "WINDOWTITLE eq UrbanEye Backend API (Port 8000)*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq UrbanEye Dashboard Server (Port 3000)*" /f >nul 2>&1
echo Done.
