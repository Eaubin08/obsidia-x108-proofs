"""
Source docs audit tests — Brody LLM Obsidien structured response chain.
Verifies that modules found in source docs (2026-05-13) are importable
and expose the correct APIs.
"""
import pytest
from pathlib import Path


_PERIPHERY = (
    Path(__file__).resolve().parents[2]
    / "periphery" / "brody_memory_readonly"
)


# ── Module presence ────────────────────────────────────────────────────────────

def test_context_packet_query_module_exists():
    p = _PERIPHERY / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    assert p.exists(), f"Module not found: {p}"


def test_context_packet_consumer_module_exists():
    p = _PERIPHERY / "context_packet_consumer_readonly" / "brody_context_packet_consumer_readonly_v1.py"
    assert p.exists(), f"Module not found: {p}"


def test_local_response_engine_module_exists():
    p = _PERIPHERY / "local_response_engine_readonly" / "brody_local_response_engine_readonly_v1.py"
    assert p.exists(), f"Module not found: {p}"


def test_terminal_structural_dialogue_module_exists():
    p = _PERIPHERY / "terminal_structural_dialogue_readonly" / "brody_terminal_structural_dialogue_readonly_v1.py"
    assert p.exists(), f"Module not found: {p}"


# ── Source doc references ─────────────────────────────────────────────────────

def test_source_doc_roadmap_exists():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134" / "BRODY_NEXT_BUILD_ROADMAP_READONLY.md"
    if not p.exists():
        pytest.skip(reason="local audit source doc not committed to repo (local-only artifact)")
    assert p.exists(), f"Source doc not found: {p}"


def test_source_doc_architecture_map_exists():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_REAL_ARCHITECTURE_MAP_READONLY_20260513_190155" / "BRODY_REAL_ARCHITECTURE_MAP_READONLY_REPORT.md"
    if not p.exists():
        pytest.skip(reason="local audit source doc not committed to repo (local-only artifact)")
    assert p.exists()


def test_source_doc_checkpoint_exists():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_SESSION_CHECKPOINT_20260513_FINAL" / "BRODY_SESSION_CHECKPOINT_FINAL.md"
    if not p.exists():
        pytest.skip(reason="local audit source doc not committed to repo (local-only artifact)")
    assert p.exists()


# ── Source docs content ────────────────────────────────────────────────────────

def test_roadmap_declares_brody_llm_obsidien():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134" / "BRODY_NEXT_BUILD_ROADMAP_READONLY.md"
    if not p.exists():
        pytest.skip(reason="local audit roadmap not committed to repo (local-only artifact)")
    content = p.read_text(encoding="utf-8")
    assert "Brody = LLM obsidien" in content


def test_roadmap_declares_chain_pass():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134" / "BRODY_NEXT_BUILD_ROADMAP_READONLY.md"
    if not p.exists():
        pytest.skip(reason="local audit roadmap not committed to repo (local-only artifact)")
    content = p.read_text(encoding="utf-8")
    assert "CHAIN_PASS" in content


def test_roadmap_mentions_kx108_only():
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "_local_audits" / "BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134" / "BRODY_NEXT_BUILD_ROADMAP_READONLY.md"
    if not p.exists():
        pytest.skip(reason="local audit roadmap not committed to repo (local-only artifact)")
    content = p.read_text(encoding="utf-8")
    assert "KX108_ONLY" in content


# ── LOW_MATERIAL — text_preview already in coalesce ───────────────────────────

def test_query_module_coalesce_has_text_preview():
    query_py = _PERIPHERY / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    content = query_py.read_text(encoding="utf-8")
    assert "text_preview" in content, "text_preview must be in coalesce — LOW_MATERIAL patch"


def test_query_module_coalesce_order_correct():
    query_py = _PERIPHERY / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    content = query_py.read_text(encoding="utf-8")
    idx_preview = content.find("p.preview")
    idx_text_preview = content.find("p.text_preview")
    assert idx_preview != -1 and idx_text_preview != -1
    assert idx_preview < idx_text_preview, "p.preview must come before p.text_preview in coalesce"


# ── structured_response_engine_adapter module ─────────────────────────────────

def test_adapter_module_importable():
    from apps.obsidia_api.brody_structured_response_engine_adapter import (
        make_structured_response_snapshot,
        chain_md_to_final_answer,
    )
    assert callable(make_structured_response_snapshot)
    assert callable(chain_md_to_final_answer)


def test_adapter_boundary_constants():
    from apps.obsidia_api.brody_structured_response_engine_adapter import _BOUNDARY
    assert _BOUNDARY["readonly"] is True
    assert _BOUNDARY["memory_write"] is False
    assert _BOUNDARY["decision_authority"] == "KX108_ONLY"


def test_adapter_source_doc_refs():
    from apps.obsidia_api.brody_structured_response_engine_adapter import _SOURCE_DOC_REFS
    assert len(_SOURCE_DOC_REFS) == 3
    assert any("ARCHITECTURE_MAP" in r for r in _SOURCE_DOC_REFS)
    assert any("ROADMAP" in r for r in _SOURCE_DOC_REFS)
    assert any("CHECKPOINT" in r for r in _SOURCE_DOC_REFS)
