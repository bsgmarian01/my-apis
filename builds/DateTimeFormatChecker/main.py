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


@app.get('/', include_in_schema=False)
async def root():
    """
    Redirects to the interactive API documentation.

    Returns:
        RedirectResponse: A response that redirects to /docs.
    """
    return RedirectResponse(url='/docs')

@app.post('/validate-datetime', response_model=ValidationResponse)
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