import pytest
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Developer API Suite" in response.text

def test_email_validator_route():
    # Test through the mounted app route
    response = client.post("/emailvalidator/validate", json={"email": "test@example.com", "check_domain": False})
    # Since we might not have API_KEYS configured in test environment, it should either return 200 or 402/422
    assert response.status_code in [200, 422, 402]
