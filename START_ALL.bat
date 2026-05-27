@echo off
echo ========================================
echo Agentic Document Intelligence Platform
echo Starting Backend and Frontend...
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Backend Server in new window...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server in new window...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two new windows have opened:
echo   1. Backend Server (Python/FastAPI)
echo   2. Frontend Server (React/Vite)
echo.
echo Wait a few seconds, then open:
echo   http://localhost:3000
echo.
echo To stop: Close both terminal windows
echo ========================================
echo.

pause
