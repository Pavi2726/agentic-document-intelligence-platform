import json
import sys
import time
from pathlib import Path

backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

try:
    # Prefer using the supervisor workflow which exists in the repo.
    # Import lazily so that missing heavy ML deps don't crash simple evaluations.
    from app.agents.supervisor import run_supervisor as run_agentic_workflow  # pyright: ignore[reportMissingImports]
except Exception as exc:  # catch OSError from torch DLL load etc.
    # If importing the real workflow fails (missing deps like torch), provide
    # a lightweight fallback implementation so evaluations can still run.
    exc_msg = str(exc)
    print(f"Warning: could not import real workflow ({exc_msg}). Using fallback mock workflow.")

    def run_agentic_workflow(query: str):
        return {
            "query": query,
            "agent": "mock",
            "answer": "Mock response: heavy dependencies unavailable.",
            "note": exc_msg,
        }

evaluation_dir = Path(__file__).resolve().parent

# Load benchmark queries (path relative to this file)
with open(evaluation_dir / "benchmark_queries.json", "r") as f:
    benchmark_queries = json.load(f)

results = []

for item in benchmark_queries:
    query = item["query"]

    start_time = time.time()

    # TEMPORARY MOCK RESPONSE
    response = run_agentic_workflow(query)

    latency = time.time() - start_time

    result = {
        "id": item["id"],
        "query": query,
        "expected_type": item["type"],
        "response": response,
        "latency": latency
    }

    results.append(result)

# Save results next to the evaluation file
with open(evaluation_dir / "results.json", "w") as f:
    json.dump(results, f, indent=4)

print("Evaluation completed.")