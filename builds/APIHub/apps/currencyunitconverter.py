from fastapi import FastAPI, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Currency Unit Converter",
    description="A reliable API microservice that provides conversion rates between different currency units using fixed exchange rates. Ideal for developers needing simple currency conversions within their applications without external data dependencies.",
)

# In-memory rate limiting dictionary
RATE_LIMITS = defaultdict(lambda: {'count': 0, 'last_reset': datetime.now()})

# Predefined conversion rates (fixed for demonstration purposes)
CONVERSION_RATES = {
    ("USD", "EUR"): 0.8574,
    ("EUR", "USD"): 1.1663,
    # Add more conversion rates as needed
}

class ConversionRequest(BaseModel):
    """
    Pydantic model to validate the request body for the /convert endpoint.
    
    Attributes:
        amount (float): The amount of money to convert.
        from_currency (str): The currency code to convert from.
        to_currency (str): The currency code to convert to.
    """
    amount: float
    from_currency: str
    to_currency: str

class ConversionResponse(BaseModel):
    """
    Pydantic model to define the response body for the /convert endpoint.
    
    Attributes:
        converted_amount (float): The resulting amount after conversion.
        currency_rate (float): The exchange rate used for conversion.
    """
    converted_amount: float
    currency_rate: float

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)) -> None:
    """
    FastAPI dependency to validate API key and enforce rate limiting.

    Args:
        request (Request): The incoming HTTP request.
        x_api_key (Optional[str]): The API key provided in the 'X-API-Key' header, if any.

    Raises:
        HTTPException: If the API key is invalid or the rate limit is exceeded.
    """
    valid_keys = set(os.getenv('API_KEYS', '').split(','))
    client_ip = request.client.host

    # Check for a valid API key
    if x_api_key and x_api_key in valid_keys:
        return  # Bypass rate limiting for valid API keys

    # Rate limit logic for unauthenticated requests
    current_time = datetime.now()
    reset_time = RATE_LIMITS[client_ip]['last_reset'] + timedelta(days=1)

    if current_time > reset_time:
        RATE_LIMITS[client_ip] = {'count': 0, 'last_reset': current_time}

    if RATE_LIMITS[client_ip]['count'] >= 100:
        raise HTTPException(
            status_code=402,
            detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'
        )

    RATE_LIMITS[client_ip]['count'] += 1

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """
    Redirects to the API documentation.

    Returns:
        RedirectResponse: A response that redirects the user to /docs.
    """
    return RedirectResponse(url="/docs")

@app.post("/convert", dependencies=[Depends(verify_api_key_and_rate_limit)])
def convert_currency(request_data: ConversionRequest) -> ConversionResponse:
    """
    Convert an amount from one currency to another using predefined conversion rates.

    Args:
        request_data (ConversionRequest): The data provided by the client for conversion.

    Returns:
        ConversionResponse: The result of the conversion including the converted amount and rate used.
    
    Raises:
        HTTPException: If the requested conversion rate is not available.
    """
    from_currency = request_data.from_currency.upper()
    to_currency = request_data.to_currency.upper()
    key = (from_currency, to_currency)

    if key not in CONVERSION_RATES:
        raise HTTPException(status_code=400, detail=f"Conversion rate from {from_currency} to {to_currency} is not available.")

    currency_rate = CONVERSION_RATES[key]
    converted_amount = request_data.amount * currency_rate

    return ConversionResponse(converted_amount=converted_amount, currency_rate=currency_rate)

