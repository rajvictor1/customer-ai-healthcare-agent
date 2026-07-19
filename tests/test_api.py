import pytest
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
