"""
F72 — OS Trad / IR / Reverse Deep Pipeline Audit
Tests for apps/obsidia_api/routes/os_trad_ir_reverse.py

Coverage:
- Routes exist in OpenAPI schema
- POST /api/os-trad/translate → 200, boundaries, readonly
- POST /api/ir/candidate → 200, boundaries, readonly
- POST /api/os-reverse/project → 200, boundaries, readonly
- All responses: decision_authority=KX108_ONLY, emits_act=False, no mutations
- Pipeline chain: text → IR → reverse → readonly response
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.obsidia_api.main import app

client = TestClient(app)

_SOVEREIGNTY_FALSE_FLAGS = (
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "memory_write",
    "graphiti_write",
    "neo4j_write",
    "real_action",
)

_MINIMAL_TEXT = "Bonjour, voici une requête de test Obsidia readonly."
_MINIMAL_PAYLOAD_TRAD = {"text": _MINIMAL_TEXT, "language": "fr"}
_MINIMAL_PAYLOAD_IR = {"text": _MINIMAL_TEXT, "language": "fr"}
_MINIMAL_PAYLOAD_REVERSE = {
    "text": _MINIMAL_TEXT,
    "language": "fr",
    "ir_candidate": {"intent": "readonly_query"},
    "audience": "general",
    "format": "structured",
}


# ---------------------------------------------------------------------------
# Class 1 — Routes exist in OpenAPI
# ---------------------------------------------------------------------------

class TestF72RoutesExist:
    @pytest.fixture(scope="class")
    def paths(self):
        return set(app.openapi().get("paths", {}).keys())

    def test_os_trad_translate_in_openapi(self, paths):
        assert "/api/os-trad/translate" in paths

    def test_ir_candidate_in_openapi(self, paths):
        assert "/api/ir/candidate" in paths

    def test_os_reverse_project_in_openapi(self, paths):
        assert "/api/os-reverse/project" in paths


# ---------------------------------------------------------------------------
# Class 2 — POST /api/os-trad/translate
# ---------------------------------------------------------------------------

class TestF72OSTradTranslate:
    @pytest.fixture(scope="class")
    def response(self):
        r = client.post("/api/os-trad/translate", json=_MINIMAL_PAYLOAD_TRAD)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        return r.json()

    def test_http_200(self):
        r = client.post("/api/os-trad/translate", json=_MINIMAL_PAYLOAD_TRAD)
        assert r.status_code == 200

    def test_decision_authority_kx108(self, response):
        assert response.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, response):
        assert response.get("readonly") is True

    def test_advisory_only_true(self, response):
        assert response.get("advisory_only") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE_FLAGS)
    def test_sovereignty_false(self, response, flag):
        assert response.get(flag) is False, f"{flag} not False in /api/os-trad/translate response"


# ---------------------------------------------------------------------------
# Class 3 — POST /api/ir/candidate
# ---------------------------------------------------------------------------

class TestF72IRCandidate:
    @pytest.fixture(scope="class")
    def response(self):
        r = client.post("/api/ir/candidate", json=_MINIMAL_PAYLOAD_IR)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        return r.json()

    def test_http_200(self):
        r = client.post("/api/ir/candidate", json=_MINIMAL_PAYLOAD_IR)
        assert r.status_code == 200

    def test_decision_authority_kx108(self, response):
        assert response.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, response):
        assert response.get("readonly") is True

    def test_advisory_only_true(self, response):
        assert response.get("advisory_only") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE_FLAGS)
    def test_sovereignty_false(self, response, flag):
        assert response.get(flag) is False, f"{flag} not False in /api/ir/candidate response"


# ---------------------------------------------------------------------------
# Class 4 — POST /api/os-reverse/project
# ---------------------------------------------------------------------------

class TestF72OSReverseProject:
    @pytest.fixture(scope="class")
    def response(self):
        r = client.post("/api/os-reverse/project", json=_MINIMAL_PAYLOAD_REVERSE)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        return r.json()

    def test_http_200(self):
        r = client.post("/api/os-reverse/project", json=_MINIMAL_PAYLOAD_REVERSE)
        assert r.status_code == 200

    def test_decision_authority_kx108(self, response):
        assert response.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, response):
        assert response.get("readonly") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE_FLAGS)
    def test_sovereignty_false(self, response, flag):
        assert response.get(flag) is False, f"{flag} not False in /api/os-reverse/project response"


# ---------------------------------------------------------------------------
# Class 5 — Pipeline boundary: IR enriches without deciding
# ---------------------------------------------------------------------------

class TestF72PipelineBoundary:
    def test_trad_then_ir_readonly_chain(self):
        """Text → OS Trad → IR : chaque étape reste readonly."""
        r_trad = client.post("/api/os-trad/translate", json=_MINIMAL_PAYLOAD_TRAD)
        assert r_trad.status_code == 200
        trad_data = r_trad.json()
        assert trad_data.get("emits_act") is False

        ir_payload = {
            "text": _MINIMAL_TEXT,
            "language": "fr",
            "memory_context": trad_data,
        }
        r_ir = client.post("/api/ir/candidate", json=ir_payload)
        assert r_ir.status_code == 200
        ir_data = r_ir.json()
        assert ir_data.get("emits_act") is False
        assert ir_data.get("decision_authority") == "KX108_ONLY"

    def test_no_act_token_in_any_route(self):
        """Aucune réponse ne contient de token interdit au niveau racine."""
        import json
        import re
        forbidden = re.compile(r'\b(ALLOW|HOLD|BLOCK|DECIDE|VERDICT)\b')
        for endpoint, payload in [
            ("/api/os-trad/translate", _MINIMAL_PAYLOAD_TRAD),
            ("/api/ir/candidate", _MINIMAL_PAYLOAD_IR),
            ("/api/os-reverse/project", _MINIMAL_PAYLOAD_REVERSE),
        ]:
            r = client.post(endpoint, json=payload)
            assert r.status_code == 200
            text = json.dumps(r.json())
            matches = forbidden.findall(text)
            assert not matches, f"Forbidden tokens {matches} in {endpoint} response"


# ---------------------------------------------------------------------------
# Class 6 — Empty + edge payloads
# ---------------------------------------------------------------------------

class TestF72EdgePayloads:
    def test_trad_empty_text_no_crash(self):
        r = client.post("/api/os-trad/translate", json={"text": "", "language": "fr"})
        assert r.status_code in (200, 422)

    def test_ir_empty_text_no_crash(self):
        r = client.post("/api/ir/candidate", json={"text": "", "language": "fr"})
        assert r.status_code in (200, 422)

    def test_reverse_empty_payload_no_crash(self):
        r = client.post("/api/os-reverse/project", json={})
        assert r.status_code in (200, 422)
