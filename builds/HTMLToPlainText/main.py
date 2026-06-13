from typing import Any, Dict, Optional
import os
import datetime
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="HTML to Plain Text Converter",
    description=(
        "This API microservice provides a simple utility for converting HTML content into plain text. "
        "It uses BeautifulSoup4 under the hood to parse HTML and extract text, making it suitable for web scraping or content extraction tasks."
    ),
)

RATE_LIMITS = {}

class ConvertRequest(BaseModel):
    """Pydantic model representing the request body for the convert endpoint."""
    html_content: str

class ConvertResponse(BaseModel):
    """Pydantic model representing the response body for the convert endpoint."""
    plain_text: str


def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    valid_api_keys = set(os.getenv('API_KEYS', '').split(','))
    
    if x_api_key and x_api_key in valid_api_keys:
        return  # Bypass rate limits for valid API keys

    client_ip = request.client.host
    current_time = datetime.datetime.utcnow()
    today_start = datetime.datetime.combine(current_time.date(), datetime.time.min)

    if client_ip not in RATE_LIMITS:
        RATE_LIMITS[client_ip] = {'count': 1, 'last_reset': today_start}
    else:
        if (current_time - RATE_LIMITS[client_ip]['last_reset']).days > 0:
            # Reset the count if it's a new day
            RATE_LIMITS[client_ip] = {'count': 1, 'last_reset': current_time}
        else:
            RATE_LIMITS[client_ip]['count'] += 1

    if RATE_LIMITS[client_ip]['count'] > 100:
        raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/convert", response_model=ConvertResponse, summary="Converts provided HTML content into plain text.", dependencies=[Depends(verify_api_key_and_rate_limit)])
async def convert_html_to_plain_text(request_body: ConvertRequest) -> Dict[str, Any]:
    """
    Converts the HTML content in the request body to plain text using BeautifulSoup.
    
    Args:
        request_body (ConvertRequest): The request containing HTML content.

    Returns:
        Dict[str, Any]: A dictionary with the key 'plain_text' and value as the extracted plain text from HTML.
        
    Raises:
        HTTPException: If there is an issue processing the HTML content.
    """
    try:
        soup = BeautifulSoup(request_body.html_content, 'html.parser')
        return {"plain_text": soup.get_text()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while converting HTML to plain text: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)