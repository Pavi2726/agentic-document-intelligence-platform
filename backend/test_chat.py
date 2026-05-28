import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.response_synthesis import synthesis_engine
from app.retrievers.vector_rag import vector_rag

print("=" * 50)
print("Testing Chat Functionality")
print("=" * 50)

# Test 1: Check Groq client
print("\n1. Testing Groq Client...")
if synthesis_engine.client:
    print("   ✓ Groq client initialized successfully")
else:
    print("   ✗ Groq client NOT initialized")
    sys.exit(1)

# Test 2: Test simple synthesis
print("\n2. Testing Response Synthesis...")
try:
    response = synthesis_engine.synthesize(
        query="Hello, how are you?",
        vector_results=[],
        graph_results=[],
        sql_results=[]
    )
    print(f"   ✓ Response received: {response['answer'][:100]}...")
except Exception as e:
    print(f"   ✗ Synthesis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test with vector results
print("\n3. Testing with Vector Search...")
try:
    vector_results = vector_rag.search("test query", top_k=3)
    print(f"   ✓ Vector search returned {len(vector_results)} results")
except Exception as e:
    print(f"   ⚠ Vector search failed (this is OK if no documents uploaded): {e}")

print("\n" + "=" * 50)
print("All tests passed! Chat should be working.")
print("=" * 50)
