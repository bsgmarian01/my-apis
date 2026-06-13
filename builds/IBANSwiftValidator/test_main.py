from fastapi.testclient import TestClient
import pytest
import os

from main import app

client = TestClient(app)

def test_validate_iban_valid():
    response = client.post("/validate/iban", json={"iban": "DE89370400440532013000"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided IBAN is valid."}

def test_validate_iban_invalid():
    response = client.post("/validate/iban", json={"iban": "INVALIDIBAN"})
    assert response.status_code == 422

def test_validate_swift_valid():
    response = client.post("/validate/swift", json={"swift_code": "INGDDEFF"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided Swift Code is valid."}

def test_validate_swift_invalid():
    response = client.post("/validate/swift", json={"swift_code": "INVALIDSWIFT"})
    assert response.status_code == 422

def test_validate_iban_format():
    response = client.post("/validate/iban", json={"iban": "123456789"})
    assert response.status_code == 422

def test_validate_swift_format():
    response = client.post("/validate/swift", json={"swift_code": "12345"})
    assert response.status_code == 422


