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


class ValidationErrorDetail(BaseModel):
    message: str

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationErrorDetail] = Field(default_factory=list)

class ValidateRequest(BaseModel):
    data: dict
    json_schema: dict  # Renamed from 'schema' to avoid shadowing


@app.post("/validate", response_model=ValidationResponse)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)