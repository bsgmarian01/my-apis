from fastapi import FastAPI, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Currency Unit Converter",
    description="A reliable API microservice that provides conversion rates between different currency units using fixed exchange rates. Ideal for developers needing simple currency conversions within their applications without external data dependencies.",
)

# In-memory rate limiting dictionary

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


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """
    Redirects to the API documentation.

    Returns:
        RedirectResponse: A response that redirects the user to /docs.
    """
    return RedirectResponse(url="/docs")

@app.post("/convert")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)