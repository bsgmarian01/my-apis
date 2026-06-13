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


class ConvertRequest(BaseModel):
    """Pydantic model representing the request body for the convert endpoint."""
    html_content: str

class ConvertResponse(BaseModel):
    """Pydantic model representing the response body for the convert endpoint."""
    plain_text: str



@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/convert", response_model=ConvertResponse, summary="Converts provided HTML content into plain text.")
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

