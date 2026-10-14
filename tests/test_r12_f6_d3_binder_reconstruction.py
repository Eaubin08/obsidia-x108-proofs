from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for _p in (_ROOT / "scripts", _ROOT / "tests"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import obsidia_canonical_receipt_replay_v1 as R3

from test_r9_b6_apply_patch_r8_adaptation import _execute, _prepared, v2_world  # noqa: F401


def test_real_apply_patch_binder_decision_is_independently_reconstructed(v2_world):
    prepared, _ = _prepared(v2_world)
    result = _execute(v2_world, prepared)
    assert result["status"] == "EXECUTED_OK"

    replay = R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert replay["KX108_ref_valid"] == R3.YES
    assert replay["binder_replay_status"] == "RECONSTRUCTED_MATCH"
    assert replay["replay_verdict"] == R3.VERDICT_VERIFIED


def test_reconstruction_mismatch_is_not_verified(v2_world, monkeypatch):
    prepared, _ = _prepared(v2_world)
    result = _execute(v2_world, prepared)

    import sigma.protocols as protocols
    real = protocols.run_tooling_build_pipeline

    def drifted(state):
        decision = real(state)
        decision.reason_code = "DRIFTED_REASON"
        return decision

    monkeypatch.setattr(protocols, "run_tooling_build_pipeline", drifted)
    replay = R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert replay["binder_replay_status"] == "RECONSTRUCTION_MISMATCH"
    assert replay["replay_verdict"] != R3.VERDICT_VERIFIED
    assert "BINDER_RECONSTRUCTION_MISMATCH" in replay["evidence_conflicts"]
