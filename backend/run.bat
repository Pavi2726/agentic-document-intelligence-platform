@echo off
echo ========================================
echo Starting Agentic Document Intelligence Platform
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking Python version...
python --version

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn app.main:app --reload --port 8000
