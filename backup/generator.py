import json
from typing import Dict, Any, Tuple
from .llm_client import LLMClient

class Generator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def _clean_code(self, code: str) -> str:
        """
        Removes markdown code fences (e.g. ```python) that LLMs sometimes include.
        """
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that start with ```
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines).strip()

    def generate_codebase(self, api_spec: Dict[str, Any], stripe_link: str = "") -> Tuple[str, str, str]:
        """
        Generates:
        1. FastAPI main.py content
        2. pytest test_main.py content
        3. requirements.txt content
        
        Returns (main_code, test_code, requirements_content)
        """
        system_prompt = (
            "You are an expert Python backend engineer. Write clean, idiomatic FastAPI code. "
            "Always include complete typing, Pydantic data schemas, proper error handling, "
            "and comprehensive inline docstrings. "
            "Every API must implement API key validation and rate limiting using a custom FastAPI dependency (NOT HTTP middleware) injected globally or into all endpoints. "
            "Specifically:\n"
            "1. Define a dependency function (e.g., `verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None))`).\n"
            "2. Valid API keys MUST be loaded from the environment variable 'API_KEYS' inside the dependency function on every request (e.g. read using `os.getenv('API_KEYS', '').split(',')` or similar, NOT loaded once globally at the top of the file). This ensures that environment changes are detected dynamically.\n"
            "3. If a valid API Key is provided in the 'X-API-Key' header, bypass rate limits and allow the request.\n"
            f"4. If no valid key is provided (or the header is missing/invalid), allow the request ONLY if the client IP (from `request.client.host`) has not exceeded 100 requests per day (stored in a simple in-memory dict `RATE_LIMITS`). If the limit is exceeded, raise `HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: {stripe_link}')`.\n"
            "5. CRITICAL CORRECTNESS RULES:\n"
            "   - You MUST add a GET endpoint at the root (`/`) that redirects users to the interactive documentation (`/docs`) using FastAPI's `RedirectResponse`. You MUST import `RedirectResponse` from `fastapi.responses` (i.e. `from fastapi.responses import RedirectResponse`), NOT from `fastapi` directly, as `fastapi` does not expose it at the root package level. Set `include_in_schema=False` on the root route. This prevents users from getting a 404 'Not Found' when opening the Hugging Face Space.\n"
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
            "Provide your output exactly in the requested XML-style format."
        )

        prompt = f"""
Given the following API Specification:
{json.dumps(api_spec, indent=2)}

Generate the complete codebase. You must format your response exactly like this:
---START_REQUIREMENTS---
[requirements.txt packages here, one per line. Include fastapi, uvicorn, pytest, httpx, and any other external packages you import]
---END_REQUIREMENTS---
---START_MAIN---
[fastapi application code here, written to run on port 8000 using uvicorn. Ensure all endpoints are fully implemented; do NOT use pass or placeholders.]
---END_MAIN---
---START_TESTS---
[pytest code here using fastapi.testclient.TestClient or httpx to exhaustively test all endpoints with both positive and negative cases.]
---END_TESTS---
"""

        response = self.llm.generate(prompt=prompt, system_prompt=system_prompt)
        
        # Parse output
        try:
            reqs = response.split("---START_REQUIREMENTS---")[1].split("VE---END_REQUIREMENTS---" if "VE---END_REQUIREMENTS---" in response else "---END_REQUIREMENTS---")[0].strip()
            main_code = response.split("---START_MAIN---")[1].split("---END_MAIN---")[0].strip()
            test_code = response.split("---START_TESTS---")[1].split("---END_TESTS---")[0].strip()
            
            # Clean any backticks from code
            return self._clean_code(main_code), self._clean_code(test_code), self._clean_code(reqs)
        except IndexError:
            raise RuntimeError(f"Model failed to output standard demarcated blocks. Output was:\n{response}")

    def debug_codebase(self, main_code: str, test_code: str, requirements: str, test_output: str, stripe_link: str = "") -> Tuple[str, str, str]:
        """
        Refines codebase based on test errors and stdout/stderr outputs.
        """
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
            "4. You MUST add a GET endpoint at the root (`/`) that redirects users to `/docs` using FastAPI's `RedirectResponse` (with `include_in_schema=False`). You MUST import `RedirectResponse` from `fastapi.responses` (i.e. `from fastapi.responses import RedirectResponse`), NOT from `fastapi` directly.\n"
            "5. CRITICAL TESTING RULES:\n"
            "   - Always write synchronous test functions using `from fastapi.testclient import TestClient`.\n"
            "   - Do NOT use `async def` for test functions.\n"
            "   - Do NOT use `await` with `client.get`, `client.post`, etc. FastAPI's `TestClient` is synchronous.\n"
            "6. CRITICAL TEST STATE ISOLATION:\n"
            "   - You MUST import the global rate limit dictionary inside your test functions and clear it (e.g., `from main import RATE_LIMITS` then `RATE_LIMITS.clear()`) at the start of every test case. This is crucial because pytest runs all tests in the same process, meaning they share the client IP address (127.0.0.1) and will trigger the 402 limit prematurely due to crosstalk."
        )

        prompt = f"""
We ran the tests on the generated codebase, and they failed.

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
        response = self.llm.generate(prompt=prompt, system_prompt=system_prompt)
        try:
            reqs = response.split("---START_REQUIREMENTS---")[1].split("---END_REQUIREMENTS---")[0].strip()
            new_main = response.split("---START_MAIN---")[1].split("---END_MAIN---")[0].strip()
            new_tests = response.split("---START_TESTS---")[1].split("---END_TESTS---")[0].strip()
            
            return self._clean_code(new_main), self._clean_code(new_tests), self._clean_code(reqs)
        except IndexError:
            raise RuntimeError(f"Debugging model failed to output standard blocks. Output was:\n{response}")
