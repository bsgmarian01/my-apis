from fastapi import FastAPI, Request, Header, Depends, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import RedirectResponse
from typing import Optional
import time

app = FastAPI()

RATE_LIMITS = {}
MAX_REQUESTS_PER_DAY = 100

class PhoneNumber(BaseModel):
    phone_number: str
    country_code: str

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    api_keys = os.getenv('API_KEYS', '').split(',')
    if x_api_key and x_api_key in api_keys:
        return
    
    client_ip = request.client.host
    current_time = int(time.time())
    
    if client_ip in RATE_LIMITS:
        requests_in_day = [req for req in RATE_LIMITS[client_ip] if (current_time - req) < 86400]
        if len(requests_in_day) >= MAX_REQUESTS_PER_DAY:
            raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
        else:
            RATE_LIMITS[client_ip].append(current_time)
    else:
        RATE_LIMITS[client_ip] = [current_time]

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.post("/validate/", dependencies=[Depends(verify_api_key_and_rate_limit)])
def validate_phone_number(phone_data: PhoneNumber):
    # Validate phone number logic here
    if not phone_data.phone_number.startswith("+"):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return {"message": "Phone number is valid"}

@app.post("/extract/", dependencies=[Depends(verify_api_key_and_rate_limit)])
def extract_phone_numbers(phone_data: PhoneNumber):
    # Extract phone numbers logic here
    if not phone_data.phone_number.startswith("+"):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return {"message": "Phone numbers extracted successfully"}