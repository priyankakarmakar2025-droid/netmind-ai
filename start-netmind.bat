@echo off
echo ========================================================
echo Starting NetMind AI Servers (Backend + Frontend)
echo ========================================================
echo.

start "NetMind AI - Backend (FastAPI)" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"
timeout /t 2 >nul
start "NetMind AI - Frontend (React Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo Servers are launching:
echo   - Backend API: http://127.0.0.1:8000/docs
echo   - Frontend:    http://localhost:5173
echo ========================================================
pause
