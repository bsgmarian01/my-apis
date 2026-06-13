from fastapi import FastAPI, Request, Header, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import os
import yaml
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(
    title="YAML to JSON Converter",
    description="This API provides a simple utility for converting YAML formatted data into JSON format. It is useful for developers who need to integrate or migrate data between systems that use different data serialization standards.",
    version="1.0.0"
)

# In-memory rate limiting dictionary
RATE_LIMITS = {}

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Dependency function to validate API key and apply rate limiting.
    Valid API keys are loaded from the environment variable 'API_KEYS' on every request.
    If a valid API Key is provided in the 'X-API-Key' header, bypass rate limits and allow the request.
    Otherwise, allow the request ONLY if the client IP has not exceeded 100 requests per day.
    """
    api_keys = os.getenv('API_KEYS', '').split(',')
    
    # Check for a valid API key
    if x_api_key and x_api_key in api_keys:
        return
    
    # Get client IP
    ip_address = request.client.host
    
    # Get current date to track requests per day
    today = datetime.now().date()
    
    # Initialize rate limit dictionary entry if not present
    if ip_address not in RATE_LIMITS:
        RATE_LIMITS[ip_address] = {'count': 1, 'last_checked': today}
    else:
        # Check if the last checked date is different from today, reset count if so
        if RATE_LIMITS[ip_address]['last_checked'] != today:
            RATE_LIMITS[ip_address]['count'] = 1
            RATE_LIMITS[ip_address]['last_checked'] = today
        else:
            # Increment request count for today
            RATE_LIMITS[ip_address]['count'] += 1
    
    # Check if the request count exceeds the limit (100 per day)
    if RATE_LIMITS[ip_address]['count'] > 100:
        raise HTTPException(
            status_code=402,
            detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'
        )

# Pydantic model for request body
class ConvertRequest(BaseModel):
    yaml_data: str

# Pydantic model for response body
class ConvertResponse(BaseModel):
    json_data: dict

@app.get("/", include_in_schema=False)
def root():
    """
    Root endpoint that redirects to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")

@app.post("/convert", dependencies=[Depends(verify_api_key_and_rate_limit)], response_model=ConvertResponse)
def convert_yaml_to_json(request: ConvertRequest):
    """
    Converts YAML formatted text into JSON format.
    
    Parameters:
    - request (ConvertRequest): The request body containing the YAML data.
    
    Returns:
    - ConvertResponse: A response object containing the converted JSON data.
    """
    try:
        # Parse YAML data
        json_data = yaml.safe_load(request.yaml_data)
        
        return ConvertResponse(json_data=json_data)
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML data: {str(e)}"
        )

