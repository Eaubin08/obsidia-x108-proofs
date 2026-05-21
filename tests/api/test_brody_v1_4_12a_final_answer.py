"""
Phase 4 — Brody V1.4.12A final_answer tests.
Validates that the V1.4.12A layer produces a natural French response separate from response_md.
"""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

MSG = (
    "Salut mon pote, tu vas bien ? Je suis ton créateur. "
    "Je peux te dire, on va aller loin, dans tous les sens."
)


@pytest.fixture(scope="module")
def brody_response():
    r = client.post("/api/brody/chat", json={"message": MSG, "language": "fr"})
    assert r.status_code == 200
    return r.json()


def test_http_200(brody_response):
    assert brody_response is not None


def test_final_answer_exists(brody_response):
    assert "final_answer" in brody_response
    assert brody_response["final_answer"]
    assert len(brody_response["final_answer"]) > 10


def test_response_equals_final_answer(brody_response):
    assert brody_response["response"] == brody_response["final_answer"]


def test_final_answer_is_french(brody_response):
    fa = brody_response["final_answer"].lower()
    fr_markers = ["je", "brody", "obsidia", "contexte", "autorité", "autorit", "salut",
                  "créateur", "createur", "décide", "decide", "décision", "decision"]
    assert any(m in fa for m in fr_markers), f"final_answer doesn't look French: {fa[:200]}"


def test_final_answer_not_response_md_format(brody_response):
    fa = brody_response["final_answer"]
    # final_answer must not look like the structured response_md audit format
    assert not fa.startswith("# BRODY LOCAL RESPONSE ENGINE"), f"final_answer is response_md format"
    assert not fa.startswith("RÉPONSE STRUCTURELLE"), f"final_answer is response_md format"
    assert not fa.startswith("brody >"), f"final_answer is response_md terminal format"


def test_response_md_exists_separately(brody_response):
    assert "response_md" in brody_response
    assert brody_response["response_md"]


def test_voice_runtime_is_v1_4_12a(brody_response):
    assert brody_response.get("voice_runtime") == "BRODY_OBSIDIEN_V1_4_12A"


def test_decision_authority_kx108(brody_response):
    assert brody_response.get("decision_authority") == "KX108_ONLY"


def test_allowed_to_decide_false(brody_response):
    assert brody_response.get("allowed_to_decide", False) is False
    # sovereignty field in top-level response
    assert brody_response.get("emits_act") is False


def test_no_forbidden_sovereign_token_in_final_answer(brody_response):
    fa = brody_response["final_answer"].upper()
    # These tokens must never appear as sovereign decisions in the response
    # Note: 'VERDICT' appearing in a negation ("je ne produis pas de verdict") is allowed
    forbidden = [" ALLOW ", " HOLD ", " BLOCK ", " DECIDE "]
    for tok in forbidden:
        assert tok not in fa, f"Forbidden token {tok.strip()} found in final_answer"


def test_memory_write_false(brody_response):
    assert brody_response.get("memory_write") is False


def test_kernel_mutation_false(brody_response):
    assert brody_response.get("kernel_mutation") is False
