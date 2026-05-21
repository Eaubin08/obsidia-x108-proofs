"""
Test: Brody Freeze Metrics Snapshot Runtime
============================================
Tests the build_freeze_metrics_snapshot() function:
  - Snapshot is produced
  - All required sections are present
  - No invented metrics (NOT_FOUND_IN_FREEZE_SOURCES for unknowns)
  - Boundary invariants are enforced
"""
import pytest
from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot


def test_snapshot_produced():
    """Snapshot should return a dict with status PASS."""
    snap = build_freeze_metrics_snapshot()
    assert isinstance(snap, dict)
    assert snap["status"] == "BRODY_FREEZE_METRICS_SNAPSHOT_RUNTIME_PASS"
    assert snap["source_mode"] == "FREEZE_SOURCED_ONLY"


def test_snapshot_has_all_sections():
    """All required sections must be present."""
    snap = build_freeze_metrics_snapshot()
    required_sections = [
        "context_packet_chain",
        "memory_pipeline",
        "operator_loop",
        "x108_boundary",
        "runtime_llm",
        "x108_proof_state",
        "not_found_in_freeze_sources",
    ]
    for section in required_sections:
        assert section in snap, f"Missing section: {section}"


def test_context_packet_chain_structure():
    """ContextPacket chain must have QUERY, CONSUMER, ENGINE, HYDRATION."""
    snap = build_freeze_metrics_snapshot()
    chain = snap["context_packet_chain"]
    assert "query" in chain
    assert "consumer" in chain
    assert "engine" in chain
    assert "hydration" in chain
    assert "status" in chain
    assert chain["status"] in ("CHAIN_PASS", "CHAIN_PARTIAL")


def test_operator_loop_structure():
    """Operator loop must contain all 7 components."""
    snap = build_freeze_metrics_snapshot()
    op = snap["operator_loop"]
    components = [
        "command_gate",
        "human_command_packet",
        "control_loop",
        "execution_line",
        "execution_receipt",
        "handoff_line",
        "final_baseline",
    ]
    for c in components:
        assert c in op, f"Missing operator_loop component: {c}"
    assert "status" in op
    # Status should be N/7 PASS
    assert "PASS" in op["status"]


def test_operator_loop_brody_execute_disabled():
    """Brody must NOT be allowed to execute."""
    snap = build_freeze_metrics_snapshot()
    op = snap["operator_loop"]
    assert op["brody_execute_allowed"] is False, "Brody should not be allowed to execute"


def test_x108_boundary():
    """X108 boundary must enforce KX108_ONLY and no mutations."""
    snap = build_freeze_metrics_snapshot()
    x108 = snap["x108_boundary"]
    assert x108["decision_authority"] == "KX108_ONLY"
    assert x108["emits_act"] is False
    assert x108["emits_verdict"] is False
    assert x108["kernel_mutation"] is False


def test_memory_pipeline_no_writes():
    """Memory pipeline must have all writes disabled."""
    snap = build_freeze_metrics_snapshot()
    mem = snap["memory_pipeline"]
    assert mem["memory_write"] is False
    assert mem["graphiti_write"] is False
    assert mem["neo4j_write"] is False


def test_runtime_llm_is_obsidien():
    """Runtime LLM must be marked as Brody LLM obsidien."""
    snap = build_freeze_metrics_snapshot()
    llm = snap["runtime_llm"]
    assert llm["brody_llm_obsidien"] is True, "Brody must be LLM obsidien"


def test_not_found_section_exists():
    """NOT_FOUND section must exist and contain known-unavailable metrics."""
    snap = build_freeze_metrics_snapshot()
    nf = snap["not_found_in_freeze_sources"]
    assert isinstance(nf, dict)
    # At minimum, OS Trad/IR/Reverse should be NOT_FOUND
    assert len(nf) > 0, "Should have at least some NOT_FOUND entries"


def test_no_invented_graphiti_counts():
    """Graphiti counts should NOT be invented — must be NOT_FOUND_IN_FREEZE_SOURCES."""
    snap = build_freeze_metrics_snapshot()
    nf = snap["not_found_in_freeze_sources"]
    # If Graphiti count keys exist in not_found, they must be NOT_FOUND
    for key in ["graphiti_v20_nodes", "graphiti_v20_rels", "graphiti_v20_entity_counts"]:
        if key in nf:
            assert nf[key] == "NOT_FOUND_IN_FREEZE_SOURCES", f"{key} should NOT be invented"


def test_no_invented_neo4j_counts():
    """Neo4j counts should NOT be invented."""
    snap = build_freeze_metrics_snapshot()
    nf = snap["not_found_in_freeze_sources"]
    if "neo4j_brody_memory_doc_node_count" in nf:
        assert nf["neo4j_brody_memory_doc_node_count"] == "NOT_FOUND_IN_FREEZE_SOURCES"


def test_no_invented_os_trad_ir_reverse():
    """OS Trad / IR / Reverse runtimes must be NOT_FOUND."""
    snap = build_freeze_metrics_snapshot()
    nf = snap["not_found_in_freeze_sources"]
    for key in ["os_trad_runtime", "ir_runtime", "reverse_os_runtime"]:
        if key in nf:
            assert nf[key] == "NOT_FOUND_IN_FREEZE_SOURCES", f"{key} should NOT be invented"


def test_snapshot_boundary_invariants():
    """Top-level snapshot must carry boundary invariants."""
    snap = build_freeze_metrics_snapshot()
    assert snap["readonly"] is True
    assert snap["memory_write"] is False
    assert snap["graphiti_write"] is False
    assert snap["neo4j_write"] is False
    assert snap["emits_act"] is False
    assert snap["emits_verdict"] is False
    assert snap["kernel_mutation"] is False
    assert snap["decision_authority"] == "KX108_ONLY"


def test_pointer_file_count():
    """Should have scanned some CURRENT_BRODY_*.txt files."""
    snap = build_freeze_metrics_snapshot()
    assert snap["pointer_file_count"] > 0, "Should have scanned at least one pointer file"


def test_source_files_scanned():
    """Source files list must not be empty."""
    snap = build_freeze_metrics_snapshot()
    assert len(snap["source_files_scanned"]) > 0
