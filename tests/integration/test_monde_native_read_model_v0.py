"""Real persisted read-model proof; no mocked canonical states."""
import json
from pathlib import Path

import pytest

from periphery.native_ops.monde_native_read_model_v0 import (
    build_monde_native_read_model_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)
from periphery.native_sources.enterprise_office_full_loop_e2e_v0 import (
    run_enterprise_office_full_loop_e2e_v0,
)


def _run(tmp_path: Path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_enterprise_office_full_loop_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
        execution_root=tmp_path / "execution",
    )
    model = build_monde_native_read_model_v0(
        source_runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
        execution_root=tmp_path / "execution",
    )
    return result, model


def test_read_model_shows_only_observed_and_replay_verified_objects(tmp_path):
    result, model = _run(tmp_path)
    assert result["committed_case_count"] == 3
    assert model["schema"] == "MONDE_OBSIDIA_NATIVE_READ_MODEL_V0"
    assert model["readonly"] is True
    assert model["canonical_truth"] is False
    assert model["decision_authority"] == "KX108_ONLY"
    assert model["allowed_to_decide"] is False
    assert model["allowed_to_act"] is False
    assert model["emits_act"] is False
    for kind, expected in (
        ("source", 12),
        ("case", 3),
        ("task", 3),
        ("followup", 3),
    ):
        assert sum(x["kind"] == kind for x in model["entities"]) == expected
        assert model["availability"][kind] == "OBSERVED"
    assert sum(x["kind"] == "receipt" and x.get("receipt_type") == "NATIVE_MUTATION"
               for x in model["entities"]) == 12
    assert sum(x["kind"] == "receipt" and x.get("receipt_type") == "WORLD_ACTION_EXECUTION"
               for x in model["entities"]) == 2
    assert sum(x["kind"] == "world_action" for x in model["entities"]) == 2
    assert model["availability"]["interpretation"] == "UNAVAILABLE"
    assert model["availability"]["provider_binding"] == "UNAVAILABLE"
    assert model["availability"]["action_candidate"] == "UNAVAILABLE"
    assert all("content" not in x or x["kind"] == "source" for x in model["entities"])
    assert all("recipient" not in x and "body" not in x for x in model["entities"])
    assert any(x["type"] == "FOLLOWS_CASE" for x in model["relations"])
    assert any(x["type"] == "TRACKS_TASK" for x in model["relations"])
    assert any(x["type"] == "HAS_RECEIPT" for x in model["relations"])


def test_read_model_is_deterministic_when_persisted_evidence_is_unchanged(tmp_path):
    _run(tmp_path)
    args = dict(
        source_runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
        execution_root=tmp_path / "execution",
    )
    first = build_monde_native_read_model_v0(**args)
    second = build_monde_native_read_model_v0(**args)
    assert first == second
    assert len(first["projection_hash"]) == 64


def test_read_model_missing_store_is_explicit_not_simulated(tmp_path):
    model = build_monde_native_read_model_v0(
        source_runtime_root=tmp_path / "missing-sources",
        native_store_root=tmp_path / "missing-native",
    )
    assert model["entities"] == []
    assert all(v == "UNAVAILABLE" for v in model["availability"].values())
    assert model["readonly"] is True


def test_read_model_tampered_source_packet_fails_closed(tmp_path):
    _run(tmp_path)
    packet = next((tmp_path / "runtime" / "packets").rglob("*.json"))
    data = json.loads(packet.read_text(encoding="utf8"))
    data["content_sha256"] = "0" * 64
    packet.write_text(json.dumps(data), encoding="utf8")
    with pytest.raises(ValueError, match="MONDE_READ_MODEL_PACKET_HASH_MISMATCH"):
        build_monde_native_read_model_v0(
            source_runtime_root=tmp_path / "runtime",
            native_store_root=tmp_path / "native",
        )


def test_read_model_tampered_native_state_fails_closed(tmp_path):
    _run(tmp_path)
    task = next((tmp_path / "native" / "native_tasks").rglob("state.json"))
    data = json.loads(task.read_text(encoding="utf8"))
    data["status"] = "DONE"
    task.write_text(json.dumps(data), encoding="utf8")
    with pytest.raises(ValueError, match="NATIVE_REPLAY_CURRENT_STATE_MISMATCH"):
        build_monde_native_read_model_v0(native_store_root=tmp_path / "native")
