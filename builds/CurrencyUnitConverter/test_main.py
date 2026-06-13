from fastapi.testclient import TestClient
import os
from main import app

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


