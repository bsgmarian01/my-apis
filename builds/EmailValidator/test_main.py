from fastapi.testclient import TestClient
import pytest
import os

from main import app

client = TestClient(app)

def test_validate_email_with_domain_check():
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
    response = client.post(
        "/validate",
        json={"email": "testexample.com", "check_domain": False},
    )
    assert response.status_code == 422

def test_validate_nonexistent_domain_with_check():
    response = client.post(
        "/validate",
        json={"email": "test@nonexistentdomain123xyz.com", "check_domain": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_format"] is True
    assert data.get("domain_exists") is False


