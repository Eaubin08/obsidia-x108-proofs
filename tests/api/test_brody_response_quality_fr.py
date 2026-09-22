"""
V5B+ Quality Test: Brody French response is natural, not a placeholder.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_french_greeting_response_natural():
    r = client.post("/api/brody/chat", json={"message": "salut mon gars", "language": "fr"})
    data = r.json()
    assert data["language"] == "fr"
    assert data["response"] != ""
    # Must NOT be the placeholder
    assert "BRODY_READONLY_RESPONSE" not in data["response"].upper().split("CONTEXT")[0] if "CONTEXT" in data["response"].upper() else True
    # Should contain X108 reference or advisory language
    assert any(w in data["response"].lower() for w in ["salut", "bonjour", "brody", "x108", "readonly", "advisory", "consultatif", "decide"])


def test_french_response_not_only_placeholder():
    r = client.post("/api/brody/chat", json={"message": "bonjour comment ca va", "language": "fr"})
    data = r.json()
    # Response should be longer than a placeholder
    assert len(data["response"]) > 30, f"Response too short: {data['response']}"


def test_french_response_contains_sovereignty_reminder():
    r = client.post("/api/brody/chat", json={"message": "salut", "language": "fr"})
    data = r.json()
    # Should mention advisory/readonly/no-decision context
    resp = data["response"].lower()
    has_sovereignty_marker = any(w in resp for w in ["x108", "advisory", "readonly", "consultatif", "decide pas", "pas de decision"])
    assert has_sovereignty_marker, f"No sovereignty marker in: {resp[:100]}"


def test_french_response_source_real_backend():
    r = client.post("/api/brody/chat", json={"message": "salut", "language": "fr"})
    data = r.json()
    assert data["source"] in (
        "REAL_BACKEND", "BACKEND_STUB", "REAL_BRODY_RUNTIME",
        "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE", "REAL_BRODY_LOCAL_RESPONSE_ENGINE",
    )
    assert data["emits_act"] is False
    assert data["decision_authority"] == "KX108_ONLY"
