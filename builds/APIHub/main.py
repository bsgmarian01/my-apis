import os
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import all sub-apps
from apps.advancedquantitativeriskratiocalculator import app as advancedquantitativeriskratiocalculator_app
from apps.creditcardvalidator import app as creditcardvalidator_app
from apps.datetimeformatchecker import app as datetimeformatchecker_app
from apps.dynamicqrcodeconfigurationhelper import app as dynamicqrcodeconfigurationhelper_app
from apps.e_commercediscounttierrulesoptimizer import app as e_commercediscounttierrulesoptimizer_app
from apps.emailvalidator import app as emailvalidator_app
from apps.gdprdataretentionlifespanengine import app as gdprdataretentionlifespanengine_app
from apps.passwordstrengthanalyzer import app as passwordstrengthanalyzer_app
from apps.saas_failed_payment_recovery.main import app as payment_recovery_app

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

# Mount all sub-apps
app.mount("/advancedquantitativeriskratiocalculator", advancedquantitativeriskratiocalculator_app)
app.mount("/creditcardvalidator", creditcardvalidator_app)
app.mount("/datetimeformatchecker", datetimeformatchecker_app)
app.mount("/dynamicqrcodeconfigurationhelper", dynamicqrcodeconfigurationhelper_app)
app.mount("/e_commercediscounttierrulesoptimizer", e_commercediscounttierrulesoptimizer_app)
app.mount("/emailvalidator", emailvalidator_app)
app.mount("/gdprdataretentionlifespanengine", gdprdataretentionlifespanengine_app)
app.mount("/passwordstrengthanalyzer", passwordstrengthanalyzer_app)
app.mount("/payment-recovery", payment_recovery_app)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    html_content = """
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
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
                    9 powerful microservices in one single endpoint.
                </h1>
                <p class="text-lg text-gray-400">
                    A suite of high-performance utility APIs designed for developers.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    
                <!-- Card for AdvancedQuantitativeRiskRatioCalculator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">AdvancedQuantitativeRiskRatioCalculator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Advanced Quantitative Risk Ratio Calculator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/advancedquantitativeriskratiocalculator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('advancedquantitativeriskratiocalculator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for CreditCardValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">CreditCardValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Credit Card Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/creditcardvalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('creditcardvalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for DateTimeFormatChecker -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">DateTimeFormatChecker</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Date Time Format Checker</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/datetimeformatchecker/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('datetimeformatchecker')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for DynamicQRCodeConfigurationHelper -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">DynamicQRCodeConfigurationHelper</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Dynamic Q R Code Configuration Helper</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/dynamicqrcodeconfigurationhelper/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('dynamicqrcodeconfigurationhelper')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for E-CommerceDiscountTierRulesOptimizer -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">E-CommerceDiscountTierRulesOptimizer</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">E- Commerce Discount Tier Rules Optimizer</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/e-commercediscounttierrulesoptimizer/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('e-commercediscounttierrulesoptimizer')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for EmailValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">EmailValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Email Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/emailvalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('emailvalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for GDPRDataRetentionLifespanEngine -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">GDPRDataRetentionLifespanEngine</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">G D P R Data Retention Lifespan Engine</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/gdprdataretentionlifespanengine/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('gdprdataretentionlifespanengine')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for PasswordStrengthAnalyzer -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">PasswordStrengthAnalyzer</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Password Strength Analyzer</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/passwordstrengthanalyzer/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('passwordstrengthanalyzer')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for SaaSFailedPaymentIntelligentRecoveryEngine -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">SaaSFailedPaymentIntelligentRecoveryEngine</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Saa S Failed Payment Intelligent Recovery Engine</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/saasfailedpaymentintelligentrecoveryengine/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('saasfailedpaymentintelligentrecoveryengine')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
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
                "currencyunitconverter": {
                    path: "/currencyunitconverter/convert",
                    body: JSON.stringify({ amount: 100.0, from_currency: "USD", to_currency: "EUR" }, null, 4)
                },
                "datetimeformatchecker": {
                    path: "/datetimeformatchecker/validate-datetime",
                    body: JSON.stringify({ date_str: "2026-06-13", format_str: "%Y-%m-%d" }, null, 4)
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
                    path: "/ibanswiftvalidator/validate/iban",
                    body: JSON.stringify({ iban: "DE89370400440532013000" }, null, 4)
                },
                "isbnvalidator": {
                    path: "/isbnvalidator/validate-isbn",
                    body: JSON.stringify({ isbn: "978-3-16-148410-0" }, null, 4)
                },
                "jsonkeypathextractor": {
                    path: "/jsonkeypathextractor/extract",
                    body: JSON.stringify({ json_data: '{"user": {"profile": {"name": "Alice"}}}', key_path: "user.profile.name" }, null, 4)
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
                "passwordstrengthanalyzer": {
                    path: "/passwordstrengthanalyzer/analyze",
                    body: JSON.stringify({ password: "StrongPassword123!" }, null, 4)
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

                sendText.innerText = "Sending...";
                responseOutput.innerText = "Processing request...";
                responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-yellow-400 overflow-x-auto min-h-[100px]";

                try {
                    const headers = {
                        "Content-Type": "application/json"
                    };

                    const response = await fetch(path, {
                        method: "POST",
                        headers: headers,
                        body: bodyText
                    });

                    const data = await response.json();
                    responseOutput.innerText = JSON.stringify(data, null, 4);

                    if (response.status === 200) {
                        responseOutput.className = "bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-sm text-green-400 overflow-x-auto min-h-[100px]";
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
    """
    return HTMLResponse(content=html_content, status_code=200)
