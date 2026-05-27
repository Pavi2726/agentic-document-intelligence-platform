@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

echo [2/3] Checking Python version...
python --version
echo.

echo [3/3] Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo Check the error messages above
    pause
)
