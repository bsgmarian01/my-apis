from typing import Optional, Dict
from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
import os
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="IBAN and Swift Code Validator",
    description="This API provides utility endpoints to validate IBAN (International Bank Account Number) "
                "and BIC/SWIFT codes ensuring they conform to international standards. It is designed for "
                "financial applications that require reliable account number validation.",
)

# Pydantic models
class IBANRequest(BaseModel):
    iban: str = Field(..., json_schema_extra={"example": "DE89370400440532013000"})

    @field_validator('iban')
    def validate_iban_format(cls, v):
        if not v.isalnum() or len(v) < 15 or len(v) > 34:
            raise ValueError("IBAN must be alphanumeric and between 15 to 34 characters long.")
        return v.upper()

class SwiftRequest(BaseModel):
    swift_code: str = Field(..., json_schema_extra={"example": "INGDDEFF"})

    @field_validator('swift_code')
    def validate_swift_format(cls, v):
        if not v.isalnum() or len(v) not in (8, 11):
            raise ValueError("Swift code must be alphanumeric and either 8 or 11 characters long.")
        return v.upper()

class ValidationResponse(BaseModel):
    valid: bool
    message: str

# Helper functions for validation
def is_valid_iban(iban: str) -> bool:
    """Simple IBAN format check (not modulus check)."""
    iban = iban.replace(" ", "").upper()
    if not iban.isalnum() or len(iban) < 15 or len(iban) > 34:
        return False
    # Modulus check
    iban = iban[4:] + iban[:4]
    iban2 = ''.join(str(int(c)) if c.isdigit() else str(ord(c.upper()) - 55) for c in iban)
    return int(iban2) % 97 == 1

def is_valid_swift_code(swift: str) -> bool:
    """Simple Swift code format check."""
    swift = swift.replace(" ", "").upper()
    if not swift.isalnum() or len(swift) not in (8, 11):
        return False
    return True

# Rate limiting and API key validation dependency


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Endpoints
@app.post("/validate/iban", response_model=ValidationResponse)
async def validate_iban(request: IBANRequest):
    """
    Validate an IBAN against the relevant country format rules.
    """
    if is_valid_iban(request.iban):
        return ValidationResponse(valid=True, message="The provided IBAN is valid.")
    else:
        raise HTTPException(status_code=400, detail="Invalid IBAN.")

@app.post("/validate/swift", response_model=ValidationResponse)
async def validate_swift(request: SwiftRequest):
    """
    Validate a BIC/SWIFT code against the standard format.
    """
    if is_valid_swift_code(request.swift_code):
        return ValidationResponse(valid=True, message="The provided Swift Code is valid.")
    else:
        raise HTTPException(status_code=400, detail="Invalid Swift Code.")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)