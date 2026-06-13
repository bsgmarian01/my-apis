from fastapi import FastAPI, Request, Header, Depends, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import RedirectResponse
from typing import Optional
import time

app = FastAPI()

MAX_REQUESTS_PER_DAY = 100

class PhoneNumber(BaseModel):
    phone_number: str
    country_code: str


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.post("/validate/")
def validate_phone_number(phone_data: PhoneNumber):
    # Validate phone number logic here
    if not phone_data.phone_number.startswith("+"):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return {"message": "Phone number is valid"}

@app.post("/extract/")
def extract_phone_numbers(phone_data: PhoneNumber):
    # Extract phone numbers logic here
    if not phone_data.phone_number.startswith("+"):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return {"message": "Phone numbers extracted successfully"}