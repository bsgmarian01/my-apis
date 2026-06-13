from fastapi.testclient import TestClient
from main import app
import os

def test_validate_isbn_13_valid():
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-13"}

def test_validate_isbn_10_valid():
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "0-471-95869-7"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-10"}

def test_validate_isbn_invalid():
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "invalid-isbn"})
    assert response.status_code == 200
    assert response.json() == {"valid": False, "message": "The provided ISBN number is invalid.", "type": None}



