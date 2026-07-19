from fastapi.testclient import TestClient
from run import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_refill():
    resp = client.post("/api/chat", json={
        "message": "Refill my Lisinopril",
        "customer_id": "cust_123",
        "channel": "web"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert data["intent"] == "AUTH_REQUIRED"


def test_chat_appointment():
    resp = client.post("/api/chat", json={
        "message": "Book appointment with Dr. Sharma tomorrow",
        "customer_id": "cust_123",
        "channel": "web"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "HC_APPOINTMENT"
    assert "Dr. Sharma" in data["response"]


def test_auth_continuation():
    # First request triggers auth
    resp = client.post("/api/chat", json={
        "message": "Refill my Lisinopril",
        "customer_id": "cust_123",
        "channel": "web",
        "conversation_id": "test_auth_conv"
    })
    assert resp.status_code == 200
    assert resp.json()["intent"] == "AUTH_REQUIRED"

    # Second request provides PIN
    resp = client.post("/api/chat", json={
        "message": "1234",
        "customer_id": "cust_123",
        "channel": "web",
        "conversation_id": "test_auth_conv"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "HC_REFILL"
    assert "Lisinopril" in data["response"]
