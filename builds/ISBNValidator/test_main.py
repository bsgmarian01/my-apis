from fastapi.testclient import TestClient
from main import app, RATE_LIMITS
import os

def test_validate_isbn_13_valid():
    RATE_LIMITS.clear()
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-13"}

def test_validate_isbn_10_valid():
    RATE_LIMITS.clear()
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "0-471-95869-7"})
    assert response.status_code == 200
    assert response.json() == {"valid": True, "message": "The provided ISBN number is valid.", "type": "ISBN-10"}

def test_validate_isbn_invalid():
    RATE_LIMITS.clear()
    client = TestClient(app)
    response = client.post("/validate-isbn", json={"isbn": "invalid-isbn"})
    assert response.status_code == 200
    assert response.json() == {"valid": False, "message": "The provided ISBN number is invalid.", "type": None}

def test_rate_limiting():
    RATE_LIMITS.clear()
    client = TestClient(app)
    
    # Make requests up to the limit
    for _ in range(100):
        response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
        assert response.status_code == 200
    
    # Exceed the rate limit
    response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
    assert response.status_code == 402
    assert response.json() == {'detail': 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'}

def test_rate_limiting_bypass_with_valid_key():
    RATE_LIMITS.clear()
    client = TestClient(app)
    os.environ['API_KEYS'] = 'valid_api_key'
    
    # Make requests up to the limit without API key
    for _ in range(100):
        response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
        assert response.status_code == 200
    
    # Exceed the rate limit without API key
    response = client.post("/validate-isbn", json={"isbn": "978-3-16-148410-0"})
    assert response.status_code == 402
    assert response.json() == {'detail': 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'}
    
    # Make requests with valid API key
    for _ in range(10):
        response = client.post("/validate-isbn", headers={"X-API-Key": "valid_api_key"}, json={"isbn": "978-3-16-148410-0"})
        assert response.status_code == 200
    
    # Exceed the rate limit with valid API key (should still work)
    for _ in range(10):
        response = client.post("/validate-isbn", headers={"X-API-Key": "valid_api_key"}, json={"isbn": "978-3-16-148410-0"})
        assert response.status_code == 200

def test_invalid_api_key():
    RATE_LIMITS.clear()
    client = TestClient(app)
    os.environ['API_KEYS'] = 'valid_api_key'
    
    # Make requests with invalid API key
    for _ in range(100):
        response = client.post("/validate-isbn", headers={"X-API-Key": "invalid_api_key"}, json={"isbn": "978-3-16-148410-0"})
        assert response.status_code == 200
    
    # Exceed the rate limit with invalid API key
    response = client.post("/validate-isbn", headers={"X-API-Key": "invalid_api_key"}, json={"isbn": "978-3-16-148410-0"})
    assert response.status_code == 402
    assert response.json() == {'detail': 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'}