import os
from fastapi.testclient import TestClient
import pytest

# Mock the environment variable for API keys
os.environ['API_KEYS'] = 'valid_api_key'

from main import app, RATE_LIMITS

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rate_limits():
    """
    Clear the in-memory rate limit storage before each test to ensure tests do not interfere with one another.
    """
    global RATE_LIMITS
    RATE_LIMITS.clear()

def test_convert_markdown_with_api_key():
    response = client.post("/convert", headers={"X-API-Key": "valid_api_key"}, json={"markdown_text": "# Test\nThis is a test."})
    assert response.status_code == 200
    html_output = response.json().get("html_output").replace('\n', '').strip()
    expected_html = "<h1>Test</h1><p>This is a test.</p>".strip()
    assert html_output == expected_html

def test_convert_markdown_without_api_key():
    response = client.post("/convert", json={"markdown_text": "# Test\nThis is a test."})
    assert response.status_code == 200
    # Rate limiting logic should be tested in a separate test case (test_rate_limiting)

def test_convert_markdown_with_invalid_api_key():
    response = client.post("/convert", headers={"X-API-Key": "invalid_api_key"}, json={"markdown_text": "# Test\nThis is a test."})
    assert response.status_code == 200
    # Rate limiting logic should be tested in a separate test case (test_rate_limiting)

def test_convert_markdown_invalid_input():
    response = client.post("/convert", json={"markdown_text": ""})
    assert response.status_code == 200
    html_output = response.json().get("html_output").replace('\n', '').strip()
    expected_html = "<p></p>".strip()  # markdown2 converts empty string to <p></p>
    assert html_output == expected_html

def test_rate_limiting():
    for _ in range(101):
        response = client.post("/convert", json={"markdown_text": "# Test\nThis is a test."})
        if response.status_code != 402:
            # Rate limit should not apply until the last request
            assert response.status_code == 200
    last_response = client.post("/convert", json={"markdown_text": "# Test\nThis is a test."})
    assert last_response.status_code == 402
    detail = last_response.json().get("detail")
    expected_detail = "Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00"
    assert detail == expected_detail

def test_rate_limiting_with_valid_api_key():
    for _ in range(101):
        response = client.post("/convert", headers={"X-API-Key": "valid_api_key"}, json={"markdown_text": "# Test\nThis is a test."})
        assert response.status_code == 200