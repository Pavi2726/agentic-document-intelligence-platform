@echo off
echo ========================================
echo Verifying .gitignore Configuration
echo ========================================
echo.

cd /d "%~dp0"

echo Checking if .env file exists...
if exist "backend\.env" (
    echo [OK] backend\.env exists
) else (
    echo [WARNING] backend\.env does not exist
    echo You need to create it from .env.example
)

echo.
echo Checking if .env is in .gitignore...
findstr /C:".env" .gitignore >nul
if %errorlevel% equ 0 (
    echo [OK] .env is in root .gitignore
) else (
    echo [ERROR] .env is NOT in root .gitignore
)

findstr /C:".env" backend\.gitignore >nul
if %errorlevel% equ 0 (
    echo [OK] .env is in backend\.gitignore
) else (
    echo [ERROR] .env is NOT in backend\.gitignore
)

findstr /C:".env" frontend\.gitignore >nul
if %errorlevel% equ 0 (
    echo [OK] .env is in frontend\.gitignore
) else (
    echo [ERROR] .env is NOT in frontend\.gitignore
)

echo.
echo Testing git status (if git is initialized)...
if exist ".git" (
    echo.
    echo Files that will be committed:
    git status --short
    echo.
    echo Checking if .env would be committed...
    git status --short | findstr ".env" >nul
    if %errorlevel% equ 0 (
        echo [ERROR] .env file will be committed! Check .gitignore
    ) else (
        echo [OK] .env file is properly ignored
    )
) else (
    echo [INFO] Git not initialized yet. Run 'git init' first.
)

echo.
echo ========================================
echo Verification Complete
echo ========================================
echo.
echo Summary:
echo - .env should exist in backend/
echo - .env should be in all .gitignore files
echo - .env should NOT appear in 'git status'
echo - .md files (except README.md) will be ignored
echo.
echo Note: Only README.md will be pushed to GitHub.
echo All other .md documentation files are excluded.
echo.
pause
