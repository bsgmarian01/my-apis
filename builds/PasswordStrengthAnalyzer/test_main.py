from fastapi.testclient import TestClient
import os
from main import app, RATE_LIMITS

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url == "http://testserver/docs"

def test_analyze_password_no_key_within_limit():
    RATE_LIMITS.clear()
    
    for _ in range(100):
        response = client.post("/analyze", json={"password": "P@ssw0rd123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["strength_score"], int)
        assert isinstance(data["feedback"], list)

    # Test rate limit exceed
    response = client.post("/analyze", json={"password": "P@ssw0rd123"})
    assert response.status_code == 402
    assert response.json()["detail"] == 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'

def test_analyze_password_with_valid_key():
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'testkey'
    
    response = client.post("/analyze", json={"password": "P@ssw0rd123"}, headers={"X-API-Key": "testkey"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["strength_score"], int)
    assert isinstance(data["feedback"], list)

def test_analyze_password_invalid_key():
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'validkey'
    
    for _ in range(100):
        response = client.post("/analyze", json={"password": "P@ssw0rd123"}, headers={"X-API-Key": "invalidkey"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["strength_score"], int)
        assert isinstance(data["feedback"], list)

    # Test rate limit exceed
    response = client.post("/analyze", json={"password": "P@ssw0rd123"}, headers={"X-API-Key": "invalidkey"})
    assert response.status_code == 402
    assert response.json()["detail"] == 'Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00'

def test_analyze_password_no_key_zero_length():
    RATE_LIMITS.clear()
    
    response = client.post("/analyze", json={"password": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["strength_score"] == 20
    assert "Your password is too short. Consider using at least 8 characters." in data["feedback"]

def test_analyze_password_no_key_perfect_length():
    RATE_LIMITS.clear()
    
    response = client.post("/analyze", json={"password": "P@ssw0rd"})
    assert response.status_code == 200
    data = response.json()
    assert data["strength_score"] >= 70

def test_analyze_password_no_key_with_common_pattern():
    RATE_LIMITS.clear()
    
    response = client.post("/analyze", json={"password": "P@ssw0rdpassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["strength_score"] <= 80
    assert "Avoid using easily guessable patterns like 'password'." in data["feedback"]