@echo off
title Syndicate Pro Quant Terminal (FastAPI + React)
echo ========================================================
echo   Starting Syndicate Pro Quant Terminal...
echo   Backend: http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo ========================================================

set "PATH=C:\Program Files\nodejs;%PATH%"

start "FastAPI Backend" cmd /k "python -m uvicorn server.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "React Frontend" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0 --port 5173"

echo Terminal launched successfully! Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173
pause
