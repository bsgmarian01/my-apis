from fastapi.testclient import TestClient
import os
from main import app, MAX_REQUESTS_PER_DAY

client = TestClient(app)

def test_redirect_root_to_docs():
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/docs")

def test_validate_invalid_number_with_key():
    headers = {"X-API-Key": "test-key"}
    response = client.post("/validate/", json={"phone_number": "1234567890", "country_code": "US"}, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid phone number format"}

def test_extract_numbers_valid_with_key():
    headers = {"X-API-Key": "test-key"}
    response = client.post("/extract/", json={"phone_number": "+14155552671", "country_code": "US"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Phone numbers extracted successfully"}

def test_extract_numbers_no_numbers_with_key():
    headers = {"X-API-Key": "test-key"}
    response = client.post("/extract/", json={"phone_number": "", "country_code": "US"}, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid phone number format"}


def test_validate_valid_number_within_limit():
    for _ in range(MAX_REQUESTS_PER_DAY):
        response = client.post("/validate/", json={"phone_number": "+14155552671", "country_code": "US"})
        assert response.status_code == 200
        assert response.json() == {"message": "Phone number is valid"}

def test_validate_valid_number_with_key_bypasses_limit():
    headers = {"X-API-Key": "test-key"}
    for _ in range(MAX_REQUESTS_PER_DAY + 1):
        response = client.post("/validate/", json={"phone_number": "+14155552671", "country_code": "US"}, headers=headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Phone number is valid"}
    del os.environ['API_KEYS']