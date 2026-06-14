from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_redirect_to_docs():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url == "http://testserver/docs"

def test_qr_config_url():
    response = client.post("/qr-config", json={"url": "https://example.com", "payload_type": "url"})
    assert response.status_code == 200
    assert "encoded_string" in response.json()
    assert "recommended_error_correction_level" in response.json()

def test_qr_config_wifi():
    response = client.post("/qr-config", json={"ssid": "MyNetwork", "password": "securePassword", "security": "WPA", "payload_type": "wifi"})
    assert response.status_code == 200
    assert "encoded_string" in response.json()
    assert "recommended_error_correction_level" in response.json()

def test_qr_config_vcard():
    response = client.post("/qr-config", json={"first_name": "John", "last_name": "Doe", "payload_type": "vcard"})
    assert response.status_code == 200
    assert "encoded_string" in response.json()
    assert "recommended_error_correction_level" in response.json()

def test_qr_config_invalid_url():
    response = client.post("/qr-config", json={"url": "", "payload_type": "url"})
    assert response.status_code == 422

def test_qr_config_invalid_wifi():
    response = client.post("/qr-config", json={"ssid": "", "password": "securePassword", "security": "WPA", "payload_type": "wifi"})
    assert response.status_code == 422

def test_qr_config_invalid_vcard():
    response = client.post("/qr-config", json={"first_name": "", "last_name": "", "payload_type": "vcard"})
    assert response.status_code == 422