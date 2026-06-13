from fastapi.testclient import TestClient
import pytest
import os

from main import app, RATE_LIMITS

client = TestClient(app)

def test_validate_email_with_domain_check():
    RATE_LIMITS.clear()
    response = client.post(
        "/validate",
        json={"email": "test@example.com", "check_domain": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_format"] is True
    assert isinstance(data["domain_exists"], bool)
    assert "valid" in data["message"]

def test_validate_email_without_domain_check():
    RATE_LIMITS.clear()
    response = client.post(
        "/validate",
        json={"email": "test@example.com", "check_domain": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_format"] is True
    assert data.get("domain_exists") is None
    assert "valid" in data["message"]

def test_validate_invalid_email():
    RATE_LIMITS.clear()
    response = client.post(
        "/validate",
        json={"email": "testexample.com", "check_domain": False},
    )
    assert response.status_code == 422

def test_validate_nonexistent_domain_with_check():
    RATE_LIMITS.clear()
    response = client.post(
        "/validate",
        json={"email": "test@nonexistentdomain123xyz.com", "check_domain": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_format"] is True
    assert data.get("domain_exists") is False

def test_rate_limit_exceeded():
    RATE_LIMITS.clear()
    for _ in range(100):
        response = client.post(
            "/validate",
            json={"email": "test@example.com", "check_domain": False},
        )
        assert response.status_code == 200
    
    # Now the rate limit should be exceeded
    response = client.post(
        "/validate",
        json={"email": "test@example.com", "check_domain": False},
    )
    assert response.status_code == 402

def test_rate_limit_bypass_with_valid_api_key():
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'valid-key'
    for _ in range(105):
        response = client.post(
            "/validate",
            headers={"X-API-Key": "valid-key"},
            json={"email": "test@example.com", "check_domain": False},
        )
        assert response.status_code == 200
    os.environ['API_KEYS'] = ''