from fastapi.testclient import TestClient
from main import app
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
    payload = {"card_number": "5105105105105100"}
    response = client.post('/validate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_valid'] is True
    assert data['card_type'] == 'MasterCard'
    assert "The card number is valid and belongs to MasterCard." in data['message']


