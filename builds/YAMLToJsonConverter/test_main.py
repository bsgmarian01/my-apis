from fastapi.testclient import TestClient
import os
from main import app, RATE_LIMITS

# Set up the API_KEYS environment variable for testing
os.environ['API_KEYS'] = "valid_api_key"

client = TestClient(app)

def test_convert_valid_yaml():
    """
    Test converting valid YAML to JSON.
    """
    RATE_LIMITS.clear()
    
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
    RATE_LIMITS.clear()
    
    response = client.post(
        "/convert",
        json={"yaml_data": "{invalid yaml"}
    )
    assert response.status_code == 400
    assert "Invalid YAML data" in response.json()['detail']

def test_rate_limit_exceeded():
    """
    Test rate limit exceeded for unauthenticated requests.
    """
    RATE_LIMITS.clear()
    
    # Simulate 100 requests to exceed the daily limit
    for _ in range(100):
        client.post(
            "/convert",
            json={"yaml_data": "name: John Doe\nage: 30\ncity: New York"}
        )
    
    # This request should fail due to rate limiting
    response = client.post(
        "/convert",
        json={"yaml_data": "name: John Doe\nage: 30\ncity: New York"}
    )
    assert response.status_code == 402
    assert response.json()['detail'] == 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'

def test_bypass_rate_limit_with_api_key():
    """
    Test that a valid API key bypasses rate limiting.
    """
    RATE_LIMITS.clear()
    
    # Simulate 100 requests to exceed the daily limit
    for _ in range(100):
        client.post(
            "/convert",
            json={"yaml_data": "name: John Doe\nage: 30\ncity: New York"}
        )
    
    # This request should succeed due to the valid API key
    response = client.post(
        "/convert",
        headers={"X-API-Key": "valid_api_key"},
        json={"yaml_data": "name: John Doe\nage: 30\ncity: New York"}
    )
    assert response.status_code == 200
    assert response.json() == {"json_data": {"name": "John Doe", "age": 30, "city": "New York"}}

def test_root_redirect():
    """
    Test that the root endpoint redirects to /docs.
    """
    RATE_LIMITS.clear()
    
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/docs")
####