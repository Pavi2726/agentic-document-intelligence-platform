from app.api.routes import chat, ChatRequest

payload = ChatRequest(message='Hello, can you summarize?', stream=False)
result = chat(payload)
print(result)
