from datetime import datetime
from typing import Optional, Dict
import os
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(
    title="Date-Time Format Validator",
    description="This API allows developers to validate date-time strings against a specified format using Python's standard libraries. It ensures that the input date-time string matches the expected pattern, making it useful for data cleaning and processing tasks.",
    version="1.0.0"
)

RATE_LIMITS: Dict[str, int] = {}

class DateTimeValidationRequest(BaseModel):
    """
    Pydantic model for validating a date-time string against a specified format.
    """
    datetime_string: str
    format: str

class ValidationResponse(BaseModel):
    """
    Pydantic model for the response of the validation endpoint.
    """
    is_valid: bool
    message: str

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)) -> None:
    """
    Dependency function to verify API key and apply rate limiting based on client IP.

    Args:
        request (Request): The incoming request object.
        x_api_key (Optional[str]): The API key provided in the X-API-Key header.

    Raises:
        HTTPException: If the rate limit is exceeded and no valid API key is provided.
    """
    api_keys = os.getenv('API_KEYS', '').split(',')
    if x_api_key and x_api_key in api_keys:
        return  # Bypass rate limits for valid API keys

    client_ip = request.client.host
    current_requests = RATE_LIMITS.get(client_ip, 0)

    if current_requests >= 100:
        raise HTTPException(
            status_code=402,
            detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'
        )

    RATE_LIMITS[client_ip] = current_requests + 1

@app.get('/', include_in_schema=False)
async def root():
    """
    Redirects to the interactive API documentation.

    Returns:
        RedirectResponse: A response that redirects to /docs.
    """
    return RedirectResponse(url='/docs')

@app.post('/validate-datetime', response_model=ValidationResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
async def validate_datetime(request_data: DateTimeValidationRequest) -> ValidationResponse:
    """
    Validates a given date-time string against a specified format.

    Args:
        request_data (DateTimeValidationRequest): The request body containing the datetime_string and format.

    Returns:
        ValidationResponse: A response indicating whether the date-time string is valid.
    """
    try:
        datetime.strptime(request_data.datetime_string, request_data.format)
        return ValidationResponse(is_valid=True, message="The date-time string is valid.")
    except ValueError as e:
        return ValidationResponse(is_valid=False, message=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)