from fastapi import FastAPI, Request, Header, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import os
import yaml
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(
    title="YAML to JSON Converter",
    description="This API provides a simple utility for converting YAML formatted data into JSON format. It is useful for developers who need to integrate or migrate data between systems that use different data serialization standards.",
    version="1.0.0"
)

# In-memory rate limiting dictionary


class ConvertRequest(BaseModel):
    yaml_data: str

# Pydantic model for response body
class ConvertResponse(BaseModel):
    json_data: dict

@app.get("/", include_in_schema=False)
def root():
    """
    Root endpoint that redirects to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")

@app.post("/convert", response_model=ConvertResponse)
def convert_yaml_to_json(request: ConvertRequest):
    """
    Converts YAML formatted text into JSON format.
    
    Parameters:
    - request (ConvertRequest): The request body containing the YAML data.
    
    Returns:
    - ConvertResponse: A response object containing the converted JSON data.
    """
    try:
        # Parse YAML data
        json_data = yaml.safe_load(request.yaml_data)
        
        return ConvertResponse(json_data=json_data)
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML data: {str(e)}"
        )

