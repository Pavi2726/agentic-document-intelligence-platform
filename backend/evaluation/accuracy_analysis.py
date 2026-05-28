import json
import pandas as pd

# Load evaluation results
with open("results.json", "r") as f:
    results = json.load(f)

total_queries = len(results)
correct = 0
hallucinations = 0
total_latency = 0

for item in results:

    response = str(item["response"]).lower()
    expected = str(item["query"]).lower()

    total_latency += item["latency"]

    # Simple accuracy check
    if any(word in response for word in expected.split()):
        correct += 1
    else:
        hallucinations += 1

accuracy = (correct / total_queries) * 100
hallucination_rate = (hallucinations / total_queries) * 100
average_latency = total_latency / total_queries

report = {
    "total_queries": total_queries,
    "accuracy_percentage": accuracy,
    "hallucination_rate": hallucination_rate,
    "average_latency": average_latency
}

print(report)

# Save report
with open("evaluation_report.json", "w") as f:
    json.dump(report, f, indent=4)