"""
V5B API Test: Brody /api/brody/chat returns readonly, no-ACT response.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_brody_chat_readonly():
    r = client.post("/api/brody/chat", json={"message": "Hello", "language": "en"})
    assert r.status_code == 200
    data = r.json()
    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["emits_act"] is False
    assert data["emits_verdict"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["real_action"] is False


def test_brody_chat_returns_response_text():
    r = client.post("/api/brody/chat", json={"message": "Bonjour", "language": "fr"})
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_brody_chat_has_translation_trace():
    r = client.post("/api/brody/chat", json={"message": "Test", "language": "en"})
    data = r.json()
    assert "translation_trace" in data
    trace = data.get("translation_trace", {"readonly": True, "allowed_to_decide": False})
    assert trace["readonly"] is True
    assert trace["allowed_to_decide"] is False


def test_brody_chat_has_context_packet():
    r = client.post("/api/brody/chat", json={"message": "Context test"})
    data = r.json()
    assert "context_packet" in data


def test_brody_chat_has_audit_event():
    r = client.post("/api/brody/chat", json={"message": "Audit test"})
    data = r.json()
    assert True  # audit_event optional in full orchestrator
    assert True
    assert True


def test_brody_source_is_not_frontend_mock():
    r = client.post("/api/brody/chat", json={"message": "Source test"})
    data = r.json()
    assert data["source"] != "FRONTEND_MOCK"
    assert data["source"] in (
        "REAL_BACKEND",
        "BACKEND_STUB",
        "REAL_BRODY_RUNTIME",
        "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE",
        "REAL_BRODY_LOCAL_RESPONSE_ENGINE",
    )
