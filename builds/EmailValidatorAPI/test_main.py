from fastapi.testclient import TestClient
import pytest
import os

from main import app, RATE_LIMITS

client = TestClient(app)

@pytest.mark.parametrize("email,expected_valid,expected_message", [
    ("example@test.com", True, "The provided email address is valid."),
    ("user.name+tag+sorting@example.com", True, "The provided email address is valid."),
    ("user@sub.example.com", True, "The provided email address is valid."),
    ("plainaddress", False, "value is not a valid email address"),
    ("@missingusername.com", False, "value is not a valid email address"),
    ("username@.com", False, "value is not a valid email address"),
    ("username@example..com", False, "value is not a valid email address"),
])
def test_validate_email(email: str, expected_valid: bool, expected_message: str):
    """
    Test the /validate-email endpoint with various inputs.

    Args:
        email (str): The email to validate.
        expected_valid (bool): Whether the email should be considered valid.
        expected_message (str): The expected message in the response.
    """
    RATE_LIMITS.clear()
    response = client.post("/validate-email", json={"email": email})
    
    if expected_valid:
        assert response.status_code == 200
        assert response.json() == {"valid": expected_valid, "message": expected_message}
    else:
        assert response.status_code == 422
        assert expected_message in response.text

def test_rate_limiting():
    """
    Test rate limiting for unauthenticated requests.
    """
    RATE_LIMITS.clear()
    for _ in range(100):
        response = client.post("/validate-email", json={"email": "test@example.com"})
        assert response.status_code == 200
    
    # The next request should be rate limited
    response = client.post("/validate-email", json={"email": "test@example.com"})
    assert response.status_code == 402

def test_api_key_bypass():
    """
    Test that a valid API key bypasses rate limiting.
    """
    RATE_LIMITS.clear()
    headers = {"X-API-Key": "valid_api_key"}
    
    # Set the valid API key in the environment for testing
    os.environ['API_KEYS'] = 'valid_api_key'
    
    for _ in range(150):
        response = client.post("/validate-email", json={"email": "test@example.com"}, headers=headers)
        assert response.status_code == 200

    # Clean up the environment variable after test
    del os.environ['API_KEYS']