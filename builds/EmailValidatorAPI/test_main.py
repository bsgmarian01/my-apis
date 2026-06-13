from fastapi.testclient import TestClient
import pytest
import os

from main import app

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
    response = client.post("/validate-email", json={"email": email})
    
    if expected_valid:
        assert response.status_code == 200
        assert response.json() == {"valid": expected_valid, "message": expected_message}
    else:
        assert response.status_code == 422
        assert expected_message in response.text


