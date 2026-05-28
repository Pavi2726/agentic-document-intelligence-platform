import json

feedback = {
    "query": "What is the leave policy?",
    "response": "Employees receive annual leave.",
    "rating": "helpful"
}

# Load existing feedback
with open("feedback_data.json", "r") as f:
    data = json.load(f)

# Add new feedback
data.append(feedback)

# Simulate learning/ranking improvement
helpful_count = sum(
    1 for item in data if item["rating"] == "helpful"
)

print("Helpful feedback count:", helpful_count)

# Save updated feedback
with open("feedback_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("Feedback stored successfully.")