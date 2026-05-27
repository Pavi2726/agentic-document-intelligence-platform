@echo off
echo ========================================
echo Installing PostgreSQL Dependencies
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [2/2] Installing PostgreSQL libraries...
pip install sqlalchemy==2.0.31 psycopg2-binary==2.9.9

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo PostgreSQL dependencies installed!
echo ========================================
echo.
echo Next steps:
echo 1. Install PostgreSQL from: https://www.postgresql.org/download/windows/
echo 2. Create database: document_intelligence
echo 3. Update backend/.env with your PostgreSQL password
echo 4. Run: setup_database.bat
echo.
pause
