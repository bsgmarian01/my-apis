from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "200 OK"}

def test_optimize_retry_endpoint():
    payload = {
        'failed_date': '2023-10-01',
        'failure_reason': 'insufficient_funds',
        'customer_timezone': -5,
        'amount': 100.0
    }
    
    response = client.post("/optimize-retry", json=payload)
    assert response.status_code == 200
    assert "optimal_retry_date" in response.json()
    assert "action_channel" in response.json()
    assert "urgency_score" in response.json()

def test_optimize_retry_endpoint_with_expired_card():
    payload = {
        'failed_date': '2023-10-01',
        'failure_reason': 'expired_card',
        'customer_timezone': -5,
        'amount': 100.0
    }
    
    response = client.post("/optimize-retry", json=payload)
    assert response.status_code == 200
    assert response.json()["action_channel"] == "delayed_retry"
    assert response.json()["urgency_score"] == 4

def test_optimize_retry_endpoint_with_other_reason():
    payload = {
        'failed_date': '2023-10-01',
        'failure_reason': 'other_reason',
        'customer_timezone': -5,
        'amount': 100.0
    }
    
    response = client.post("/optimize-retry", json=payload)
    assert response.status_code == 200
    assert response.json()["action_channel"] == "email_update_form"
    assert response.json()["urgency_score"] == 2