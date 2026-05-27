@echo off
echo Testing backend startup...
echo.

cd /d "%~dp0backend"

call venv\Scripts\activate.bat

echo Starting server for 10 seconds...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1

timeout /t 5 /nobreak > nul

echo Testing health endpoint...
curl http://localhost:8000/api/health

echo.
echo.
echo If you see JSON response above, the server works!
echo.
echo Now start the server properly using backend\start_server.bat
echo.

taskkill /F /IM python.exe > nul 2>&1

pause
