import os
import sys
import re
import json
import requests
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Tuple

# Path to the configuration of your original RunPod setup
ORIGINAL_CONFIG_PATH = "d:/Money_making/config.json"
BUILDS_DIR = "builds"

def load_runpod_config() -> Dict[str, Any]:
    """Loads Ollama LLM settings from the previous Money_making config.json."""
    if os.path.exists(ORIGINAL_CONFIG_PATH):
        try:
            with open(ORIGINAL_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "LLM_ENDPOINT": "https://k8k7jsxqre0keg-11434.proxy.runpod.net",
        "LLM_MODEL": "qwen2.5-coder:32b-instruct-q4_K_M"
    }

class JITOllamaClient:
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint.rstrip('/')
        self.generate_url = f"{self.endpoint}/api/generate"
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_ctx": 16384
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.generate_url, json=payload, timeout=300, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    full_response += chunk.get("response", "")
            return full_response
        except Exception as e:
            raise RuntimeError(f"Ollama communication failed: {e}")

def _clean_code(code: str) -> str:
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def run_local_validation(main_code: str, test_code: str, reqs: str) -> Tuple[bool, str]:
    """Runs pytest in a temporary folder to validate the codebase."""
    temp_dir = tempfile.mkdtemp(prefix="jit_val_")
    try:
        # Write files
        with open(os.path.join(temp_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(main_code)
        with open(os.path.join(temp_dir, "test_main.py"), "w", encoding="utf-8") as f:
            f.write(test_code)
        
        # Ensure essentials are listed in requirements
        req_lines = reqs.split('\n')
        essentials = ["fastapi", "uvicorn", "pytest", "httpx"]
        for item in essentials:
            if not any(item in line.lower() for line in req_lines if line.strip()):
                req_lines.append(item)
                
        with open(os.path.join(temp_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write('\n'.join(req_lines))

        # We execute pytest directly in the current environment to be fast
        # (Assuming the requirements are present in the runner environment)
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "test_main.py"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = (res.returncode == 0)
        output = f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        return success, output
    except Exception as e:
        return False, f"Validation runner encountered an error: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def generate_api_code(api_name, api_description, checkout_link="", ui_callback=None):
    def log(msg, level="info"):
        if ui_callback:
            ui_callback(msg, level)
        else:
            print(f"[{level.upper()}] {msg}")

    config_data = load_runpod_config()
    endpoint = config_data.get("LLM_ENDPOINT")
    model = config_data.get("LLM_MODEL")

    log(f"Connecting to RunPod LLM: {endpoint} ({model})...", "info")
    try:
        client = JITOllamaClient(endpoint, model)
    except Exception as e:
        return {"success": False, "error": f"Failed to initialize client: {e}"}

    system_prompt = (
        "You are an expert Python backend engineer. Write clean, idiomatic FastAPI code. "
        "Every endpoint must be fully functional, complete, and optimized. "
        "Do not include any rate-limiting, payment gateways, or billing restrictions. "
        "Ensure you redirect the root URL '/' to the interactive Swagger documentation '/docs' using RedirectResponse from fastapi.responses.\n"
        "Tests must be synchronous and use TestClient.\n"
        "Output requirements, main code, and pytest tests in the exact requested tags."
    )

    prompt = f"""
    Create a FastAPI project for the API named: {api_name}
    Requirements: {api_description}
    
    Format your response exactly as:
    ---START_REQUIREMENTS---
    [packages]
    ---END_REQUIREMENTS---
    ---START_MAIN---
    [main.py code]
    ---END_MAIN---
    ---START_TESTS---
    [test_main.py code]
    ---END_TESTS---
    """

    # Initial Gen
    log("Requesting initial code from RunPod...", "info")
    try:
        response = client.generate(prompt, system_prompt)
    except Exception as e:
        log(f"RunPod Ollama generation failed: {e}", "error")
        return {"success": False, "error": str(e)}

    # Parse helper
    def parse_blocks(text):
        reqs = re.search(r"---START_REQUIREMENTS---(.*?)---END_REQUIREMENTS---", text, re.DOTALL)
        main = re.search(r"---START_MAIN---(.*?)---END_MAIN---", text, re.DOTALL)
        tests = re.search(r"---START_TESTS---(.*?)---END_TESTS---", text, re.DOTALL)

        if not reqs or not main or not tests:
            # Fallback: try finding markdown code fences
            blocks = re.findall(r"```(?:python|requirements|txt)?\n(.*?)\n```", text, re.DOTALL)
            if len(blocks) >= 3:
                return _clean_code(blocks[1]), _clean_code(blocks[2]), _clean_code(blocks[0])
            
            # Save raw output for inspection
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(text)
                
            raise ValueError("Could not parse code blocks using standard tags or fallback code fences. Raw response saved to debug_response.txt.")
            
        return _clean_code(main.group(1)), _clean_code(tests.group(1)), _clean_code(reqs.group(1))

    try:
        main_code, test_code, reqs = parse_blocks(response)
    except Exception:
        log("Initial model response did not conform to the expected format.", "error")
        return {"success": False, "error": "Invalid format response from model."}

    # Debug loop
    max_attempts = 10
    validated = False
    last_log = ""

    for attempt in range(1, max_attempts + 1):
        log(f"Running validator tests (Attempt {attempt}/{max_attempts})...", "info")
        success, test_log = run_local_validation(main_code, test_code, reqs)
        last_log = test_log

        if success:
            log("Validation passed successfully!", "success")
            validated = True
            break
        else:
            log(f"Validation failed (Attempt {attempt}). Sending logs to Qwen for debugging.", "warning")
            short_log = test_log[:1000] + "..." if len(test_log) > 1000 else test_log
            log(f"Failures:\n{short_log}", "debug")

            if attempt < max_attempts:
                debug_prompt = f"""
                We ran the tests on the generated codebase, and they failed.
                
                ---CURRENT_MAIN---
                {main_code}
                
                ---CURRENT_TESTS---
                {test_code}
                
                ---CURRENT_REQUIREMENTS---
                {reqs}
                
                ---PYTEST_FAILURE_OUTPUT---
                {test_log}
                
                Fix the bugs. Return the updated blocks using the exact same tags.
                """
                debug_system_prompt = (
                    "You are an expert debugger. Analyze the code and pytest failures, correct all errors, "
                    "and return the complete corrected main.py, test_main.py, and requirements.txt "
                    "using the exact same tags:\n"
                    "---START_REQUIREMENTS---\n"
                    "[packages]\n"
                    "---END_REQUIREMENTS---\n"
                    "---START_MAIN---\n"
                    "[main.py code]\n"
                    "---END_MAIN---\n"
                    "---START_TESTS---\n"
                    "[test_main.py code]\n"
                    "---END_TESTS---"
                )
                try:
                    response = client.generate(debug_prompt, debug_system_prompt)
                    main_code, test_code, reqs = parse_blocks(response)
                except Exception as e:
                    log(f"Failed during debugging iteration: {e}", "error")
                    return {"success": False, "error": f"Debug loop error: {e}"}
            else:
                log("Exceeded maximum debugging attempts.", "error")

    if not validated:
        return {"success": False, "error": "Validation failed after 10 attempts.", "logs": last_log}

    # Save to builds/
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', api_name.replace(" ", ""))
    api_dir = os.path.join(BUILDS_DIR, safe_name)
    os.makedirs(api_dir, exist_ok=True)

    try:
        with open(os.path.join(api_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(main_code)
        with open(os.path.join(api_dir, "test_main.py"), "w", encoding="utf-8") as f:
            f.write(test_code)
        with open(os.path.join(api_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(reqs)
        return {
            "success": True,
            "api_name": api_name,
            "directory": api_dir,
            "files": ["main.py", "test_main.py", "requirements.txt"]
        }
    except Exception as e:
        return {"success": False, "error": f"Save failed: {e}"}
