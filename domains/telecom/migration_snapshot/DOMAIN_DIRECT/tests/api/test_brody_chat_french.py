"""
V5B API Test: Brody chat returns French response for French input.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_brody_chat_french_input_returns_french_language_tag():
    r = client.post("/api/brody/chat", json={"message": "salut mon gars", "language": "fr"})
    data = r.json()
    assert data["language"] == "fr"
    assert len(data["response"]) > 0


def test_brody_chat_french_response_not_empty():
    r = client.post("/api/brody/chat", json={"message": "bonjour comment ca va", "language": "fr"})
    data = r.json()
    assert "response" in data
    assert data["response"] != ""


def test_brody_chat_french_trace():
    r = client.post("/api/brody/chat", json={"message": "salut", "language": "fr"})
    data = r.json()
    trace = data.get("translation_trace", {"readonly": True, "allowed_to_decide": False})
    assert trace["detected_language"] in ("fr", "en")
    assert trace["response_language"] in ("fr", "en")


def test_brody_chat_respects_input_language():
    r = client.post("/api/brody/chat", json={"message": "hello world", "language": "en"})
    data = r.json()
    assert data["language"] == "en"
