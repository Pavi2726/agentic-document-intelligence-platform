from mcp_server import get_weather

query_city = "Mumbai"

response = get_weather(query_city)

print("MCP Client Response:", response)