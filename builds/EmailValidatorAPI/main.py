from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel, EmailStr
import os
from datetime import date
from typing import Optional
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Email Validator Microservice",
    description="A reliable microservice for validating email addresses based on common patterns, ensuring the format is correct without checking domain existence or deliverability.",
    version="1.0.0"
)

# In-memory rate limiting dictionary
RATE_LIMITS = {}

class EmailRequest(BaseModel):
    """
    Pydantic model to validate incoming request body.
    """
    email: EmailStr

class EmailResponse(BaseModel):
    """
    Pydantic model to structure the response body.
    """
    valid: bool
    message: str

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Dependency to validate API key and enforce rate limits.
    """
    # Load valid API keys from environment variable every time this function is called
    API_KEYS = set(os.getenv('API_KEYS', '').split(','))
    
    if x_api_key and x_api_key in API_KEYS:
        # Valid API key provided, bypass rate limits
        return
    
    client_ip = request.client.host
    today = date.today()
    
    # Check or initialize the rate limit for the client IP
    if client_ip not in RATE_LIMITS:
        RATE_LIMITS[client_ip] = {}
    
    if today not in RATE_LIMITS[client_ip]:
        RATE_LIMITS[client_ip][today] = 0
    
    if RATE_LIMITS[client_ip][today] >= 100:
        raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
    
    # Increment the rate limit for today
    RATE_LIMITS[client_ip][today] += 1

@app.get("/", include_in_schema=False)
def root():
    """
    Redirects users to /docs.
    """
    return RedirectResponse(url="/docs")

@app.post("/validate-email", response_model=EmailResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
async def validate_email(request: EmailRequest) -> EmailResponse:
    """
    Validates whether a given email address conforms to standard email formatting rules.

    Args:
        request (EmailRequest): The incoming request body containing the email to be validated.

    Returns:
        EmailResponse: A response indicating if the email is valid and an accompanying message.
    """
    try:
        # If we reach here, Pydantic's validation has already passed.
        return EmailResponse(valid=True, message="The provided email address is valid.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)