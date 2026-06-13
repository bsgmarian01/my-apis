from typing import Optional, Dict
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import RedirectResponse
import dns.resolver
import os
from datetime import datetime, timedelta

app = FastAPI(
    title="Email Address Validator",
    description=(
        "A simple utility service that validates email addresses for format correctness "
        "and domain existence using standard Python libraries, ensuring reliable checks without external dependencies."
    ),
)

class EmailValidationRequest(BaseModel):
    """
    Pydantic model for the request body of the /validate endpoint.
    
    Attributes:
        email (EmailStr): The email address to be validated.
        check_domain (bool): Whether to perform a DNS domain existence check.
    """
    email: EmailStr
    check_domain: Optional[bool] = False

class EmailValidationResponse(BaseModel):
    """
    Pydantic model for the response body of the /validate endpoint.
    
    Attributes:
        is_valid_format (bool): Indicates if the email format is valid.
        domain_exists (bool): Indicates if the domain exists (only relevant when check_domain is True).
        message (str): A human-readable message summarizing the validation results.
    """
    is_valid_format: bool
    domain_exists: Optional[bool]
    message: str

# In-memory rate limit storage
RATE_LIMITS = {}

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    valid_api_keys = os.getenv('API_KEYS', '').split(',')
    
    if x_api_key and x_api_key in valid_api_keys:
        # Bypass rate limits for valid API keys
        return
    
    client_ip = request.client.host
    current_time = datetime.now()
    
    if client_ip not in RATE_LIMITS:
        RATE_LIMITS[client_ip] = []
    
    # Remove outdated timestamps (more than 24 hours old)
    RATE_LIMITS[client_ip] = [timestamp for timestamp in RATE_LIMITS[client_ip] if current_time - timestamp < timedelta(days=1)]
    
    if len(RATE_LIMITS[client_ip]) >= 100:
        raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
    
    # Record the current request
    RATE_LIMITS[client_ip].append(current_time)

def domain_exists(domain: str) -> bool:
    """
    Checks if a given domain has MX records, indicating it can receive emails.
    
    Args:
        domain (str): The domain to check.
        
    Returns:
        bool: True if the domain has MX records, False otherwise.
    """
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/validate", response_model=EmailValidationResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
def validate_email(request: EmailValidationRequest) -> Dict[str, bool]:
    """
    Validates an email address for proper formatting and optional DNS domain existence check.
    
    Args:
        request (EmailValidationRequest): The request body containing the email to be validated and a flag indicating whether to check the domain.
        
    Returns:
        EmailValidationResponse: A response object with validation results.
    """
    is_valid_format = True
    domain_exists_result = None
    
    if request.check_domain:
        try:
            domain_part = request.email.split('@')[1]
            domain_exists_result = domain_exists(domain_part)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error checking domain: {str(e)}")
    
    message_parts = []
    if is_valid_format:
        message_parts.append("The email address is valid.")
    if request.check_domain and domain_exists_result is not None:
        if domain_exists_result:
            message_parts.append("The domain exists.")
        else:
            message_parts.append("The domain does not exist.")
    
    return {
        "is_valid_format": is_valid_format,
        "domain_exists": domain_exists_result,
        "message": ' '.join(message_parts)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)