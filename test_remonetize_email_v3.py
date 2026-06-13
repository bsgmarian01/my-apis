import os
import sys
import json
from src.llm_client import LLMClient
from src.validator import Validator
from remonetize_old_builds import remonetize_codebase, debug_codebase

OLLAMA_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://t5ds0879r1rl3m-11434.proxy.runpod.net")

def main():
    with open("config.json", "r") as f:
        config = json.load(f)
    stripe_link = config.get("STRIPE_LINK", "")
    llm = LLMClient(endpoint=OLLAMA_ENDPOINT)
    validator = Validator()
    
    app_dir = "builds/EmailValidator"
    with open(os.path.join(app_dir, "main.py"), "r", encoding="utf-8") as f:
        main_code = f.read()
    with open(os.path.join(app_dir, "test_main.py"), "r", encoding="utf-8") as f:
        test_code = f.read()
    with open(os.path.join(app_dir, "requirements.txt"), "r", encoding="utf-8") as f:
        reqs = f.read()
        
    print("Generating updated codebase...")
    new_main, new_test, new_reqs = remonetize_codebase(llm, main_code, test_code, reqs, stripe_link)
    
    print("Running tests...")
    success, test_log = validator.run_tests(new_main, new_test, new_reqs)
    print(f"Success: {success}")
    print("Test Log output:")
    print(test_log)
    print("\n--- NEW MAIN.PY CODE ---")
    print(new_main)
    print("\n--- NEW TEST_MAIN.PY CODE ---")
    print(new_test)

if __name__ == "__main__":
    main()
