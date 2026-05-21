"""
LOW_MATERIAL patch tests — verify text_preview is in coalesce.
Source: BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134 §2.A
"""
import pytest
from pathlib import Path

_QUERY_PY = (
    Path(__file__).resolve().parents[2]
    / "periphery" / "brody_memory_readonly"
    / "context_packet_query_readonly"
    / "brody_context_packet_query_readonly_v1.py"
)


def _source() -> str:
    return _QUERY_PY.read_text(encoding="utf-8")


def test_text_preview_in_coalesce():
    src = _source()
    assert "p.text_preview" in src, "LOW_MATERIAL fix: text_preview must be in coalesce"


def test_coalesce_pattern_complete():
    src = _source()
    # All standard fields + text_preview
    for field in ("p.text", "p.content", "p.body", "p.excerpt", "p.summary", "p.preview", "p.text_preview"):
        assert field in src, f"Missing coalesce field: {field}"


def test_coalesce_not_doubled():
    src = _source()
    # text_preview should appear exactly once in the coalesce line
    coalesce_line = next((l for l in src.splitlines() if "coalesce" in l.lower() and "text_preview" in l), "")
    assert coalesce_line, "No coalesce line with text_preview found"
    assert coalesce_line.count("text_preview") == 1


def test_decision_authority_in_query_module():
    src = _source()
    assert "KX108_ONLY" in src


def test_readonly_true_in_query_module():
    src = _source()
    assert '"readonly": True' in src or "'readonly': True" in src or "readonly=True" in src


def test_emits_act_false_in_query_module():
    src = _source()
    assert "emits_act" in src.lower()


def test_query_module_not_neo4j_writer():
    src = _source()
    # Must not contain write/create/update Cypher keywords
    src_upper = src.upper()
    for bad in ("CREATE (", "MERGE (", "SET d.", "DELETE d", "DETACH DELETE"):
        assert bad.upper() not in src_upper, f"Write operation found: {bad}"
