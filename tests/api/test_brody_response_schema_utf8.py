"""
Test: Brody response schema + UTF-8 integrity
==============================================
Validates that /api/brody/chat returns:
  - status 200
  - final_answer with correct French accents (no mojibake)
  - topic top-level non-empty
  - final_answer_source top-level non-empty
  - neo4j_write == false
  - decision_authority == KX108_ONLY
  - emits_act == false
  - memory_write == false
  - graphiti_write == false
  - kernel_mutation == false
"""
from __future__ import annotations
import json
import pytest
from fastapi.testclient import TestClient

# Patch environment before importing app
import os
os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = TestClient(app)

# ── Moji bake patterns that MUST NOT appear ──────────────────────────────────
_FORBIDDEN_MOJIBAKE = [
    "\u00c3\u00a9",  # Ã©
    "\u00c3\u00a8",  # Ã¨
    "\u00c3\u00aa",  # Ãª
    "\u00c3\u00a0",  # Ã
    "\u00c3\u00a2",  # â
    "\u00c3\u00b9",  # Ã¹
    "\u00c3\u00bb",  # Ã»
    "\u00c3\u00ae",  # Ã®
    "\u00c3\u00af",  # Ã¯
    "\u00c3\u00b4",  # Ã´
    "\u00c3\u00b6",  # Ã¶
    "\u00c3\u00a7",  # Ã§
]

# ── Accented French words that MUST appear somewhere in the response ─────────
# (at least one of these accented characters should appear if Brody responds in French)
_ACCENTED_CHARS = "éèêëàâùûîïôöçÉÈÊËÀÂÙÛÎÏÔÖÇ"


def _has_accented(text: str) -> bool:
    return any(ch in _ACCENTED_CHARS for ch in text)


def _has_mojibake(text: str) -> bool:
    return any(mb in text for mb in _FORBIDDEN_MOJIBAKE)


@pytest.fixture(scope="module")
def brody_response():
    """Send a simple French query to Brody to get a baseline response."""
    resp = client.post("/api/brody/chat", json={
        "message": "Bonjour Brody, quel est l'etat du systeme ?",
        "language": "fr",
        "session_id": "test_schema_utf8",
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
    return resp.json()


class TestBrodyResponseSchema:
    """Validate top-level schema invariants."""

    def test_status_200(self, brody_response):
        assert brody_response is not None

    def test_final_answer_not_empty(self, brody_response):
        fa = brody_response.get("final_answer", "")
        assert fa, "final_answer is empty"
        assert len(fa) > 20, f"final_answer too short: {len(fa)} chars"

    def test_final_answer_no_mojibake(self, brody_response):
        fa = brody_response.get("final_answer", "")
        assert not _has_mojibake(fa), f"final_answer contains mojibake: {fa[:200]}"

    def test_topic_top_level_non_empty(self, brody_response):
        topic = brody_response.get("topic", "")
        assert topic, "topic is empty at top level"

    def test_final_answer_source_top_level_non_empty(self, brody_response):
        source = brody_response.get("final_answer_source", "")
        assert source, "final_answer_source is empty at top level"

    def test_neo4j_write_is_false(self, brody_response):
        assert brody_response.get("neo4j_write") is False, f"neo4j_write={brody_response.get('neo4j_write')}"

    def test_decision_authority_kx108(self, brody_response):
        assert brody_response.get("decision_authority") == "KX108_ONLY"

    def test_emits_act_is_false(self, brody_response):
        assert brody_response.get("emits_act") is False

    def test_memory_write_is_false(self, brody_response):
        assert brody_response.get("memory_write") is False

    def test_graphiti_write_is_false(self, brody_response):
        assert brody_response.get("graphiti_write") is False

    def test_kernel_mutation_is_false(self, brody_response):
        assert brody_response.get("kernel_mutation") is False


class TestBrodyUTF8:
    """Validate UTF-8 integrity of the final_answer field."""

    # List of common French words that require accents.
    # At least 3 must appear correctly if Brody answers in French.
    ACCENTED_WORDS = [
        "décision", "système", "frontière", "irréversible",
        "préparer", "mémoire", "réponse", "état", "autorité",
        "périmètre", "décideur", "émet", "détecté",
    ]

    def test_final_answer_has_correct_accents(self, brody_response):
        fa = brody_response.get("final_answer", "")
        found = [w for w in self.ACCENTED_WORDS if w in fa]
        # At least 2 accented words should appear
        assert len(found) >= 2, (
            f"Only {len(found)} accented words found in final_answer. "
            f"Text may have lost accents. Found: {found}. "
            f"First 300 chars: {fa[:300]}"
        )

    def test_final_answer_no_naked_ascii_variants(self, brody_response):
        """Ensure common French words haven't been stripped to ASCII."""
        fa = brody_response.get("final_answer", "")
        # These ASCII-only forms of normally-accented words are suspicious
        suspicious = [
            ("decision", "décision"),
            ("systeme", "système"),
            ("memoire", "mémoire"),
            ("reponse", "réponse"),
            ("autorite", "autorité"),
            ("prepare", "prépare"),
        ]
        issues = []
        for ascii_form, accented_form in suspicious:
            # If ASCII form appears but accent form does NOT, that's a problem
            if ascii_form in fa and accented_form not in fa:
                issues.append(f"'{ascii_form}' found but '{accented_form}' missing")
        assert not issues, f"Accents stripped: {'; '.join(issues)}. Text: {fa[:300]}"

    def test_response_contains_french_response(self, brody_response):
        """Brody must respond in French with accented characters."""
        fa = brody_response.get("final_answer", "")
        assert _has_accented(fa), (
            f"No accented characters found in French response. "
            f"First 200 chars: {fa[:200]}"
        )

    def test_response_utf8_roundtrip(self, brody_response):
        """final_answer must survive a JSON encode/decode roundtrip."""
        fa = brody_response.get("final_answer", "")
        # Simulate what happens over the wire
        roundtripped = json.loads(json.dumps({"text": fa}, ensure_ascii=False))
        assert roundtripped["text"] == fa, "final_answer changed during JSON roundtrip"
        assert not _has_mojibake(roundtripped["text"]), "Mojibake appeared after JSON roundtrip"
