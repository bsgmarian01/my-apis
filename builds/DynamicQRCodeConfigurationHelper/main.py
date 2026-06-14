from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import RedirectResponse, JSONResponse
from enum import Enum
from urllib.parse import quote
import base64
from pydantic import BaseModel, field_validator

app = FastAPI(title="Dynamic QR Code Configuration Helper", description="A stateless API for QR payloads.")

class PayloadType(str, Enum):
    url = "url"
    wifi = "wifi"
    vcard = "vcard"

class URLData(BaseModel):
    url: str
    payload_type: PayloadType

    @field_validator('url')
    def validate_url(cls, value):
        if not value:
            raise ValueError("URL cannot be empty")
        return value

class WiFiData(BaseModel):
    ssid: str
    password: str
    security: str = 'WPA'
    payload_type: PayloadType

    @field_validator('ssid')
    def validate_ssid(cls, value):
        if not value:
            raise ValueError("SSID cannot be empty")
        return value

class VCardData(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    payload_type: PayloadType

    @field_validator('first_name', 'last_name')
    def validate_names(cls, value):
        if not value:
            raise ValueError("First and last names cannot be empty")
        return value

def encode_url(data: URLData) -> str:
    return quote(data.url)

def encode_wifi(data: WiFiData) -> str:
    security = data.security.upper()
    return f"WIFI:S:{data.ssid};T:{security};P:{data.password};"

def encode_vcard(data: VCardData) -> str:
    vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data.first_name} {data.last_name}\n"
    if data.email:
        vcard += f"EMAIL;TYPE=INTERNET:{data.email}\n"
    if data.phone:
        vcard += f"TEL;TYPE=CELL:{data.phone}\n"
    vcard += "END:VCARD"
    return quote(vcard)

def determine_error_correction_level(payload_type: PayloadType) -> str:
    if payload_type == PayloadType.url:
        return 'M'
    elif payload_type == PayloadType.wifi:
        return 'Q'
    elif payload_type == PayloadType.vcard:
        return 'H'
    else:
        raise ValueError("Unsupported payload type.")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/qr-config")
async def qr_config(data: URLData | WiFiData | VCardData = Body(...)):
    try:
        if data.payload_type == PayloadType.url:
            encoded_string = encode_url(data)
        elif data.payload_type == PayloadType.wifi:
            encoded_string = encode_wifi(data)
        elif data.payload_type == PayloadType.vcard:
            encoded_string = encode_vcard(data)
        else:
            raise ValueError("Unsupported payload type.")
        
        recommended_error_correction_level = determine_error_correction_level(data.payload_type)
        return JSONResponse(content={
            "encoded_string": base64.urlsafe_b64encode(encoded_string.encode()).decode(),
            "recommended_error_correction_level": recommended_error_correction_level
        })
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))