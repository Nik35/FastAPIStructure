import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_dns_request():
    payload = {
        "context": {"account_id": "test123"},
        "resource": {
            "record_type": "A",
            "domain": "example.com",
            "target": "1.2.3.4"
        }
    }
    response = client.post("/api/v1/dns/create", json=payload)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "status" in data
    assert data["status"] in ["PENDING", "SUCCESS", "FAILED"]


def test_create_dns_request_invalid_payload():
    # Missing required 'resource' field
    payload = {
        "context": {"account_id": "test123"}
    }
    response = client.post("/api/v1/dns/create", json=payload)
    assert response.status_code == 422


def test_create_dns_request_missing_context():
    # Missing required 'context' field
    payload = {
        "resource": {
            "record_type": "A",
            "domain": "example.com",
            "target": "1.2.3.4"
        }
    }
    response = client.post("/api/v1/dns/create", json=payload)
    assert response.status_code == 422


def test_create_dns_request_mx_record():
    # Valid MX record with extra config
    payload = {
        "context": {"account_id": "test456"},
        "resource": {
            "record_type": "MX",
            "domain": "mail.example.com",
            "target": "mailserver.example.com",
            "config": {"priority": 10, "ttl": 600}
        }
    }
    response = client.post("/api/v1/dns/create", json=payload)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "status" in data
