from fastapi.testclient import TestClient
import pytest
import os
from main import app

@pytest.fixture(scope="module")
def client():
    """Fixture for creating a test client for the FastAPI application."""
    return TestClient(app)

def test_convert_html_to_plain_text(client: TestClient):
    """
    Tests the /convert endpoint with valid HTML content.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    response = client.post(
        "/convert",
        json={"html_content": "<div><p>Hello, <strong>world</strong>!</p></div>"}
    )
    assert response.status_code == 200
    assert response.json() == {"plain_text": "Hello, world!"}

def test_convert_html_with_empty_string(client: TestClient):
    """
    Tests the /convert endpoint with an empty string.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    response = client.post(
        "/convert",
        json={"html_content": ""}
    )
    assert response.status_code == 200
    assert response.json() == {"plain_text": ""}

def test_convert_html_with_invalid_json(client: TestClient):
    """
    Tests the /convert endpoint with invalid JSON to ensure proper error handling.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    response = client.post(
        "/convert",
        json={"html_content_not": "<div><p>Hello, <strong>world</strong>!</p></div>"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_convert_html_with_invalid_html(client: TestClient):
    """
    Tests the /convert endpoint with invalid HTML to ensure it can still handle conversion gracefully.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    response = client.post(
        "/convert",
        json={"html_content": "<div><p>Hello, <strong>world!</p></div>"}
    )
    assert response.status_code == 200
    assert response.json() == {"plain_text": "Hello, world!"}


