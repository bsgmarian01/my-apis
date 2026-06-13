from fastapi.testclient import TestClient
import pytest

from main import app

@pytest.fixture(scope="module")
def client():
    """
    Fixture to create a test client for the FastAPI application.
    """
    return TestClient(app)

def test_convert_valid_xml(client):
    """
    Tests converting valid XML data to JSON.
    """
    response = client.post("/convert", json={"xml_data": "<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don't forget me this weekend!</body></note>"})
    assert response.status_code == 200
    assert response.json() == {"json_data": {'note': {'to': 'Tove', 'from': 'Jani', 'heading': 'Reminder', 'body': "Don't forget me this weekend!"}}}

def test_convert_invalid_xml(client):
    """
    Tests converting invalid XML data to JSON.
    """
    response = client.post("/convert", json={"xml_data": "<invalid><tag>"})
    assert response.status_code == 400
    assert "Failed to convert XML to JSON" in response.json()["detail"]

def test_convert_empty_xml(client):
    """
    Tests converting empty XML data to JSON.
    """
    response = client.post("/convert", json={"xml_data": ""})
    assert response.status_code == 400
    assert "Failed to convert XML to JSON" in response.json()["detail"]

def test_convert_missing_xml_field(client):
    """
    Tests posting a request without the 'xml_data' field.
    """
    response = client.post("/convert", json={})
    assert response.status_code == 422

def test_convert_non_string_xml(client):
    """
    Tests converting XML data that is not a string to JSON.
    """
    response = client.post("/convert", json={"xml_data": 12345})
    assert response.status_code == 422