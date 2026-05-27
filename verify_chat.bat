@echo off
echo ========================================
echo CHAT VERIFICATION TEST
echo ========================================
echo.

cd backend
call venv\Scripts\activate.bat

echo Running comprehensive test...
echo.
python test_comprehensive.py

echo.
echo ========================================
echo.
echo If all tests passed, your chat is ready!
echo.
echo To use it:
echo 1. Start backend: run.bat
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Open: http://localhost:3000/chat
echo.
echo Try asking:
echo - "What is in the uploaded documents?" (document question)
echo - "What is the capital of France?" (general question)
echo.
echo ========================================
pause
