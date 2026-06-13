import os
import sys
import json
from src.llm_client import LLMClient
from src.validator import Validator
from src.hf_deployer import HFDeployer

# Configuration
OLLAMA_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://t5ds0879r1rl3m-11434.proxy.runpod.net")

def remonetize_codebase(llm: LLMClient, main_code: str, test_code: str, requirements: str, stripe_link: str) -> tuple:
    system_prompt = (
        "You are an expert Python backend engineer and debugger. Your task is to update an existing FastAPI application "
        "to add API key validation and rate limiting using a custom FastAPI dependency (NOT HTTP middleware) injected globally or into all endpoints "
        "while keeping all existing endpoints, functions, and logic completely intact.\n\n"
        "Requirements:\n"
        "1. Define a dependency function (e.g., `verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None))`).\n"
        "2. Valid API keys MUST be loaded from the environment variable 'API_KEYS' inside the dependency function on every request (e.g. read using `os.getenv('API_KEYS', '').split(',')` or similar, NOT loaded once globally at the top of the file). This ensures that environment changes are detected dynamically.\n"
        "3. If a valid API Key is provided in the 'X-API-Key' header, bypass rate limits and allow the request.\n"
        f"4. If no valid key is provided (or the header is missing/invalid), allow the request ONLY if the client IP (from `request.client.host`) has not exceeded 100 requests per day (stored in a simple in-memory dict `RATE_LIMITS`). If the limit is exceeded, raise `HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: {stripe_link}')`.\n"
        "5. CRITICAL CORRECTNESS RULES:\n"
        "   - You MUST add a GET endpoint at the root (`/`) that redirects users to `/docs` using FastAPI's `RedirectResponse` (imported from `fastapi.responses`). Set `include_in_schema=False` on the root route. This prevents users from getting a 404 'Not Found' when opening the Hugging Face Space.\n"
        "   - Do NOT load 'API_KEYS' globally at the top of `main.py`; it must be fetched dynamically inside the dependency function on every request so it can be mocked/updated at runtime.\n"
        "   - Do NOT hardcode endpoints to reject requests without a key (do NOT return 403 for missing keys), as this completely defeats the 100 free requests rate limit rule.\n"
        "   - Prefer using a FastAPI dependency (`Depends`) instead of HTTP middleware (`@app.middleware('http')`), as raising `HTTPException` inside dependency injections works natively in FastAPI and returns the correct status code to clients.\n"
        "6. CRITICAL TESTING RULES:\n"
        "   - Always write synchronous test functions using `from fastapi.testclient import TestClient`.\n"
        "   - Do NOT use `async def` for test functions.\n"
        "   - Do NOT use `await` with `client.get`, `client.post`, etc. FastAPI's `TestClient` is synchronous.\n"
        "7. CRITICAL TEST STATE ISOLATION:\n"
        "   - Because tests run in the same process, they share the global in-memory rate-limiting dictionary state (all requests from `TestClient` default to IP `127.0.0.1`).\n"
        "   - To prevent test crosstalk (where one test's requests cause another test to fail with 402), you MUST import the global rate limit dictionary inside the test functions and clear it (e.g., `from main import RATE_LIMITS` then `RATE_LIMITS.clear()`) at the start of every test case.\n"
        "   - You MUST write a test that verifies unauthenticated requests succeed up to the limit and then return 402 once exceeded, AND a test verifying valid API keys bypass this limit.\n"
        "8. Do not modify the existing core endpoint functionalities. Keep them exactly as they are.\n"
        "9. FORMATTING RULE: You MUST output your response containing ONLY the designated blocks (---START_REQUIREMENTS---, ---END_REQUIREMENTS---, ---START_MAIN---, ---END_MAIN---, ---START_TESTS---, ---END_TESTS---). Do NOT include any chat headers, introductory text, explanations, or conversational filler. Start directly with the first block."
    )

    prompt = f"""
We want to add monetization (X-API-Key and rate-limiting dependency) to the following codebase:

---CURRENT_MAIN---
{main_code}

---CURRENT_TESTS---
{test_code}

---CURRENT_REQUIREMENTS---
{requirements}

Return the updated files enclosed in standard blocks. Do not add explanations, conversational introduction, or markdown comments. Output format:
---START_REQUIREMENTS---
...
---END_REQUIREMENTS---
---START_MAIN---
...
---END_MAIN---
---START_TESTS---
...
---END_TESTS---
"""
    response = llm.generate(prompt=prompt, system_prompt=system_prompt)
    
    # Strip fences helper
    def clean_code(code: str) -> str:
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines).strip()

    try:
        reqs = response.split("---START_REQUIREMENTS---")[1].split("VE---END_REQUIREMENTS---" if "VE---END_REQUIREMENTS---" in response else "---END_REQUIREMENTS---")[0].strip()
        new_main = response.split("---START_MAIN---")[1].split("---END_MAIN---")[0].strip()
        new_tests = response.split("---START_TESTS---")[1].split("---END_TESTS---")[0].strip()
        return clean_code(new_main), clean_code(new_tests), clean_code(reqs)
    except IndexError:
        raise RuntimeError(f"Model failed to output standard blocks. Output was:\n{response}")

