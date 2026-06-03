"""
Legacy Brody conscience test — CI-safe rewrite.

Original: called http://127.0.0.1:8000/api/brody/chat directly (live server required).
Rewrite: uses FastAPI TestClient (no live server, no network, runs in CI).

Validates:
  - /api/brody/chat returns HTTP 200
  - decision_authority = KX108_ONLY
  - emits_act = False
  - final_answer is present and non-empty
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

_PAYLOAD = {
    "message": (
        "Explique ton architecture technique. "
        "Comment recois-tu les evenements Gencoin et pourquoi es-tu en mode readonly ?"
    ),
    "language": "fr",
    "session_id": "audit_architecture_001",
}


def test_brody_conscience_returns_200():
    r = client.post("/api/brody/chat", json=_PAYLOAD)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:200]}"


def test_brody_conscience_decision_authority_kx108():
    r = client.post("/api/brody/chat", json=_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority={body.get('decision_authority')}"
    )


def test_brody_conscience_no_act():
    r = client.post("/api/brody/chat", json=_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body.get("emits_act") is False, f"emits_act={body.get('emits_act')}"


def test_brody_conscience_final_answer_present():
    r = client.post("/api/brody/chat", json=_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    final = body.get("final_answer") or body.get("response", "")
    assert final, "final_answer/response is empty"
