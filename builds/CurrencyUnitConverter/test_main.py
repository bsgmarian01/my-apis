from fastapi.testclient import TestClient
import os
from main import app, RATE_LIMITS

client = TestClient(app)

def test_redirect_to_docs():
    response = client.get("/")
    assert response.status_code == 200
    # Use str(response.url) to convert URL object to string for comparison
    assert str(response.url).endswith("/docs")

def test_convert_valid_conversion():
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "USD", "to_currency": "EUR"}
    )
    assert response.status_code == 200
    data = response.json()
    # Use a small tolerance for floating-point comparison
    assert abs(data["converted_amount"] - 85.74) < 1e-6
    assert data["currency_rate"] == 0.8574

def test_convert_invalid_conversion():
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "USD", "to_currency": "XYZ"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Conversion rate from USD to XYZ is not available."

def test_rate_limit_unauthenticated():
    # Clear the global RATE_LIMITS dictionary for isolation
    RATE_LIMITS.clear()

    for _ in range(100):
        response = client.post(
            "/convert",
            json={"amount": 100, "from_currency": "USD", "to_currency": "EUR"}
        )
        assert response.status_code == 200

    # Now try one more request which should exceed the rate limit
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "USD", "to_currency": "EUR"}
    )
    assert response.status_code == 402
    assert "Rate limit exceeded" in response.json()["detail"]

def test_bypass_rate_limit_with_api_key():
    # Clear the global RATE_LIMITS dictionary for isolation
    RATE_LIMITS.clear()
    
    os.environ['API_KEYS'] = 'test-key'

    for _ in range(150):  # Attempt many requests to ensure we exceed normal rate limits
        response = client.post(
            "/convert",
            json={"amount": 100, "from_currency": "USD", "to_currency": "EUR"},
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 200

    # Ensure that requests still succeed with valid API key even after exceeding rate limits
    os.environ['API_KEYS'] = ''  # Reset API keys for other tests