def debug_codebase(llm: LLMClient, main_code: str, test_code: str, requirements: str, test_output: str, stripe_link: str) -> tuple:
    system_prompt = (
        "You are an expert debugger. Analyze the current code and the corresponding pytest tracebacks. "
        "Correct all errors. Return the entire updated main.py, test_main.py, and requirements.txt "
        "using the exact same demarcation blocks. "
        "Make sure to keep the X-API-Key checking and rate-limiting dependency functionality intact: "
        f"If the daily limit of 100 requests per IP is exceeded without a valid key from 'API_KEYS', return HTTP 402 with the subscription link: {stripe_link}.\n"
        "CRITICAL DEPENDENCY RULES:\n"
        "1. Do NOT write a middleware that raises HTTPException (which fails inside Starlette middleware). Instead, use a FastAPI dependency (e.g. using `Depends(verify_api_key_and_rate_limit)`) for endpoints.\n"
        "2. Ensure the dependency does NOT block requests without a key with a 403 unless they also exceed the 100 free requests rate limit.\n"
        "3. Valid API keys MUST be loaded from the environment variable 'API_KEYS' inside the dependency function on every request (e.g. read using `os.getenv('API_KEYS', '').split(',')` or similar, NOT loaded once globally at the top of the file). This ensures that environment changes during tests are detected dynamically.\n"
        "4. You MUST add a GET endpoint at the root (`/`) that redirects users to `/docs` using FastAPI's `RedirectResponse` (with `include_in_schema=False`).\n"
        "5. CRITICAL TESTING RULES:\n"
        "   - Always write synchronous test functions using `from fastapi.testclient import TestClient`.\n"
        "   - Do NOT use `async def` for test functions.\n"
        "   - Do NOT use `await` with `client.get`, `client.post`, etc. FastAPI's `TestClient` is synchronous.\n"
        "6. CRITICAL TEST STATE ISOLATION:\n"
        "   - You MUST import the global rate limit dictionary inside your test functions and clear it (e.g., `from main import RATE_LIMITS` then `RATE_LIMITS.clear()`) at the start of every test case. This is crucial because pytest runs all tests in the same process, meaning they share the client IP address (127.0.0.1) and will trigger the 402 limit prematurely due to crosstalk.\n"
        "7. FORMATTING RULE: You MUST output your response containing ONLY the designated blocks (---START_REQUIREMENTS---, ---END_REQUIREMENTS---, ---START_MAIN---, ---END_MAIN---, ---START_TESTS---, ---END_TESTS---). Do NOT include any chat headers, introductory text, explanations, or conversational filler. Start directly with the first block."
    )


    prompt = f"""
We ran the tests on the codebase, and they failed.

---CURRENT_MAIN---
{main_code}

---CURRENT_TESTS---
{test_code}

---CURRENT_REQUIREMENTS---
{requirements}

---PYTEST_FAILURE_OUTPUT---
{test_output}

Please fix the bugs causing the test failures. Return the fixed files enclosed in the standard blocks:
---START_REQUIREMENTS---
...
---END_REQUIREMENTS---
---START_MAIN---
...
---END_MAIN---
---START_TESTS---
...
---END_TESTS---
"""
    response = llm.generate(prompt=prompt, system_prompt=system_prompt)
    
    def clean_code(code: str) -> str:
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines).strip()

    try:
        reqs = response.split("---START_REQUIREMENTS---")[1].split("---END_REQUIREMENTS---")[0].strip()
        new_main = response.split("---START_MAIN---")[1].split("---END_MAIN---")[0].strip()
        new_tests = response.split("---START_TESTS---")[1].split("---END_TESTS---")[0].strip()
        return clean_code(new_main), clean_code(new_tests), clean_code(reqs)
    except IndexError:
        raise RuntimeError(f"Debugging model failed to output standard blocks. Output was:\n{response}")

