from fastapi.testclient import TestClient
import os
from main import app

client = TestClient(app)

def setup_function():
    """
    Setup function to clear the rate limit dictionary before each test.
    """

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


