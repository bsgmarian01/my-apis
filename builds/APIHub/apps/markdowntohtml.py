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
DAILY_LIMIT = 100


class MarkdownRequest(BaseModel):
    markdown_text: str

# Endpoint to convert Markdown to HTML
@app.post("/convert", summary="Converts Markdown text to HTML")
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