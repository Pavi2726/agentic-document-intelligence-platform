from dotenv import load_dotenv
load_dotenv()

from importlib import import_module
import argparse
import os

# Defer importing the Groq client until a real request is needed to keep
# test runs lightweight (CI/dry-run won't require langchain_groq installed).


def main(argv=None):
    # Read model name from environment so tests don't rely on a hard-coded model.
    # Set MODEL_NAME in your .env to a supported Groq model (see Groq deprecations docs).
    MODEL_NAME = os.getenv("MODEL_NAME")

    # Check for common API keys and warn early if missing.
    missing_keys = []
    for key in ("GROQ_API_KEY", "GROQ_API_TOKEN", "LANGCHAIN_API_KEY", "LANGSMITH_API_KEY"):
        if os.getenv(key) is None:
            missing_keys.append(key)

    if missing_keys:
        print("Warning: the following environment variables are not set:", ", ".join(missing_keys))
        print("If you rely on Groq or LangSmith, set the appropriate API keys in your .env file.")

    parser = argparse.ArgumentParser(description="Test Groq/LangSmith integration (safe defaults).")
    parser.add_argument("--model", "-m", help="Model name to use (overrides MODEL_NAME env)")
    parser.add_argument("--real", action="store_true", help="Perform a real API call (requires model and API keys)")
    args = parser.parse_args(argv)

    if args.model:
        MODEL_NAME = args.model

    # Default to dry-run; require explicit --real flag to perform external calls.
    dry_run = True
    if args.real:
        if not MODEL_NAME:
            print("Cannot run real request: MODEL_NAME not set.")
            dry_run = True
        else:
            # If user explicitly requested a real call, ensure API keys exist
            required = ("GROQ_API_KEY", "GROQ_API_TOKEN")
            missing = [k for k in required if not os.getenv(k)]
            if missing:
                print(f"Cannot run real request: missing required keys: {', '.join(missing)}")
                dry_run = True
            else:
                dry_run = False

    # Treat model names prefixed with `test-` as simulated safe models even when --real is passed.
    if MODEL_NAME and MODEL_NAME.startswith("test-"):
        print(f"MODEL_NAME '{MODEL_NAME}' is a test model; forcing simulated mode.")
        dry_run = True

    llm = None

    try:
        if dry_run:
            print("\nDry-run: would invoke model=", MODEL_NAME)
            print("Simulated response: Hello LangSmith (dry-run)")
        else:
            # Instantiate the client now that we have a MODEL_NAME. Import lazily
            # so CI and dry-run tests don't need langchain_groq installed.
            ChatGroq = import_module("langchain_groq").ChatGroq
            llm = ChatGroq(model_name=MODEL_NAME)
            response = llm.invoke("Hello LangSmith")
            print(response.content)
    except Exception as e:
        import traceback
        traceback.print_exc()

        msg = str(e)
        if "decommissioned" in msg.lower() or "model_decommissioned" in msg.lower():
            print("\nHint: The chosen model appears to be decommissioned.")
            print("Set `MODEL_NAME` to a supported Groq model and try again. See:")
            print("https://console.groq.com/docs/deprecations")
        if "forbidden" in msg.lower() or "403" in msg:
            print("\nHint: Received 403 from LangSmith. Check your LangSmith/LangChain API key and permissions.")


if __name__ == "__main__":
    main()