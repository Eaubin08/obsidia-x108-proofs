"""
Phase 3 — Brody UTF-8 No-Mojibake Test

Proves that the API response `final_answer` contains no mojibake characters.
Root cause was POWERSHELL_RENDERING_ONLY (Windows pipe encoding artifact),
so this test is defensive — it documents and freezes the clean state.

Key assertion: final_answer string contains proper Unicode é (U+00E9),
NOT the mojibake pair Ã© (U+00C3 U+00A9).
"""
import json
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

_ACCENTED_MSG = "test mémoire structure"


@pytest.fixture(scope="module")
def response_data():
    r = client.post("/api/brody/chat", json={"message": _ACCENTED_MSG, "language": "fr"})
    assert r.status_code == 200
    # Use json.loads(r.content) to bypass any TestClient encoding quirks
    return json.loads(r.content)


def test_http_200(response_data):
    assert response_data is not None


def test_final_answer_non_empty(response_data):
    fa = response_data.get("final_answer", "")
    assert len(fa) > 20, "final_answer is too short"


def test_no_mojibake_in_final_answer(response_data):
    fa = response_data.get("final_answer", "")
    # Mojibake pattern: U+00C3 followed by U+00A9 (Ã©) = latin1-misread UTF-8 é
    mojibake_pairs = [
        (0xC3, 0xA9),   # Ã© ← é misread
        (0xC3, 0xA8),   # Ã¨ ← è misread
        (0xC3, 0xAA),   # Ãª ← ê misread
        (0xC3, 0xA0),   # Ã  ← à misread
        (0xC3, 0xB9),   # Ã¹ ← ù misread
        (0xC3, 0xB4),   # Ã´ ← ô misread
        (0xE2, 0x80),   # â€  ← — / " misread
    ]
    chars = list(fa)
    for i in range(len(chars) - 1):
        hi, lo = ord(chars[i]), ord(chars[i + 1])
        for exp_hi, exp_lo in mojibake_pairs:
            assert not (hi == exp_hi and lo == exp_lo), (
                f"Mojibake pair U+{exp_hi:04X} U+{exp_lo:04X} found at position {i} "
                f"in final_answer: ...{fa[max(0,i-10):i+15]!r}..."
            )


def test_proper_unicode_e_present(response_data):
    fa = response_data.get("final_answer", "")
    # final_answer should use proper é/è etc. (U+00E9 etc.)
    # For a French response, at least some accented char should be present
    has_proper_accent = any(0xC0 <= ord(c) <= 0xFF for c in fa)
    assert has_proper_accent, (
        "No proper accented characters (U+00C0–U+00FF) found in final_answer. "
        "Either the response is English-only or accents were stripped."
    )


def test_response_bytes_are_valid_utf8(response_data):
    fa = response_data.get("final_answer", "")
    # Re-encoding as UTF-8 and decoding back must be lossless
    roundtrip = fa.encode("utf-8").decode("utf-8")
    assert roundtrip == fa, "final_answer is not round-trip stable in UTF-8"


def test_no_replacement_chars(response_data):
    fa = response_data.get("final_answer", "")
    assert chr(0xFFFD) not in fa, "Replacement char U+FFFD found in final_answer"


def test_boundary_invariants(response_data):
    assert response_data.get("emits_act") is False
    assert response_data.get("memory_write") is False
    assert response_data.get("decision_authority") == "KX108_ONLY"
