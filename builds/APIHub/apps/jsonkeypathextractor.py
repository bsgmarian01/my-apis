from typing import Optional, Dict
import json
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="JSON Key Path Extractor", description="This API allows developers to extract specific values from a JSON structure using a specified key path.")

# In-memory rate limiting dictionary
LIMIT_REQUESTS_PER_DAY = 100

class ExtractionRequest(BaseModel):
    json_data: str
    key_path: str

class ExtractionResponse(BaseModel):
    value: Optional[str]
    status: str


@app.get("/", include_in_schema=False)
def root():
    """
    Redirects to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")

@app.post("/extract", response_model=ExtractionResponse)
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

