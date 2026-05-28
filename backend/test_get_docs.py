from app.db.postgres import get_documents

print('Calling get_documents...')
try:
    docs = get_documents()
    print('Returned', len(docs), 'documents')
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Error:', e)
