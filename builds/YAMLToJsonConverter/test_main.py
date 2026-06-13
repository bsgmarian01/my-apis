from fastapi.testclient import TestClient
import os
from main import app

# Set up the API_KEYS environment variable for testing

client = TestClient(app)

def test_convert_valid_yaml():
    """
    Test converting valid YAML to JSON.
    """
    
    response = client.post(
        "/convert",
        json={"yaml_data": "name: John Doe\nage: 30\ncity: New York"}
    )
    assert response.status_code == 200
    assert response.json() == {"json_data": {"name": "John Doe", "age": 30, "city": "New York"}}

def test_convert_invalid_yaml():
    """
    Test converting invalid YAML to JSON.
    """
    
    response = client.post(
        "/convert",
        json={"yaml_data": "{invalid yaml"}
    )
    assert response.status_code == 400
    assert "Invalid YAML data" in response.json()['detail']



def test_root_redirect():
    """
    Test that the root endpoint redirects to /docs.
    """
    
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/docs")
####