"""
Test: Brody SEMANTIC_ADVISORY_NO_MEMORY — UTF-8 Runtime Fix
=============================================================
Validates that /api/brody/chat with message="explique X108 avec la mémoire actuelle"
returns correct UTF-8 in final_answer when voice_source=SEMANTIC_ADVISORY_NO_MEMORY.

Targets the exact runtime path that showed mojibake:
  - rÃ©ponse → réponse
  - dÃ©cision → décision
  - Ã©criture → écriture
  - mÃ©moire → mémoire
  - â → (no standalone â from broken em dash)
"""
from __future__ import annotations
import json
import os
import pytest

# Patch environment before importing app
os.environ.setdefault("OBSIDIA_API_KEY", "")
os.environ.setdefault("OBSIDIA_AUTH_MODE", "apikey")
os.environ.setdefault("NEO4J_PASSWORD", "obsidia_neo4j_2026")

from apps.obsidia_api.main import app

client = pytest.importorskip("fastapi.testclient").TestClient(app)


@pytest.fixture(scope="module")
def brody_semantic_advisory_response():
    """
    Send the exact message that triggers SEMANTIC_ADVISORY_NO_MEMORY path.
    """
    resp = client.post("/api/brody/chat", json={
        "message": "explique X108 avec la mémoire actuelle",
        "language": "fr",
        "session_id": "test_semantic_advisory_utf8",
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
    return resp.json()


class TestSemanticAdvisoryRouting:
    """Verify the routing lands on the correct path."""

    def test_status_200(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response is not None

    def test_final_answer_source_is_semantic_advisory(self, brody_semantic_advisory_response):
        source = brody_semantic_advisory_response.get("final_answer_source", "")
        assert source == "SEMANTIC_ADVISORY_NO_MEMORY", (
            f"Expected SEMANTIC_ADVISORY_NO_MEMORY, got {source}"
        )

    def test_topic_is_x108(self, brody_semantic_advisory_response):
        topic = brody_semantic_advisory_response.get("topic", "")
        assert topic == "X108", f"Expected topic=X108, got topic={topic}"


class TestSemanticAdvisoryBoundary:
    """Verify all boundary invariants hold."""

    def test_neo4j_write_is_false(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("neo4j_write") is False

    def test_decision_authority_kx108_only(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("decision_authority") == "KX108_ONLY"

    def test_emits_act_is_false(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("emits_act") is False

    def test_memory_write_is_false(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("memory_write") is False

    def test_graphiti_write_is_false(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("graphiti_write") is False

    def test_kernel_mutation_is_false(self, brody_semantic_advisory_response):
        assert brody_semantic_advisory_response.get("kernel_mutation") is False


class TestSemanticAdvisoryUTF8:
    """Validate zero mojibake and correct French accents in final_answer."""

    # ── Forbidden mojibake patterns ──────────────────────────────────────
    _FORBIDDEN = [
        "\u00c3",  # Ã (U+00C3) — always a mojibake marker
        "\u00e2",  # â (U+00E2) — standalone â is always mojibake of em dash
    ]

    # ── Required accented French words ───────────────────────────────────
    _REQUIRED_WORDS = [
        "réponse",
        "décision",
        "mémoire",
    ]

    def test_final_answer_not_empty(self, brody_semantic_advisory_response):
        fa = brody_semantic_advisory_response.get("final_answer", "")
        assert fa, "final_answer is empty"
        assert len(fa) > 20, f"final_answer too short: {len(fa)} chars"

    def test_no_forbidden_mojibake_markers(self, brody_semantic_advisory_response):
        fa = brody_semantic_advisory_response.get("final_answer", "")
        for mb in self._FORBIDDEN:
            assert mb not in fa, (
                f"Mojibake marker U+{ord(mb):04X} found in final_answer. "
                f"First 300 chars: {fa[:300]}"
            )

    def test_contains_required_accented_words(self, brody_semantic_advisory_response):
        fa = brody_semantic_advisory_response.get("final_answer", "")
        missing = [w for w in self._REQUIRED_WORDS if w not in fa]
        assert not missing, (
            f"Missing accented words in final_answer: {missing}. "
            f"First 300 chars: {fa[:300]}"
        )

    def test_utf8_json_roundtrip(self, brody_semantic_advisory_response):
        """final_answer must survive JSON encode/decode with accents intact."""
        fa = brody_semantic_advisory_response.get("final_answer", "")
        roundtripped = json.loads(json.dumps({"text": fa}, ensure_ascii=False))
        assert roundtripped["text"] == fa, "final_answer changed during JSON roundtrip"
        for mb in self._FORBIDDEN:
            assert mb not in roundtripped["text"], (
                f"Mojibake appeared after JSON roundtrip: U+{ord(mb):04X}"
            )

    def test_response_field_also_clean(self, brody_semantic_advisory_response):
        """The 'response' field must also be mojibake-free."""
        resp = brody_semantic_advisory_response.get("response", "")
        for mb in self._FORBIDDEN:
            assert mb not in resp, (
                f"Mojibake marker U+{ord(mb):04X} found in 'response' field. "
                f"First 300 chars: {resp[:300]}"
            )
        for w in self._REQUIRED_WORDS:
            assert w in resp, f"Missing accented word '{w}' in 'response' field"

    def test_response_md_field_also_clean(self, brody_semantic_advisory_response):
        """The 'response_md' field must also be mojibake-free."""
        rmd = brody_semantic_advisory_response.get("response_md", "")
        if rmd:  # response_md may be empty on this path
            for mb in self._FORBIDDEN:
                assert mb not in rmd, (
                    f"Mojibake marker U+{ord(mb):04X} found in 'response_md' field."
                )

    def test_em_dash_or_hyphen_present_not_mojibake(self, brody_semantic_advisory_response):
        """The footer contains an em dash (—). It must be the real char, not â."""
        fa = brody_semantic_advisory_response.get("final_answer", "")
        # Real em dash is U+2014
        has_real_em_dash = "\u2014" in fa
        # Also accept if it was replaced by a simple hyphen
        has_hyphen = " - " in fa or " — " in fa or "\u2014" in fa or " -- " in fa
        assert has_hyphen, (
            f"No dash/hyphen separator found in final_answer. "
            f"First 200 chars: {fa[:200]}"
        )
        # The corrupted em dash pattern must NOT appear
        assert "\u00e2\u0080\u0094" not in fa, "Mojibake em dash (â\\x80\\x94) found"
        assert "\u00e2\u0080\u0093" not in fa, "Mojibake en dash (â\\x80\\x93) found"

class TestRepairMixedMojibake:
    """Unit test: repair_mojibake_via_latin1_roundtrip on the exact live mojibake string."""

    # The exact mojibake string from live HTTP at /api/brody/chat
    EXACT_MOJIBAKE = (
        "_Brody \u00e2 r\u00c3\u00a9ponse structur\u00c3\u00a9e readonly. "
        "KX108_ONLY. Pas de d\u00c3\u00a9cision, pas d'\u00c3\u00a9criture m\u00c3\u00a9moire._"
    )

    def test_repair_no_forbidden_chars(self):
        from apps.obsidia_api.brody_text_encoding import repair_mojibake_via_latin1_roundtrip
        result = repair_mojibake_via_latin1_roundtrip(self.EXACT_MOJIBAKE)
        assert "\u00c3" not in result, f"Mojibake Ã (U+00C3) found after repair: {result[:200]}"
        assert "\u00e2" not in result, f"Mojibake â (U+00E2) found after repair: {result[:200]}"

    def test_repair_contains_correct_accents(self):
        from apps.obsidia_api.brody_text_encoding import repair_mojibake_via_latin1_roundtrip
        result = repair_mojibake_via_latin1_roundtrip(self.EXACT_MOJIBAKE)
        assert "réponse" in result, f"'réponse' missing: {result[:200]}"
        assert "structurée" in result, f"'structurée' missing: {result[:200]}"
        assert "décision" in result, f"'décision' missing: {result[:200]}"
        assert "écriture" in result, f"'écriture' missing: {result[:200]}"
        assert "mémoire" in result, f"'mémoire' missing: {result[:200]}"

    def test_repair_contains_em_dash(self):
        from apps.obsidia_api.brody_text_encoding import repair_mojibake_via_latin1_roundtrip
        result = repair_mojibake_via_latin1_roundtrip(self.EXACT_MOJIBAKE)
        assert "\u2014" in result or "—" in result, f"Em dash missing: {result[:200]}"

    def test_repair_preserves_structure(self):
        from apps.obsidia_api.brody_text_encoding import repair_mojibake_via_latin1_roundtrip
        result = repair_mojibake_via_latin1_roundtrip(self.EXACT_MOJIBAKE)
        assert "KX108_ONLY" in result
        assert "_Brody" in result
        assert "readonly" in result
        assert len(result) > 50, f"Result too short after repair: {len(result)} chars"

    def test_repair_idempotent(self):
        from apps.obsidia_api.brody_text_encoding import repair_mojibake_via_latin1_roundtrip
        first = repair_mojibake_via_latin1_roundtrip(self.EXACT_MOJIBAKE)
        second = repair_mojibake_via_latin1_roundtrip(first)
        assert first == second, f"Repair not idempotent. First: {first[:100]}, Second: {second[:100]}"


class TestLastMilePreservesAccents:
    """Verify the last-mile repair on the HTTP payload preserves accents."""

    _FORBIDDEN = ["\u00c3", "\u00e2"]

    def test_last_mile_repair_preserves_accents(self, brody_semantic_advisory_response):
        """The last-mile repair must preserve accents, not strip to ASCII."""
        fa = brody_semantic_advisory_response.get("final_answer", "")
        # These accented chars must be present (confirm repair didn't fallback to ASCII)
        accented_chars = ["é", "è", "ê", "à"]
        found = [ch for ch in accented_chars if ch in fa]
        assert found, (
            f"No accented characters found after last-mile repair. "
            f"Accents may have been stripped. Found chars: {found}. "
            f"First 200 chars: {fa[:200]}"
        )
        # The forbidden markers must still be absent
        for mb in self._FORBIDDEN:
            assert mb not in fa
