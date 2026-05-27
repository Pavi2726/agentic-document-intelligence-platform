@echo off
echo ========================================
echo Checking Port Availability
echo ========================================
echo.

echo Checking port 8000 (Backend)...
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo [X] Port 8000 is IN USE
    echo.
    echo Process using port 8000:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo PID: %%a
        tasklist | findstr %%a
    )
    echo.
    echo To kill this process, run:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo taskkill /PID %%a /F
    )
) else (
    echo [OK] Port 8000 is AVAILABLE
)

echo.
echo Checking port 3000 (Frontend)...
netstat -ano | findstr :3000 > nul
if %errorlevel% equ 0 (
    echo [X] Port 3000 is IN USE
    echo.
    echo Process using port 3000:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo PID: %%a
        tasklist | findstr %%a
    )
    echo.
    echo To kill this process, run:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo taskkill /PID %%a /F
    )
) else (
    echo [OK] Port 3000 is AVAILABLE
)

echo.
echo ========================================
echo.
pause
