from fastapi.testclient import TestClient
import pytest

from main import app
import os

client = TestClient(app)

def test_validate_json_valid():
    """
    Test valid JSON data against a correct schema.
    """
    response = client.post(
        "/validate",
        json={
            "data": {"name": "John Doe", "age": 30},
            "json_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json()['valid'] is True

def test_validate_json_invalid_data():
    """
    Test invalid JSON data against a correct schema.
    """
    response = client.post(
        "/validate",
        json={
            "data": {"name": "John Doe", "age": "thirty"},
            "json_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json()['valid'] is False

def test_validate_json_invalid_schema():
    """
    Test invalid JSON schema.
    """
    response = client.post(
        "/validate",
        json={
            "data": {"name": "John Doe", "age": 30},
            "json_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "unknown_type"}  # This is an invalid type
                },
                "required": ["name", "age"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json()['valid'] is False

def test_validate_json_empty_schema():
    """
    Test empty JSON schema.
    """
    response = client.post(
        "/validate",
        json={
            "data": {"name": "John Doe", "age": 30},
            "json_schema": {}
        }
    )
    assert response.status_code == 422
    assert response.json()['detail'] == "Schema cannot be empty"

def test_validate_json_no_schema():
    """
    Test no JSON schema provided.
    """
    response = client.post(
        "/validate",
        json={
            "data": {"name": "John Doe", "age": 30}
        }
    )
    assert response.status_code == 422


