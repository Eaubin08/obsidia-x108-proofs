"""
V5B+ Quality Test: Memory context response mentions readonly, candidate-only.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


def test_memory_query_response_contains_context_info():
    r = client.post("/api/brody/chat", json={"message": "montre moi le contexte memoire x108", "language": "fr"})
    data = r.json()
    resp = data["response"].lower()
    # Should mention memory/readonly/candidate context
    has_mem = any(w in resp for w in ["memoire", "memory", "candidate", "readonly", "lecture", "context"])
    assert has_mem, f"No memory context in response: {resp[:120]}"


def test_memory_query_response_no_write():
    r = client.post("/api/brody/chat", json={"message": "montre le contexte memoire", "language": "fr"})
    data = r.json()
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False


def test_memory_query_context_packet_present():
    r = client.post("/api/brody/chat", json={"message": "contexte memoire x108"})
    data = r.json()
    assert "context_packet" in data


def test_memory_query_response_source():
    r = client.post("/api/brody/chat", json={"message": "memoire x108 contexte"})
    data = r.json()
    assert data["source"] != "FRONTEND_MOCK"
