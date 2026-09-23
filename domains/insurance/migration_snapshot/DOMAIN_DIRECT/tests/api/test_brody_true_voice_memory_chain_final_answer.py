"""
Tests: build_true_brody_answer() — final_answer reflects memory chain source.

When chain is LOCAL_INDEX_FALLBACK_PARTIAL with selected_items,
final_answer must acknowledge local index mode (not claim live Neo4j).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer

_BASE_CTX = {
    "brody_full_context": {},
    "true_response_structure_snapshot": {},
    "project_memory_snapshot": {},
    "session_memory_snapshot": {},
    "freeze_metrics_snapshot": {},
    "authority_snapshot": {},
    "automation_snapshot": {},
    "structured_response_snapshot": {},
}


def _make_ctx(chain_override: dict) -> dict:
    ctx = dict(_BASE_CTX)
    ctx["memory_response_chain_snapshot"] = chain_override
    return ctx


def test_local_fallback_partial_with_items_uses_voice_source():
    chain = {
        "status": "LOCAL_INDEX_FALLBACK_PARTIAL",
        "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
        "material_quality": "PARTIAL_MATERIAL",
        "response_md": "",
        "selected_items": [
            {"title": "X108 kernel governance", "tags": ["x108", "kernel", "kx108"]},
            {"title": "Brody decision authority", "tags": ["brody", "x108"]},
        ],
        "effective_query": "x108",
        "primary_query": "x108",
        "graphiti_live": False,
    }
    r = build_true_brody_answer(user_message="X108 kernel", brody_full_context=_make_ctx(chain))
    assert isinstance(r, dict)
    assert r.get("voice_source") == "LOCAL_GRAPHITI_INDEX_FALLBACK"
    fa = r.get("final_answer", "")
    assert "x108" in fa.lower() or "index" in fa.lower() or "local" in fa.lower(), (
        f"final_answer should reference local index: {fa[:200]!r}"
    )


def test_local_fallback_partial_no_items_does_not_claim_local_fallback():
    chain = {
        "status": "LOCAL_INDEX_FALLBACK_PARTIAL",
        "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
        "material_quality": "PARTIAL_MATERIAL",
        "response_md": "",
        "selected_items": [],
        "effective_query": "x108",
        "graphiti_live": False,
    }
    r = build_true_brody_answer(user_message="X108 kernel", brody_full_context=_make_ctx(chain))
    # With empty selected_items, should NOT claim LOCAL_GRAPHITI_INDEX_FALLBACK voice
    assert r.get("voice_source") != "LOCAL_GRAPHITI_INDEX_FALLBACK"


def test_chain_pass_with_response_md_uses_memory_response_chain():
    chain = {
        "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
        "source_mode": "MEMORY_RESPONSE_CHAIN",
        "material_quality": "USABLE_MATERIAL",
        "response_md": "X108 kernel est le décisionnaire unique. Boundary: readonly.",
        "selected_items": [],
        "graphiti_live": True,
    }
    r = build_true_brody_answer(user_message="X108 kernel", brody_full_context=_make_ctx(chain))
    assert r.get("voice_source") == "MEMORY_RESPONSE_CHAIN"
    fa = r.get("final_answer", "")
    assert "X108" in fa or "kernel" in fa.lower()


def test_no_chain_produces_valid_answer():
    ctx = dict(_BASE_CTX)
    ctx["memory_response_chain_snapshot"] = {}
    r = build_true_brody_answer(user_message="bonjour", brody_full_context=ctx)
    assert isinstance(r, dict)
    assert r.get("final_answer")


def test_boundary_fields_always_present():
    chain = {
        "status": "LOCAL_INDEX_FALLBACK_PARTIAL",
        "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
        "material_quality": "PARTIAL_MATERIAL",
        "response_md": "",
        "selected_items": [{"title": "test", "tags": []}],
        "effective_query": "x108",
        "graphiti_live": False,
    }
    r = build_true_brody_answer(user_message="X108", brody_full_context=_make_ctx(chain))
    assert r.get("readonly") is True
    assert r.get("memory_write") is False
    assert r.get("emits_act") is False
    assert r.get("decision_authority") == "KX108_ONLY"
