from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xmltodict

app = FastAPI(
    title="XML to JSON Converter API",
    description="This API provides a simple endpoint to convert XML data into JSON format. Ideal for developers who need to parse and manipulate XML data in applications primarily using JSON.",
)

class ConvertRequest(BaseModel):
    """Pydantic model for the request body expecting XML data."""
    xml_data: str

class ConvertResponse(BaseModel):
    """Pydantic model for the response body containing converted JSON data."""
    json_data: dict

@app.post("/convert", response_model=ConvertResponse)
async def convert_xml_to_json(request: ConvertRequest) -> ConvertResponse:
    """
    Converts XML data to JSON format.

    Args:
        request (ConvertRequest): The request object containing XML data.

    Returns:
        ConvertResponse: The response object containing the converted JSON data.

    Raises:
        HTTPException: If there is an error parsing the XML data.
    """
    try:
        json_data = xmltodict.parse(request.xml_data)
        return ConvertResponse(json_data=json_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to convert XML to JSON: {str(e)}")

