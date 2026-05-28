import os
import pytest

from periphery.brody_memory_readonly.neo4j_brody_guide_bridge_readonly.brody_neo4j_guide_bridge_readonly_v1 import (
    BOUNDARY,
    MANUAL_NEO4J_WRITE_CONFIRMATION,
    MANUAL_NEO4J_WRITE_ENV,
    import_records,
    require_manual_neo4j_write_confirmation,
)


def test_f29_1_manual_neo4j_write_guard_blocks_without_env_and_token(tmp_path, monkeypatch):
    monkeypatch.delenv(MANUAL_NEO4J_WRITE_ENV, raising=False)

    records = tmp_path / "records.jsonl"
    records.write_text('{"id":"x","text_preview":"hello"}\n', encoding="utf-8")

    with pytest.raises(RuntimeError, match="MANUAL_NEO4J_WRITE_BLOCKED"):
        import_records(records, batch_size=1)


def test_f29_1_manual_neo4j_write_guard_blocks_with_only_env(monkeypatch):
    monkeypatch.setenv(MANUAL_NEO4J_WRITE_ENV, MANUAL_NEO4J_WRITE_CONFIRMATION)

    with pytest.raises(RuntimeError, match="MANUAL_NEO4J_WRITE_BLOCKED"):
        require_manual_neo4j_write_confirmation(confirm_manual_write="")


def test_f29_1_manual_neo4j_write_guard_allows_only_double_confirmation(monkeypatch):
    monkeypatch.setenv(MANUAL_NEO4J_WRITE_ENV, MANUAL_NEO4J_WRITE_CONFIRMATION)

    assert require_manual_neo4j_write_confirmation(
        confirm_manual_write=MANUAL_NEO4J_WRITE_CONFIRMATION
    ) is True


def test_f29_1_boundary_declares_manual_write_surface_not_runtime_execution():
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert BOUNDARY["readonly"] is True
    assert BOUNDARY["runtime_readonly"] is True
    assert BOUNDARY["manual_write_surface"] is True
    assert BOUNDARY["manual_operator_required"] is True
    assert BOUNDARY["manual_write_guard_required"] is True
    assert BOUNDARY["allowed_to_decide"] is False
    assert BOUNDARY["emits_act"] is False
    assert BOUNDARY["emits_verdict"] is False
    assert BOUNDARY["runtime_execute"] is False
    assert BOUNDARY["kernel_binding"] is False
    assert BOUNDARY["x108_runtime_binding"] is False
    assert BOUNDARY["x108_merge"] is False
    assert BOUNDARY["kernel_mutation"] is False
    assert BOUNDARY["x108_mutation"] is False
