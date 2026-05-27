@echo off
echo Testing Chat Functionality
echo ========================================

cd backend
call venv\Scripts\activate.bat

echo.
echo Test 1: Checking Groq API Key...
python -c "from app.core.config import settings; print('API Key:', settings.GROQ_API_KEY[:20] + '...')"

echo.
echo Test 2: Testing Groq Client...
python -c "from groq import Groq; from app.core.config import settings; client = Groq(api_key=settings.GROQ_API_KEY); print('Groq Client: OK')"

echo.
echo Test 3: Testing Response Synthesis...
python -c "from app.services.response_synthesis import synthesis_engine; print('Synthesis Engine:', 'OK' if synthesis_engine.client else 'FAILED')"

echo.
echo Test 4: Making a test API call...
python -c "from app.services.response_synthesis import synthesis_engine; result = synthesis_engine.synthesize('Hello', [], [], []); print('Response:', result['answer'][:50] + '...')"

echo.
echo ========================================
echo All tests completed!
pause
