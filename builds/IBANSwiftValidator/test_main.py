from fastapi.testclient import TestClient
import pytest
import os

from main import app, RATE_LIMITS

client = TestClient(app)

def test_validate_iban_valid():
    RATE_LIMITS.clear()
    response = client.post("/validate/iban", json={"iban": "DE89370400440532013000"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided IBAN is valid."}

def test_validate_iban_invalid():
    RATE_LIMITS.clear()
    response = client.post("/validate/iban", json={"iban": "INVALIDIBAN"})
    assert response.status_code == 422

def test_validate_swift_valid():
    RATE_LIMITS.clear()
    response = client.post("/validate/swift", json={"swift_code": "INGDDEFF"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided Swift Code is valid."}

def test_validate_swift_invalid():
    RATE_LIMITS.clear()
    response = client.post("/validate/swift", json={"swift_code": "INVALIDSWIFT"})
    assert response.status_code == 422

def test_validate_iban_format():
    RATE_LIMITS.clear()
    response = client.post("/validate/iban", json={"iban": "123456789"})
    assert response.status_code == 422

def test_validate_swift_format():
    RATE_LIMITS.clear()
    response = client.post("/validate/swift", json={"swift_code": "12345"})
    assert response.status_code == 422

def test_rate_limiting_exceeded():
    RATE_LIMITS.clear()
    for _ in range(101):
        response = client.post("/validate/iban", json={"iban": "DE89370400440532013000"})
    assert response.status_code == 402

def test_valid_api_key_bypasses_rate_limit():
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'testkey'
    headers = {'X-API-Key': 'testkey'}
    for _ in range(150):
        response = client.post("/validate/iban", json={"iban": "DE89370400440532013000"}, headers=headers)
        assert response.status_code == 200