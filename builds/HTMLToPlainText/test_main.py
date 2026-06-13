from fastapi.testclient import TestClient
import pytest
import os
from main import app, RATE_LIMITS

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
    RATE_LIMITS.clear()
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
    RATE_LIMITS.clear()
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
    RATE_LIMITS.clear()
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
    RATE_LIMITS.clear()
    response = client.post(
        "/convert",
        json={"html_content": "<div><p>Hello, <strong>world!</p></div>"}
    )
    assert response.status_code == 200
    assert response.json() == {"plain_text": "Hello, world!"}

def test_rate_limit_exceeded(client: TestClient):
    """
    Tests the rate limit exceeding scenario.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    RATE_LIMITS.clear()
    for _ in range(100):
        response = client.post(
            "/convert",
            json={"html_content": "<div><p>Hello, <strong>world</strong>!</p></div>"}
        )
        assert response.status_code == 200
    
    response = client.post(
        "/convert",
        json={"html_content": "<div><p>Hello, <strong>world</strong>!</p></div>"}
    )
    assert response.status_code == 402

def test_api_key_bypasses_rate_limit(client: TestClient):
    """
    Tests that a valid API key bypasses the rate limit.
    
    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'valid-api-key'
    for _ in range(150):
        response = client.post(
            "/convert",
            json={"html_content": "<div><p>Hello, <strong>world</strong>!</p></div>"},
            headers={'X-API-Key': 'valid-api-key'}
        )
        assert response.status_code == 200