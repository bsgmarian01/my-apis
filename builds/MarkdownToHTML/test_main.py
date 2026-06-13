import os
from fastapi.testclient import TestClient
import pytest

# Mock the environment variable for API keys

from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rate_limits():
    """
    Clear the in-memory rate limit storage before each test to ensure tests do not interfere with one another.
    """
    global RATE_LIMITS




def test_convert_markdown_invalid_input():
    response = client.post("/convert", json={"markdown_text": ""})
    assert response.status_code == 200
    html_output = response.json().get("html_output").replace('\n', '').strip()
    expected_html = "<p></p>".strip()  # markdown2 converts empty string to <p></p>
    assert html_output == expected_html