def main():
    print("=== Starting Remonetization of Existing APIs ===")
    
    # 1. Load configuration
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("[MIGRATOR] ERROR: config.json not found!")
        sys.exit(1)
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    token = config.get("HF_TOKEN")
    username = config.get("HF_USERNAME")
    stripe_link = config.get("STRIPE_LINK", "")
    
    if not token or not username or not stripe_link:
        print("[MIGRATOR] ERROR: HF_TOKEN, HF_USERNAME, or STRIPE_LINK not set in config.json.")
        sys.exit(1)
        
    ollama_endpoint = os.getenv("LLM_ENDPOINT", config.get("LLM_ENDPOINT", OLLAMA_ENDPOINT))
    llm_model = config.get("LLM_MODEL", "qwen2.5-coder:32b-instruct-q4_K_M")
    llm = LLMClient(endpoint=ollama_endpoint, model=llm_model)
    validator = Validator()
    deployer = HFDeployer(token=token, username=username)
    
    builds_dir = "builds"
    if not os.path.exists(builds_dir):
        print("[MIGRATOR] No builds directory found.")
        sys.exit(0)
        
    folders = [d for d in os.listdir(builds_dir) if os.path.isdir(os.path.join(builds_dir, d))]
    print(f"[MIGRATOR] Found {len(folders)} old APIs to remonetize and deploy: {folders}")
    
    for folder in folders:
        app_dir = os.path.join(builds_dir, folder)
        main_path = os.path.join(app_dir, "main.py")
        test_path = os.path.join(app_dir, "test_main.py")
        reqs_path = os.path.join(app_dir, "requirements.txt")
        
        if not os.path.exists(main_path):
            print(f"[MIGRATOR] Skipping {folder} - main.py not found.")
            continue
            
        print(f"\n--- Remonetizing {folder} ---")
        
        with open(main_path, "r", encoding="utf-8") as f:
            main_code = f.read()
        
        test_code = ""
        if os.path.exists(test_path):
            with open(test_path, "r", encoding="utf-8") as f:
                test_code = f.read()
                
        reqs = ""
        if os.path.exists(reqs_path):
            with open(reqs_path, "r", encoding="utf-8") as f:
                reqs = f.read()
                
        try:
            # 1. Ask LLM to inject middleware
            new_main, new_test, new_reqs = remonetize_codebase(llm, main_code, test_code, reqs, stripe_link)
        except Exception as e:
            print(f"[MIGRATOR] Error modifying code for {folder}: {e}")
            continue
            
        # 2. Run test & self-debug loop
        validated = False
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            print(f"[{folder}] Running tests (Attempt {attempt}/{max_attempts})...")
            success, test_log = validator.run_tests(new_main, new_test, new_reqs)
            if success:
                print(f"[{folder}] Tests passed!")
                validated = True
                break
            else:
                print(f"[{folder}] Tests failed. Debugging...")
                try:
                    new_main, new_test, new_reqs = debug_codebase(llm, new_main, new_test, new_reqs, test_log, stripe_link)
                except Exception as dbg_err:
                    print(f"[{folder}] Debugging error: {dbg_err}")
                    break
                    
        if validated:
            # Save monetized files
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(new_main)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(new_test)
            with open(reqs_path, "w", encoding="utf-8") as f:
                f.write(new_reqs)
                
            print(f"[{folder}] Saved updated code files.")
            
            # Deploy to Hugging Face
            print(f"[{folder}] Deploying to Hugging Face...")
            try:
                live_url = deployer.deploy_space(folder, app_dir)
                print(f"[{folder}] Deploy success!")
                print(f"-> Live URL: {live_url}")
            except Exception as deploy_err:
                print(f"[{folder}] Deploy failed: {deploy_err}")
        else:
            print(f"[MIGRATOR] Skipping deployment for {folder} as tests could not be resolved.")

if __name__ == "__main__":
    main()
