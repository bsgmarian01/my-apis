import os
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import all sub-apps
from apps.creditcardvalidator import app as creditcardvalidator_app
from apps.currencyunitconverter import app as currencyunitconverter_app
from apps.datetimeformatchecker import app as datetimeformatchecker_app
from apps.emailvalidator import app as emailvalidator_app
from apps.emailvalidatorapi import app as emailvalidatorapi_app
from apps.htmltoplaintext import app as htmltoplaintext_app
from apps.ibanswiftvalidator import app as ibanswiftvalidator_app
from apps.isbnvalidator import app as isbnvalidator_app
from apps.jsonkeypathextractor import app as jsonkeypathextractor_app
from apps.jsonschemavalidator import app as jsonschemavalidator_app
from apps.markdowntohtml import app as markdowntohtml_app
from apps.passwordstrengthanalyzer import app as passwordstrengthanalyzer_app
from apps.phonenumbervalidator import app as phonenumbervalidator_app
from apps.xmltojsonconverter import app as xmltojsonconverter_app
from apps.yamltojsonconverter import app as yamltojsonconverter_app

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
app.mount("/creditcardvalidator", creditcardvalidator_app)
app.mount("/currencyunitconverter", currencyunitconverter_app)
app.mount("/datetimeformatchecker", datetimeformatchecker_app)
app.mount("/emailvalidator", emailvalidator_app)
app.mount("/emailvalidatorapi", emailvalidatorapi_app)
app.mount("/htmltoplaintext", htmltoplaintext_app)
app.mount("/ibanswiftvalidator", ibanswiftvalidator_app)
app.mount("/isbnvalidator", isbnvalidator_app)
app.mount("/jsonkeypathextractor", jsonkeypathextractor_app)
app.mount("/jsonschemavalidator", jsonschemavalidator_app)
app.mount("/markdowntohtml", markdowntohtml_app)
app.mount("/passwordstrengthanalyzer", passwordstrengthanalyzer_app)
app.mount("/phonenumbervalidator", phonenumbervalidator_app)
app.mount("/xmltojsonconverter", xmltojsonconverter_app)
app.mount("/yamltojsonconverter", yamltojsonconverter_app)

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
        
                <!-- Card for CurrencyUnitConverter -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">CurrencyUnitConverter</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Currency Unit Converter</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/currencyunitconverter/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('currencyunitconverter')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
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
        
                <!-- Card for EmailValidatorAPI -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">EmailValidatorAPI</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Email Validator A P I</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/emailvalidatorapi/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('emailvalidatorapi')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for HTMLToPlainText -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">HTMLToPlainText</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">H T M L To Plain Text</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/htmltoplaintext/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('htmltoplaintext')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for IBANSwiftValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">IBANSwiftValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">I B A N Swift Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/ibanswiftvalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('ibanswiftvalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for ISBNValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">ISBNValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">I S B N Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/isbnvalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('isbnvalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for JSONKeyPathExtractor -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">JSONKeyPathExtractor</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">J S O N Key Path Extractor</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/jsonkeypathextractor/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('jsonkeypathextractor')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for JSONSchemaValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">JSONSchemaValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">J S O N Schema Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/jsonschemavalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('jsonschemavalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for MarkdownToHTML -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">MarkdownToHTML</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Markdown To H T M L</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/markdowntohtml/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('markdowntohtml')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
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
        
                <!-- Card for PhoneNumberValidator -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">PhoneNumberValidator</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Phone Number Validator</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/phonenumbervalidator/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('phonenumbervalidator')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for XMLToJsonConverter -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">XMLToJsonConverter</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">X M L To Json Converter</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/xmltojsonconverter/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('xmltojsonconverter')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
                            Try It
                        </button>
                    </div>
                </div>
        
                <!-- Card for YAMLToJsonConverter -->
                <div class="glass-card p-6 rounded-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full">YAMLToJsonConverter</span>
                            <span class="text-xs text-gray-500">Active</span>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Y A M L To Json Converter</h3>
                        <p class="text-sm text-gray-400 mb-6">Validate, convert, and parse data with high performance.</p>
                    </div>
                    <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-800/60">
                        <a href="/yamltojsonconverter/docs" target="_blank" class="text-sm font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                            API Docs <i class="fas fa-external-link-alt text-xs"></i>
                        </a>
                        <button onclick="openPlayground('yamltojsonconverter')" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-colors">
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
                    body: JSON.stringify({ markdown_text: "# Hello\n\nThis is **bold** markdown." }, null, 4)
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
                    body: JSON.stringify({ yaml_data: "title: API Suite\nversion: 1.0\nenabled: true" }, null, 4)
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
    """
    return HTMLResponse(content=html_content, status_code=200)
