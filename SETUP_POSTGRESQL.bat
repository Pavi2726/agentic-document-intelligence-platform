@echo off
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         PostgreSQL Setup for Document Intelligence            ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0backend"

:MENU
echo.
echo Please choose an option:
echo.
echo [1] Install PostgreSQL dependencies (Python packages)
echo [2] Create PostgreSQL database
echo [3] Initialize database tables
echo [4] Full setup (all steps)
echo [5] Test PostgreSQL connection
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto INSTALL_DEPS
if "%choice%"=="2" goto CREATE_DB
if "%choice%"=="3" goto INIT_TABLES
if "%choice%"=="4" goto FULL_SETUP
if "%choice%"=="5" goto TEST_CONNECTION
if "%choice%"=="6" goto END
goto MENU

:INSTALL_DEPS
echo.
echo ========================================
echo Installing Python dependencies...
echo ========================================
call venv\Scripts\activate.bat
pip install sqlalchemy==2.0.31 psycopg2-binary==2.9.9
echo.
echo Dependencies installed!
pause
goto MENU

:CREATE_DB
echo.
echo ========================================
echo Creating database...
echo ========================================
echo.
echo Enter PostgreSQL password when prompted.
psql -U postgres -c "CREATE DATABASE document_intelligence;"
echo.
pause
goto MENU

:INIT_TABLES
echo.
echo ========================================
echo Initializing database tables...
echo ========================================
call venv\Scripts\activate.bat
python -c "from app.db.postgres import init_db; init_db(); print('Tables created!')"
echo.
pause
goto MENU

:FULL_SETUP
echo.
echo ========================================
echo Running full setup...
echo ========================================
echo.
echo Step 1: Installing dependencies...
call venv\Scripts\activate.bat
pip install sqlalchemy==2.0.31 psycopg2-binary==2.9.9
echo.
echo Step 2: Creating database...
echo Enter PostgreSQL password when prompted.
psql -U postgres -c "CREATE DATABASE document_intelligence;"
echo.
echo Step 3: Creating tables...
python -c "from app.db.postgres import init_db; init_db(); print('Setup complete!')"
echo.
echo ========================================
echo Full setup complete!
echo ========================================
pause
goto MENU

:TEST_CONNECTION
echo.
echo ========================================
echo Testing PostgreSQL connection...
echo ========================================
call venv\Scripts\activate.bat
python -c "from sqlalchemy import create_engine; from app.core.config import settings; engine = create_engine(settings.POSTGRES_URL); conn = engine.connect(); print('✓ Connection successful!'); conn.close()"
echo.
pause
goto MENU

:END
echo.
echo Goodbye!
exit /b 0
