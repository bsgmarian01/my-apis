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


@app.get("/", include_in_schema=False)
def root():
    """
    Redirects users to /docs.
    """
    return RedirectResponse(url="/docs")

@app.post("/validate-email", response_model=EmailResponse)
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