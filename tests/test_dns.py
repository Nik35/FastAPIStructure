import requests
import uuid
import os

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/v1/dns/create")

def test_create_dns_request():
    request_data = {
        "context": {
            "account_id": "test_account",
            "source": "api"
        },
        "resource": {
            "record_type": "A",
            "domain": "example.com",
            "target": "192.168.1.1",
            "comment": "Test record",
            "config": {
                "ttl": 600,
                "priority": 10,
                "extra_config": {"custom_field": "custom_value"}
            }
        }
    }

    response = requests.post(API_URL, json=request_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "PENDING"
    assert response_data["message"] == "DNS request submitted and is being processed."
    assert uuid.UUID(response_data["context"]["request_id"])
    assert response_data["context"]["partition"] == "dns"
    assert response_data["context"]["service"] == "orchestrator"
    assert response_data["context"]["region"] == "global"
    assert response_data["context"]["account_id"] == "test_account"
