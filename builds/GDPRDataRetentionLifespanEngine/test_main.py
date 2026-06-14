# test_main.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app, follow_redirects=False)

def test_root_redirects_to_docs():
    response = client.get("/")
    assert response.status_code == 307  # Correct status code for redirect
    assert response.headers["Location"] == "/docs"  # Correct header key for location

def test_evaluate_marketing_within_retention_period():
    response = client.post("/evaluate", json={
        "data_category": "marketing",
        "creation_date": "2023-01-01",
        "current_date": "2023-06-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["retention_years"] == 3
    assert data["days_remaining"] > 0
    assert not data["cleanup_flag"]

def test_evaluate_marketing_past_retention_period():
    response = client.post("/evaluate", json={
        "data_category": "marketing",
        "creation_date": "2019-01-01",
        "current_date": "2023-06-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["retention_years"] == 3
    assert data["days_remaining"] == 0
    assert data["cleanup_flag"]

def test_evaluate_financial_within_retention_period():
    response = client.post("/evaluate", json={
        "data_category": "financial",
        "creation_date": "2023-01-01",
        "current_date": "2024-06-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["retention_years"] == 7
    assert data["days_remaining"] > 0
    assert not data["cleanup_flag"]

def test_evaluate_financial_past_retention_period():
    response = client.post("/evaluate", json={
        "data_category": "financial",
        "creation_date": "2015-01-01",
        "current_date": "2023-06-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["retention_years"] == 7
    assert data["days_remaining"] == 0
    assert data["cleanup_flag"]

def test_evaluate_invalid_date_format():
    response = client.post("/evaluate", json={
        "data_category": "marketing",
        "creation_date": "2023-13-01",
        "current_date": "2023-06-01"
    })
    assert response.status_code == 400

def test_evaluate_invalid_data_category():
    response = client.post("/evaluate", json={
        "data_category": "invalid",
        "creation_date": "2023-01-01",
        "current_date": "2023-06-01"
    })
    assert response.status_code == 400