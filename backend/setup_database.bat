@echo off
echo ========================================
echo Setting Up PostgreSQL Database
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [2/3] Testing PostgreSQL connection...
python -c "from sqlalchemy import create_engine; from app.core.config import settings; engine = create_engine(settings.POSTGRES_URL); conn = engine.connect(); print('✓ PostgreSQL connection successful!'); conn.close()"

if errorlevel 1 (
    echo.
    echo ERROR: Cannot connect to PostgreSQL
    echo.
    echo Please check:
    echo 1. PostgreSQL is installed and running
    echo 2. Database 'document_intelligence' exists
    echo 3. Password in .env file is correct
    echo.
    echo To create database, run:
    echo   psql -U postgres -c "CREATE DATABASE document_intelligence;"
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Creating database tables...
python -c "from app.db.postgres import init_db; init_db(); print('✓ Database tables created successfully!')"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create tables
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo Tables created:
echo   - document_metadata
echo   - upload_sessions
echo   - retrieval_logs
echo.
echo You can now start the backend server.
echo.
pause
