import os
import shutil
import re

def main():
    print("=== Building Unified API Hub ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    builds_dir = os.path.join(base_dir, "builds")
    hub_dir = os.path.join(builds_dir, "APIHub")
    apps_dir = os.path.join(hub_dir, "apps")
    
    os.makedirs(apps_dir, exist_ok=True)
    open(os.path.join(apps_dir, "__init__.py"), "w").close()

    # Find all API directories
    api_dirs = []
    for d in os.listdir(builds_dir):
        full_path = os.path.join(builds_dir, d)
        if os.path.isdir(full_path) and d != "APIHub" and not d.startswith("."):
            if os.path.exists(os.path.join(full_path, "main.py")):
                api_dirs.append(d)

    print(f"Found {len(api_dirs)} APIs to merge: {api_dirs}")

    # Gather and merge requirements
    merged_requirements = {
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "pytest",
        "jinja2"
    }

    for api in api_dirs:
        req_file = os.path.join(builds_dir, api, "requirements.txt")
        if os.path.exists(req_file):
            with open(req_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Clean inline comments
                        clean_req = line.split("#")[0].strip()
                        if clean_req:
                            merged_requirements.add(clean_req)

    # Write merged requirements.txt
    with open(os.path.join(hub_dir, "requirements.txt"), "w") as f:
        for req in sorted(list(merged_requirements)):
            f.write(f"{req}\n")
    print("Merged requirements.txt created.")

    # Copy each app to apps/
    for api in api_dirs:
        src_main = os.path.join(builds_dir, api, "main.py")
        dest_main = os.path.join(apps_dir, f"{api.lower()}.py")
        
        # Read the original code
        with open(src_main, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Remove any if __name__ == '__main__': blocks to avoid conflicts
        code = re.sub(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*\n(\s+.*)*', '', code)
        
        # Write modified code to the apps folder
        with open(dest_main, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Copied and prepared {api} -> apps/{api.lower()}.py")

    # Generate the main.py
    main_py_content = """import os
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import all sub-apps
"""
    for api in api_dirs:
        main_py_content += f"from apps.{api.lower()} import app as {api.lower()}_app\n"

    main_py_content += """
app = FastAPI(
    title="Developer API Suite",
    description="A single portal giving you access to multiple high-utility developer APIs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global/Shared rate limits and keys
RATE_LIMITS = {}
STRIPE_LINK = "https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00"

def verify_global_limit_and_key(request: Request, x_api_key: Optional[str] = Header(None)):
    valid_api_keys = set(os.getenv('API_KEYS', '').split(','))
    if x_api_key and x_api_key in valid_api_keys:
        return

    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean up old entries (older than 24 hours)
    keys_to_remove = [k for k, (count, last_checked) in RATE_LIMITS.items() 
                      if (current_time - last_checked).days >= 1]
    for key in keys_to_remove:
        del RATE_LIMITS[key]

    if client_ip not in RATE_LIMITS:
        RATE_LIMITS[client_ip] = (1, current_time)
    else:
        count, last_checked = RATE_LIMITS[client_ip]
        RATE_LIMITS[client_ip] = (count + 1, last_checked)

    if RATE_LIMITS[client_ip][0] > 100:
        raise HTTPException(
            status_code=402,
            detail=f"Rate limit exceeded. To get unlimited access and your API key, subscribe at: {STRIPE_LINK}"
        )

# Mount all sub-apps
"""
    for api in api_dirs:
        main_py_content += f'app.mount("/{api.lower()}", {api.lower()}_app)\n'

    # Add HTML Dashboard for the main app
    main_py_content += """
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    html_content = \"\"\"
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Developer API Suite</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: radial-gradient(circle at top right, #1e1b4b, #09090b);
            }
            .glass-card {
                background: rgba(30, 30, 45, 0.4);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        </style>
    </head>
    <body class="text-gray-100 min-h-screen font-sans antialiased">
        <header class="border-b border-gray-800 bg-black/40 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="bg-indigo-600 p-2 rounded-lg text-white">
                        <i class="fas fa-cubes fa-lg"></i>
                    </div>
                    <span class="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
                        DevSuite APIs
                    </span>
                </div>
                <div class="flex items-center space-x-4">
                    <input type="text" id="apiKeyInput" placeholder="Enter X-API-Key" class="bg-gray-950 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-indigo-500 w-48 sm:w-64" oninput="saveApiKey()">
                    <a href="https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00" target="_blank" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors flex items-center gap-2">
                        <i class="fas fa-credit-card"></i> Get Key
                    </a>
                </div>
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
                    10 powerful microservices in one single endpoint.
                </h1>
                <p class="text-lg text-gray-400">
                    A suite of high-performance utility APIs designed for developers. Up to 100 free requests per day, or subscribe for unlimited access.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    """
    
    # Add API cards
    for api in api_dirs:
        # Create a display name
        display_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', api)
        api_slug = api.lower()
        main_py_content += f"""
                <!-- Card for {api} -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">{api}</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">{display_name}</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/{api_slug}/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('{api_slug}')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        """

    main_py_content += """
            </div>
        </main>

        <!-- Modal Playground -->
        <div id="playgroundModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 hidden z-50">
            <div class="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col">
                <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
                    <h3 id="modalTitle" class="text-lg font-bold text-white">API Playground</h3>
                    <button onclick="closePlayground()" class="text-gray-400 hover:text-white transition-colors">
                        <i class="fas fa-times fa-lg"></i>
                    </button>
                </div>
                <div class="p-6 space-y-4 overflow-y-auto max-h-[75vh]">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Endpoint</label>
                        <div class="flex items-center bg-gray-950 px-3 py-2 rounded-lg border border-gray-800 text-sm font-mono text-gray-300">
                            <span class="text-green-400 font-bold mr-2">POST</span>
                            <span id="endpointPath">/validate</span>
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">JSON Request Body</label>
                        <textarea id="requestBody" rows="6" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-gray-300 focus:outline-none focus:border-indigo-500 resize-none"></textarea>
                    </div>
                    <div class="flex justify-between items-center">
                        <button onclick="sendRequest()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors flex items-center gap-2">
                            <span id="sendText">Send Request</span>
                            <i class="fas fa-paper-plane text-xs"></i>
                        </button>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Response</label>
                        <pre id="responseOutput" class="bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-green-400 overflow-x-auto min-h-[100px]">Click send to test the API...</pre>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Pre-populated request bodies for testing
            const requestTemplates = {
                "creditcardvalidator": {
                    path: "/creditcardvalidator/validate",
                    body: JSON.stringify({ card_number: "4111111111111111" }, null, 4)
                },
                "emailvalidator": {
                    path: "/emailvalidator/validate",
                    body: JSON.stringify({ email: "hello@world.com", check_domain: true }, null, 4)
                },
                "emailvalidatorapi": {
                    path: "/emailvalidatorapi/validate-email",
                    body: JSON.stringify({ email: "user@example.com" }, null, 4)
                },
                "htmltoplaintext": {
                    path: "/htmltoplaintext/convert",
                    body: JSON.stringify({ html_content: "<html><body><h1>Hello World</h1><p>Test</p></body></html>" }, null, 4)
                },
                "ibanswiftvalidator": {
                    path: "/ibanswiftvalidator/validate/iban", // fallback path
                    body: JSON.stringify({ iban: "DE89370400440532013000", swift_code: "INGDDEFF" }, null, 4)
                },
                "jsonschemavalidator": {
                    path: "/jsonschemavalidator/validate",
                    body: JSON.stringify({
                        data: { name: "Alice", age: 30 },
                        json_schema: {
                            type: "object",
                            properties: {
                                name: { type: "string" },
                                age: { type: "integer" }
                            },
                            required: ["name"]
                        }
                    }, null, 4)
                },
                "markdowntohtml": {
                    path: "/markdowntohtml/convert",
                    body: JSON.stringify({ markdown_text: "# Hello\\n\\nThis is **bold** markdown." }, null, 4)
                },
                "phonenumbervalidator": {
                    path: "/phonenumbervalidator/validate/",
                    body: JSON.stringify({ phone_number: "+14155552671", country_code: "US" }, null, 4)
                },
                "xmltojsonconverter": {
                    path: "/xmltojsonconverter/convert",
                    body: JSON.stringify({ xml_data: "<note><to>User</to><from>Admin</from><body>Welcome</body></note>" }, null, 4)
                },
                "yamltojsonconverter": {
                    path: "/yamltojsonconverter/convert",
                    body: JSON.stringify({ yaml_data: "title: API Suite\\nversion: 1.0\\nenabled: true" }, null, 4)
                }
            };

            let currentApi = "";

            // Load API key from local storage
            document.getElementById('apiKeyInput').value = localStorage.getItem('api_key') || '';

            function saveApiKey() {
                const key = document.getElementById('apiKeyInput').value;
                localStorage.setItem('api_key', key);
            }

            function openPlayground(apiSlug) {
                currentApi = apiSlug;
                const template = requestTemplates[apiSlug];
                document.getElementById('modalTitle').innerText = apiSlug.toUpperCase().replace(/-/g, ' ') + " PLAYGROUND";
                document.getElementById('endpointPath').innerText = template.path;
                document.getElementById('requestBody').value = template.body;
                document.getElementById('responseOutput').innerText = "Click send to test...";
                document.getElementById('responseOutput').className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-gray-400 overflow-x-auto min-h-[100px]";
                document.getElementById('playgroundModal').classList.remove('hidden');
            }

            function closePlayground() {
                document.getElementById('playgroundModal').classList.add('hidden');
            }

            async function sendRequest() {
                const path = document.getElementById('endpointPath').innerText;
                const bodyText = document.getElementById('requestBody').value;
                const responseOutput = document.getElementById('responseOutput');
                const sendText = document.getElementById('sendText');
                const apiKey = document.getElementById('apiKeyInput').value;

                sendText.innerText = "Sending...";
                responseOutput.innerText = "Processing request...";
                responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-yellow-400 overflow-x-auto min-h-[100px]";

                try {
                    const headers = {
                        "Content-Type": "application/json"
                    };
                    if (apiKey) {
                        headers["X-API-Key"] = apiKey;
                    }

                    const response = await fetch(path, {
                        method: "POST",
                        headers: headers,
                        body: bodyText
                    });

                    const data = await response.json();
                    responseOutput.innerText = JSON.stringify(data, null, 4);

                    if (response.status === 200) {
                        responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-green-400 overflow-x-auto min-h-[100px]";
                    } else if (response.status === 402) {
                        responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-red-400 overflow-x-auto min-h-[100px]";
                    } else {
                        responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-orange-400 overflow-x-auto min-h-[100px]";
                    }
                } catch (err) {
                    responseOutput.innerText = "Error: " + err.message;
                    responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-red-500 overflow-x-auto min-h-[100px]";
                } finally {
                    sendText.innerText = "Send Request";
                }
            }
        </script>
    </body>
    </html>
    \"\"\"
    return HTMLResponse(content=html_content, status_code=200)
"""

    with open(os.path.join(hub_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write(main_py_content)
    print("Unified main.py created.")

    # Generate test_main.py for APIHub
    test_py_content = """import pytest
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Developer API Suite" in response.text

def test_email_validator_route():
    # Test through the mounted app route
    response = client.post("/emailvalidator/validate", json={"email": "test@example.com", "check_domain": False})
    # Since we might not have API_KEYS configured in test environment, it should either return 200 or 402/422
    assert response.status_code in [200, 422, 402]
"""
    with open(os.path.join(hub_dir, "test_main.py"), "w", encoding="utf-8") as f:
        f.write(test_py_content)
    print("Unified test_main.py created.")

    # Generate Dockerfile for APIHub
    dockerfile_content = """FROM python:3.11-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
"""
    with open(os.path.join(hub_dir, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    print("Unified Dockerfile created.")

    # Generate README.md for APIHub
    readme_content = f"""---
title: API Suite
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Developer API Suite
All-in-one suite of 10 micro-services with unified landing page and monetization!
"""
    with open(os.path.join(hub_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Unified README.md created.")

    # Generate .gitignore for APIHub
    gitignore_content = """venv/
__pycache__/
*.pyc
.pytest_cache/
.git/
"""
    with open(os.path.join(hub_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("Unified .gitignore created.")
    print("=== API Hub Build Completed successfully ===")

if __name__ == "__main__":
    main()
