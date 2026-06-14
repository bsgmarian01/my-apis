from fastapi.testclient import TestClient
import pytest

from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}

def test_risk_ratios_success():
    data = {
        "daily_returns": [0.01, -0.02, 0.03],
        "risk_free_rate": 0.001
    }
    response = client.post("/risk-ratios", json=data)
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["sharpe_ratio"], float)
    assert isinstance(result["sortino_ratio"], float)
    assert isinstance(result["calmar_ratio"], (float, type(None)))

def test_risk_ratios_zero_volatility():
    data = {
        "daily_returns": [0.01, 0.01, 0.01],
        "risk_free_rate": 0.001
    }
    response = client.post("/risk-ratios", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": [{"loc": ["body", "daily_returns"], "msg": "Daily returns have no variation", "type": "value_error"}]}

def test_risk_ratios_empty_daily_returns():
    data = {
        "daily_returns": [],
        "risk_free_rate": 0.001
    }
    response = client.post("/risk-ratios", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": [{"loc": ["body", "daily_returns"], "msg": "daily_returns must not be empty", "type": "value_error"}]}

def test_risk_ratios_no_downside_volatility():
    data = {
        "daily_returns": [0.02, 0.03, 0.01],
        "risk_free_rate": 0.001
    }
    response = client.post("/risk-ratios", json=data)
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["sortino_ratio"], float)

def test_risk_ratios_no_drawdown():
    data = {
        "daily_returns": [0.01, 0.02, 0.03],
        "risk_free_rate": 0.001
    }
    response = client.post("/risk-ratios", json=data)
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["calmar_ratio"], type(None))