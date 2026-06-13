from fastapi.testclient import TestClient
import os
from main import app, RATE_LIMITS

client = TestClient(app)

def setup_function():
    """
    Setup function to clear the rate limit dictionary before each test.
    """
    RATE_LIMITS.clear()

def test_validate_datetime_with_valid_format():
    """
    Tests the validate-datetime endpoint with a valid date-time string and format.
    """
    response = client.post(
        '/validate-datetime',
        json={
            "datetime_string": "2023-10-05T14:30:00",
            "format": "%Y-%m-%dT%H:%M:%S"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"is_valid": True, "message": "The date-time string is valid."}

def test_validate_datetime_with_invalid_format():
    """
    Tests the validate-datetime endpoint with an invalid date-time format.
    """
    response = client.post(
        '/validate-datetime',
        json={
            "datetime_string": "2023-10-05T14:30:00",
            "format": "%Y-%m-%d %H:%M:%S"
        }
    )
    assert response.status_code == 200
    assert not response.json()["is_valid"]
    assert "does not match format" in response.json()["message"]

def test_validate_datetime_rate_limiting():
    """
    Tests the rate limiting mechanism for unauthenticated requests.
    """
    os.environ['API_KEYS'] = ''  # Ensure no API keys are available

    for _ in range(100):
        response = client.post(
            '/validate-datetime',
            json={
                "datetime_string": "2023-10-05T14:30:00",
                "format": "%Y-%m-%dT%H:%M:%S"
            }
        )
        assert response.status_code == 200

    # Attempting the 101st request should result in a rate limit error
    response = client.post(
        '/validate-datetime',
        json={
            "datetime_string": "2023-10-05T14:30:00",
            "format": "%Y-%m-%dT%H:%M:%S"
        }
    )
    assert response.status_code == 402
    assert response.json()["detail"] == 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'

def test_validate_datetime_bypass_rate_limit_with_api_key():
    """
    Tests that a valid API key bypasses the rate limit.
    """
    os.environ['API_KEYS'] = 'valid_api_key'  # Set a valid API key

    for _ in range(150):
        response = client.post(
            '/validate-datetime',
            headers={"X-API-Key": "valid_api_key"},
            json={
                "datetime_string": "2023-10-05T14:30:00",
                "format": "%Y-%m-%dT%H:%M:%S"
            }
        )
        assert response.status_code == 200