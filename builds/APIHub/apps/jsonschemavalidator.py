from fastapi import FastAPI, HTTPException, status, Depends, Header, Request, Response
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from typing import List, Optional
import jsonschema
import os
import time
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="JSON Schema Validator",
    description="A utility API microservice that validates JSON data against a provided JSON schema.",
    version="1.0.0"
)

RATE_LIMITS = {}

class ValidationErrorDetail(BaseModel):
    message: str

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationErrorDetail] = Field(default_factory=list)

class ValidateRequest(BaseModel):
    data: dict
    json_schema: dict  # Renamed from 'schema' to avoid shadowing

def verify_api_key_and_rate_limit(request: Request, x_api_key: Optional[str] = Header(None)):
    valid_keys = os.getenv('API_KEYS', '').split(',')
    
    if x_api_key and x_api_key in valid_keys:
        return
    
    client_ip = request.client.host
    current_time = int(time.time())
    day_start = current_time - (current_time % 86400)
    
    if client_ip not in RATE_LIMITS:
        RATE_LIMITS[client_ip] = {'count': 1, 'last_day_start': day_start}
    elif RATE_LIMITS[client_ip]['last_day_start'] != day_start:
        RATE_LIMITS[client_ip] = {'count': 1, 'last_day_start': day_start}
    else:
        if RATE_LIMITS[client_ip]['count'] >= 100:
            raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
        RATE_LIMITS[client_ip]['count'] += 1

@app.post("/validate", response_model=ValidationResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
async def validate_json(request: ValidateRequest) -> ValidationResponse:
    """
    Validates the given JSON data against the specified JSON Schema.

    Args:
        request (ValidateRequest): The request body containing data and schema.

    Returns:
        ValidationResponse: A response indicating if the validation was successful and any errors encountered.
    """
    try:
        # Check if the schema is empty
        if not request.json_schema:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Schema cannot be empty")

        jsonschema.validate(instance=request.data, schema=request.json_schema)
        return ValidationResponse(valid=True)
    except jsonschema.exceptions.SchemaError as se:
        error = ValidationErrorDetail(message=str(se))
        return ValidationResponse(valid=False, errors=[error])
    except jsonschema.exceptions.ValidationError as ve:
        error = ValidationErrorDetail(message=str(ve))
        return ValidationResponse(valid=False, errors=[error])

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

