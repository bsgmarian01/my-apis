from fastapi.testclient import TestClient
import os
from main import app, RATE_LIMITS

client = TestClient(app)

def test_extract_value():
    """
    Tests the /extract endpoint with valid JSON data and key path.
    """
    response = client.post("/extract", json={"json_data": '{"user":{"profile":{"name":"John Doe","age":30}}}', "key_path": "user.profile.name"})
    assert response.status_code == 200
    assert response.json() == {"value": "John Doe", "status": "success"}

def test_extract_invalid_key_path():
    """
    Tests the /extract endpoint with an invalid key path.
    """
    response = client.post("/extract", json={"json_data": '{"user":{"profile":{"name":"John Doe","age":30}}}', "key_path": "invalid.path"})
    assert response.status_code == 200
    assert response.json() == {"value": None, "status": "Key path not found"}

def test_extract_invalid_json():
    """
    Tests the /extract endpoint with invalid JSON data.
    """
    response = client.post("/extract", json={"json_data": '{invalid:json}', "key_path": "user.profile.name"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON data provided"}

def test_rate_limiting():
    """
    Tests the rate limiting functionality without a valid API key.
    """
    RATE_LIMITS.clear()
    
    for _ in range(100):
        response = client.post("/extract", json={"json_data": '{"user":{"profile":{"name":"John Doe","age":30}}}', "key_path": "user.profile.name"})
        assert response.status_code == 200
    
    # Exceeding the limit
    response = client.post("/extract", json={"json_data": '{"user":{"profile":{"name":"John Doe","age":30}}}', "key_path": "user.profile.name"})
    assert response.status_code == 402

def test_bypass_rate_limit_with_api_key():
    """
    Tests that a valid API key bypasses the rate limit.
    """
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'valid-api-key'
    
    for _ in range(150):
        response = client.post("/extract", headers={"X-API-Key": "valid-api-key"}, json={"json_data": '{"user":{"profile":{"name":"John Doe","age":30}}}', "key_path": "user.profile.name"})
        assert response.status_code == 200