import subprocess
import sys
import os


def test_dry_run_simulated_response():
    """Run test_langsmith.py with no MODEL_NAME and verify simulated output."""
    env = os.environ.copy()
    env.pop("MODEL_NAME", None)
    env.pop("GROQ_API_TOKEN", None)
    # Run the script from the backend directory
    backend_dir = os.path.dirname(__file__)
    proc = subprocess.run([sys.executable, "test_langsmith.py"], cwd=backend_dir, env=env, capture_output=True, text=True)

    assert proc.returncode == 0, f"Script failed: {proc.stderr}"
    assert "Simulated response: Hello LangSmith (dry-run)" in proc.stdout
