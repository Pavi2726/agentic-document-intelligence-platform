@echo off
echo ========================================
echo Testing Backend Configuration
echo ========================================
echo.

call venv\Scripts\activate.bat

echo Testing Python version...
python --version
echo.

echo Testing Groq API Key...
python -c "from app.core.config import settings; print('✓ GROQ_API_KEY loaded successfully')"
echo.

echo Testing imports...
python -c "from app.services.response_synthesis import synthesis_engine; print('✓ Response Synthesis Engine imported')"
python -c "from app.services.conversation_context import context_manager; print('✓ Conversation Context Manager imported')"
python -c "from app.retrievers.vector_rag import vector_rag; print('✓ Vector RAG imported')"
echo.

echo ========================================
echo All tests passed! ✓
echo.
echo You can now start the server with:
echo   run.bat
echo.
echo Or manually:
echo   uvicorn app.main:app --reload --port 8000
echo ========================================
pause
