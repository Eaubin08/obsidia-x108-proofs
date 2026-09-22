"""
Tests for brody_structured_response_engine_adapter.py
Verifies make_structured_response_snapshot() and chain_md_to_final_answer().
"""
import pytest
from apps.obsidia_api.brody_structured_response_engine_adapter import (
    make_structured_response_snapshot,
    chain_md_to_final_answer,
    _BOUNDARY,
    _SOURCE_DOC_REFS,
)


# ── make_structured_response_snapshot ────────────────────────────────────────

def _pipeline_offline() -> dict:
    return {
        "graphiti_probe": {"status": "GRAPHITI_LIVE_BLOCKED", "blocker": "NEO4J_PASSWORD not set", "port_7688_open": False},
        "engine_status": "TERMINAL_FALLBACK",
        "material_quality": "",
        "response_md": "",
        "selected_items": [],
        "tag_counts": {},
        "memory_query": "",
        "neo4j_status": "OFFLINE_OR_UNAVAILABLE",
    }


def _pipeline_live_with_material() -> dict:
    return {
        "graphiti_probe": {"status": "GRAPHITI_LIVE_READONLY_PASS", "blocker": "", "port_7688_open": True},
        "engine_status": "BRODY_LOCAL_RESPONSE_ENGINE_READONLY_PASS",
        "material_quality": "USABLE_MATERIAL",
        "response_md": "# BRODY LOCAL RESPONSE ENGINE — READONLY\n\n## Lecture active\n\n### 1. Doc Title\n- score: 280\n\nContent here.",
        "selected_items": [{"title": "doc1"}, {"title": "doc2"}],
        "tag_counts": {"x108": 3},
        "memory_query": "x108 kernel",
        "neo4j_status": "LIVE_READONLY",
    }


def _pipeline_live_low_material() -> dict:
    return {
        "graphiti_probe": {"status": "GRAPHITI_LIVE_READONLY_PASS", "blocker": "", "port_7688_open": True},
        "engine_status": "BRODY_LOCAL_RESPONSE_ENGINE_READONLY_PASS",
        "material_quality": "LOW_MATERIAL",
        "response_md": "",
        "selected_items": [],
        "tag_counts": {},
        "memory_query": "test",
        "neo4j_status": "LIVE_READONLY",
    }


# Offline scenarios

def test_offline_status():
    snap = make_structured_response_snapshot(_pipeline_offline())
    assert snap["status"] == "STRUCTURED_RESPONSE_ENGINE_UNAVAILABLE"
    assert snap["readonly"] is True
    assert snap["memory_write"] is False
    assert snap["decision_authority"] == "KX108_ONLY"


def test_offline_query_stage_unavailable():
    snap = make_structured_response_snapshot(_pipeline_offline())
    assert snap["query_stage"] == "NOT_REQUIRED"
    assert snap["readonly"] is True
    assert snap["memory_write"] is False


def test_offline_material_status_chain_unavailable():
    snap = make_structured_response_snapshot(_pipeline_offline())
    assert snap["text_material_status"] == "CHAIN_UNAVAILABLE"


def test_offline_context_items_count_zero():
    snap = make_structured_response_snapshot(_pipeline_offline())
    assert snap["context_items_count"] == 0


# Live with material

def test_live_material_status_has_material():
    snap = make_structured_response_snapshot(_pipeline_live_with_material())
    assert snap["text_material_status"] == "HAS_MATERIAL"


def test_live_query_stage_pass():
    snap = make_structured_response_snapshot(_pipeline_live_with_material())
    assert snap["query_stage"] == "PASS"
    assert snap["engine_stage"] == "PASS"


def test_live_context_items_count():
    snap = make_structured_response_snapshot(_pipeline_live_with_material())
    assert snap["context_items_count"] == 2


def test_live_response_md_preserved():
    snap = make_structured_response_snapshot(_pipeline_live_with_material())
    assert "BRODY LOCAL RESPONSE ENGINE" in snap["response_md"]


# Live low material

def test_live_low_material_status():
    snap = make_structured_response_snapshot(_pipeline_live_low_material())
    assert snap["text_material_status"] == "LOW_MATERIAL"


# Boundary invariants

def test_boundary_readonly():
    for pipeline in [_pipeline_offline(), _pipeline_live_with_material()]:
        snap = make_structured_response_snapshot(pipeline)
        assert snap["readonly"] is True
        assert snap["memory_write"] is False
        assert snap["emits_act"] is False
        assert snap["kernel_mutation"] is False
        assert snap["decision_authority"] == "KX108_ONLY"
        assert "graphiti_write" not in snap
        assert "neo4j_write" not in snap


def test_source_doc_refs_present():
    snap = make_structured_response_snapshot(_pipeline_offline())
    refs = snap.get("source_doc_refs", [])
    assert len(refs) == 3
    assert any("ARCHITECTURE_MAP" in r for r in refs)


def test_chain_source_present():
    snap = make_structured_response_snapshot(_pipeline_offline())
    assert "chain_source" in snap
    assert "BRODY_REAL_RESPONSE_PIPELINE" in snap["chain_source"]


# ── chain_md_to_final_answer ──────────────────────────────────────────────────

_GOOD_CHAIN_MD = """# BRODY LOCAL RESPONSE ENGINE — READONLY

- query: operator loop
- role: LOCAL_RESPONSE_ENGINE
- decision_authority: KX108_ONLY
- emits_act: false

## Réponse locale structurée

Brody transforme le packet hydraté en réponse locale structurée.

## Lecture active

### 1. Operator Loop Guide
- score: 280
- source_ref: docs/operator_loop.md

The operator loop consists of: command_packet → gate → receipt → handoff → boundary_final.

## Carte tags

- operator: 3

## Sources

- Operator Loop Guide :: docs/operator_loop.md

## Boundary

Memory is guide/context/navigation only.
"""

_NO_CONTENT_CHAIN_MD = """# BRODY LOCAL RESPONSE ENGINE — READONLY

- query: xyz
- role: LOCAL_RESPONSE_ENGINE

## Réponse locale structurée

Brody transforme le packet hydraté.

## Lecture active

Aucun extrait local hydraté exploitable dans ce packet.

## Boundary

Memory is guide/context only.
"""


def test_chain_md_extracts_content():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "fr")
    assert "Operator Loop Guide" in result
    assert "command_packet" in result


def test_chain_md_strips_header():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "fr")
    assert "# BRODY LOCAL RESPONSE ENGINE" not in result


def test_chain_md_strips_metadata_lines():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "fr")
    assert "- query:" not in result
    assert "- role:" not in result
    assert "- decision_authority:" not in result


def test_chain_md_strips_boundary_section():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "fr")
    assert "Memory is guide" not in result


def test_chain_md_has_footer_fr():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "fr")
    assert "KX108_ONLY" in result


def test_chain_md_has_footer_en():
    result = chain_md_to_final_answer(_GOOD_CHAIN_MD, "en")
    assert "KX108_ONLY" in result


def test_chain_md_no_content_returns_empty():
    result = chain_md_to_final_answer(_NO_CONTENT_CHAIN_MD, "fr")
    assert result == ""


def test_chain_md_empty_input_returns_empty():
    assert chain_md_to_final_answer("", "fr") == ""
    assert chain_md_to_final_answer(None, "fr") == ""  # type: ignore
