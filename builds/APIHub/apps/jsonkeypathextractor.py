from typing import Optional, Dict
import json
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI(title="JSON Key Path Extractor", description="This API allows developers to extract specific values from a JSON structure using a specified key path.")

# In-memory rate limiting dictionary
RATE_LIMITS: Dict[str, int] = defaultdict(int)
LIMIT_REQUESTS_PER_DAY = 100

class ExtractionRequest(BaseModel):
    json_data: str
    key_path: str

class ExtractionResponse(BaseModel):
    value: Optional[str]
    status: str

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Dependency function to verify API key and apply rate limiting.
    
    Checks if a valid API key is provided. If not, it applies rate limiting based on the client's IP address.
    """
    api_keys = set(os.getenv('API_KEYS', '').split(','))
    ip_address = request.client.host
    
    if x_api_key in api_keys:
        return  # Bypass rate limits for valid API keys
    
    today = datetime.now().date()
    key = f"{ip_address}_{today}"
    
    if RATE_LIMITS[key] >= LIMIT_REQUESTS_PER_DAY:
        raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
    
    RATE_LIMITS[key] += 1

@app.get("/", include_in_schema=False)
def root():
    """
    Redirects to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")

@app.post("/extract", response_model=ExtractionResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
def extract_value(request: ExtractionRequest):
    """
    Extracts a value from a JSON object using a specified key path.
    
    Args:
        request (ExtractionRequest): The extraction request containing the JSON data and the key path.
        
    Returns:
        ExtractionResponse: The extracted value or an error status.
    """
    try:
        json_obj = json.loads(request.json_data)
        keys = request.key_path.split('.')
        current_value = json_obj
        
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return ExtractionResponse(value=None, status="Key path not found")
        
        return ExtractionResponse(value=str(current_value), status="success")
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data provided")

