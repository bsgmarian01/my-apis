from fastapi.testclient import TestClient
import pytest

from main import app

client = TestClient(app)

def test_redirect_to_docs():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url == "http://testserver/docs"

def test_get_league_logo_found():
    response = client.get("/league-logos/12345")
    assert response.status_code == 200
    assert response.json() == {"name": "The International 2022", "logo_url": "https://example.com/ti2022.png"}

def test_get_league_logo_not_found():
    response = client.get("/league-logos/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "League with ID 99999 not found."}