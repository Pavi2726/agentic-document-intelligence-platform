@echo off
echo ========================================
echo Creating PostgreSQL Database
echo ========================================
echo.

echo This script will create the 'document_intelligence' database.
echo.
echo You will be prompted for the PostgreSQL password.
echo Default password is usually 'postgres' or what you set during installation.
echo.
pause

echo.
echo Creating database...
psql -U postgres -c "CREATE DATABASE document_intelligence;"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create database
    echo.
    echo Possible reasons:
    echo 1. PostgreSQL is not installed
    echo 2. psql command not in PATH
    echo 3. Wrong password
    echo 4. Database already exists (this is OK!)
    echo.
    echo To check if database exists:
    echo   psql -U postgres -l
    echo.
) else (
    echo.
    echo ========================================
    echo Database created successfully!
    echo ========================================
    echo.
)

echo.
echo Next step: Run setup_database.bat to create tables
echo.
pause
