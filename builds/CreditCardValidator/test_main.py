from fastapi.testclient import TestClient
from main import app, RATE_LIMITS
import os

client = TestClient(app)

def test_root_redirect():
    """
    Tests that the root endpoint redirects to /docs.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert str(response.url).endswith('/docs')

def test_validate_credit_card_valid_visa():
    """
    Tests validating a valid Visa credit card number.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "4111111111111111"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is True
    assert data['card_type'] == 'Visa'
    assert "The card number is valid and belongs to Visa." in data['message']

def test_validate_credit_card_invalid_visa():
    """
    Tests validating an invalid Visa credit card number.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "4111111111111112"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is False
    assert data['card_type'] == 'Unknown'
    assert "The card number is invalid." in data['message']

def test_validate_credit_card_non_numeric():
    """
    Tests validating a credit card number with non-numeric characters.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "4111 1111 1111 1111"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is True
    assert data['card_type'] == 'Visa'
    assert "The card number is valid and belongs to Visa." in data['message']

def test_validate_credit_card_invalid_input():
    """
    Tests validating a credit card number with non-digit characters.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "4111-1111-1111-1111"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is False
    assert data['card_type'] == 'Unknown'
    assert "Invalid input. The card number should contain only digits." in data['message']

def test_validate_credit_card_invalid_mastercard():
    """
    Tests validating an invalid MasterCard credit card number.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "5105105105105107"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is False
    assert data['card_type'] == 'Unknown'
    assert "The card number is invalid." in data['message']

def test_validate_credit_card_valid_mastercard():
    """
    Tests validating a valid MasterCard credit card number.
    """
    RATE_LIMITS.clear()
    payload = {"card_number": "5105105105105100"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is True
    assert data['card_type'] == 'MasterCard'
    assert "The card number is valid and belongs to MasterCard." in data['message']

def test_validate_credit_card_rate_limit_exceeded():
    """
    Tests that the rate limit is enforced after 100 requests without a valid API key.
    """
    RATE_LIMITS.clear()
    for _ in range(100):
        payload = {"card_number": "4111111111111111"}
        response = client.post('/validate', json=payload)
        assert response.status_code == 200
    
    payload = {"card_number": "4111111111111111"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 402
    assert "Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00" in response.json()['detail']

def test_validate_credit_card_rate_limit_bypass_with_api_key():
    """
    Tests that a valid API key bypasses the rate limit.
    """
    RATE_LIMITS.clear()
    os.environ['API_KEYS'] = 'valid-api-key'
    
    for _ in range(105):
        headers = {"X-API-Key": "valid-api-key"}
        payload = {"card_number": "4111111111111111"}
        response = client.post('/validate', json=payload, headers=headers)
        assert response.status_code == 200
    
    os.environ.pop('API_KEYS')