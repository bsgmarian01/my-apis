from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/docs")

def test_discount_apply_no_promos():
    response = client.post("/discount-apply", json={"cart_total": 150.0, "active_promos": []})
    assert response.status_code == 200
    data = response.json()
    assert data["best_promo_applied"] == "No Promo"
    assert data["discount_amount"] == 0.0
    assert data["final_total"] == 150.0

def test_discount_apply_one_promo():
    response = client.post("/discount-apply", json={
        "cart_total": 150.0,
        "active_promos": [{"threshold": 100, "discount_pct": 10}]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["best_promo_applied"] == "No Promo"
    assert data["discount_amount"] == 15.0  # Corrected expected value
    assert data["final_total"] == 135.0  # Corrected expected value

def test_discount_apply_best_promo():
    response = client.post("/discount-apply", json={
        "cart_total": 250.0,
        "active_promos": [
            {"name": "Promo A", "threshold": 200, "discount_pct": 10},
            {"name": "Promo B", "threshold": 250, "discount_pct": 20}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["best_promo_applied"] == "Promo B"
    assert data["discount_amount"] == 50.0
    assert data["final_total"] == 200.0

def test_discount_apply_tie_breaker():
    response = client.post("/discount-apply", json={
        "cart_total": 300.0,
        "active_promos": [
            {"name": "Promo A", "threshold": 250, "discount_pct": 10},
            {"name": "Promo B", "threshold": 250, "discount_pct": 10}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["best_promo_applied"] in ["Promo A", "Promo B"]
    assert data["discount_amount"] == 30.0
    assert data["final_total"] == 270.0

def test_discount_apply_no_threshold_met():
    response = client.post("/discount-apply", json={
        "cart_total": 50.0,
        "active_promos": [
            {"name": "Promo A", "threshold": 100, "discount_pct": 10},
            {"name": "Promo B", "threshold": 200, "discount_pct": 20}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["best_promo_applied"] == "No Promo"
    assert data["discount_amount"] == 0.0
    assert data["final_total"] == 50.0