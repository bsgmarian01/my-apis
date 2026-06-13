import os
from typing import Optional, Dict
from fastapi import FastAPI, Request, Header, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import markdown2

app = FastAPI(title="Markdown to HTML Converter",
              description="This API microservice converts Markdown formatted text into clean and semantic HTML. Ideal for developers who need to render user-generated content from a simple text format into rich web pages or documentation.",
              version="1.0.0")

# In-memory rate limit storage
RATE_LIMITS: Dict[str, int] = {}
DAILY_LIMIT = 100

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Verify the API key provided in the X-API-Key header and apply rate limiting if no valid API key is present.
    
    If a valid API key is provided, bypass rate limits. Otherwise, enforce rate limits based on client IP.
    """
    # Load valid API keys from environment dynamically
    VALID_API_KEYS = set(os.getenv('API_KEYS', '').split(','))
    
    ip = request.client.host
    
    current_time = datetime.now()
    
    # Clear outdated entries from the rate limit dictionary
    keys_to_remove = [k for k, (count, last_checked) in RATE_LIMITS.items() 
                      if (current_time - last_checked).days >= 1]
            
    for key in keys_to_remove:
        del RATE_LIMITS[key]
    
    # Check API key validity
    if x_api_key and x_api_key in VALID_API_KEYS:
        return
    
    # Update or initialize IP count and last checked time
    if ip not in RATE_LIMITS:
        RATE_LIMITS[ip] = (1, current_time)
    else:
        count, last_checked = RATE_LIMITS[ip]
        RATE_LIMITS[ip] = (count + 1, current_time)

    # Check rate limit if the API key is invalid
    if ip in RATE_LIMITS and RATE_LIMITS[ip][0] >= DAILY_LIMIT:
        raise HTTPException(
            status_code=402,
            detail="Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00"
        )

# Pydantic model for request body
class MarkdownRequest(BaseModel):
    markdown_text: str

# Endpoint to convert Markdown to HTML
@app.post("/convert", summary="Converts Markdown text to HTML", dependencies=[Depends(verify_api_key_and_rate_limit)])
async def convert_markdown_to_html(markdown_request: MarkdownRequest):
    """
    Converts the provided Markdown formatted text into HTML.
    
    Parameters:
    - markdown_request (MarkdownRequest): The request body containing the Markdown text.
    
    Returns:
    - A JSON response with the converted HTML output.
    """
    try:
        html_output = markdown2.markdown(markdown_request.markdown_text)
        return {"html_output": html_output}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Root endpoint to redirect to /docs
@app.get("/", include_in_schema=False)
def root():
    """
    Redirects the user from the root URL to the API documentation.
    
    Returns:
    - A RedirectResponse to /docs.
    """
    return RedirectResponse(url="/docs")