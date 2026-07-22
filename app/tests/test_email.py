import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)


def test_send_email_audit_not_found():
    fake_id = str(uuid4())
    response = client.post(
        f"/api/v1/audits/{fake_id}/send-email",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 404


def test_send_email_invalid_format():
    fake_id = str(uuid4())
    response = client.post(
        f"/api/v1/audits/{fake_id}/send-email",
        json={"email": "invalid"}
    )
    assert response.status_code == 422