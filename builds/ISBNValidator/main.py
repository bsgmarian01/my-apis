from datetime import date
from typing import Optional, Dict
import os
from fastapi import FastAPI, Request, Header, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(
    title="ISBN Validator",
    description="A simple utility API that validates the format and checksum of ISBN-10 and ISBN-13 numbers.",
)

# In-memory rate limiting dictionary
RATE_LIMITS: Dict[str, int] = {}

class ISBNValidationRequest(BaseModel):
    isbn: str

class ISBNValidationResponse(BaseModel):
    valid: bool
    message: str
    type: Optional[str] = None  # Make the 'type' field optional and default it to None

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Dependency function to verify API key and enforce rate limiting.
    
    Args:
        request (Request): The incoming request object.
        x_api_key (Optional[str]): The API key provided in the X-API-Key header.
        
    Raises:
        HTTPException: If the API key is invalid or if the rate limit is exceeded.
    """
    valid_api_keys = set(os.getenv('API_KEYS', '').split(','))
    
    if x_api_key and x_api_key in valid_api_keys:
        return
    
    client_ip = request.client.host
    today = date.today()
    
    if (client_ip, today) not in RATE_LIMITS:
        RATE_LIMITS[(client_ip, today)] = 0
        
    if RATE_LIMITS[(client_ip, today)] >= 100:
        raise HTTPException(
            status_code=402,
            detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'
        )
        
    RATE_LIMITS[(client_ip, today)] += 1

def is_valid_isbn_10(isbn: str) -> bool:
    """
    Validates an ISBN-10 number.
    
    Args:
        isbn (str): The ISBN-10 number to validate.
        
    Returns:
        bool: True if the ISBN-10 is valid, False otherwise.
    """
    isbn = isbn.replace('-', '')
    if len(isbn) != 10 or not isbn[:-1].isdigit() or (isbn[-1] not in '0123456789X'):
        return False
    
    total = sum((i + 1) * int(x) for i, x in enumerate(isbn[:9]))
    
    if isbn[-1] == 'X':
        total += 10 * 10
    else:
        total += 10 * int(isbn[-1])
        
    return total % 11 == 0

def is_valid_isbn_13(isbn: str) -> bool:
    """
    Validates an ISBN-13 number.
    
    Args:
        isbn (str): The ISBN-13 number to validate.
        
    Returns:
        bool: True if the ISBN-13 is valid, False otherwise.
    """
    isbn = isbn.replace('-', '')
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    
    total = sum(int(x) * (3 if i % 2 else 1) for i, x in enumerate(isbn[:-1]))
    
    check_digit = (10 - (total % 10)) % 10
    return int(isbn[-1]) == check_digit

@app.post("/validate-isbn", response_model=ISBNValidationResponse)
def validate_isbn(request: Request, isbn_data: ISBNValidationRequest, _: None = Depends(verify_api_key_and_rate_limit)):
    """
    Validates an ISBN number to ensure it is correctly formatted and the checksum is valid.
    
    Args:
        request (Request): The incoming request object.
        isbn_data (ISBNValidationRequest): The ISBN data provided in the request body.
        
    Returns:
        ISBNValidationResponse: A response indicating whether the ISBN is valid, a message, and optionally the type of ISBN.
    """
    isbn = isbn_data.isbn
    if is_valid_isbn_10(isbn):
        return {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-10"}
    
    elif is_valid_isbn_13(isbn):
        return {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-13"}
    
    else:
        return {"valid": False, "message": "The provided ISBN number is invalid."}

@app.get("/", include_in_schema=False)
def root():
    """
    Redirects to the interactive API documentation.
    
    Returns:
        RedirectResponse: A redirect response to the /docs path.
    """
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)