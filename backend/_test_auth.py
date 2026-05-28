import requests
resp = requests.post('http://127.0.0.1:8000/api/auth/register', json={'username':'testuser','password':'password123','email':'test@example.com'})
print(resp.status_code, resp.text)
resp2 = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'testuser','password':'password123'})
print(resp2.status_code, resp2.text)
