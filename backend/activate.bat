@echo off
echo ========================================
echo Activating Python 3.11 Virtual Environment
echo ========================================
echo.

call venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo Python version:
python --version
echo.
echo To run the backend server:
echo   uvicorn app.main:app --reload --port 8000
echo.
echo To deactivate:
echo   deactivate
echo.
echo ========================================
