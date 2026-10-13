from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for _p in (_ROOT / "scripts", _ROOT / "tests"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import obsidia_canonical_receipt_replay_v1 as R3
import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_governance_decision_replay_v1 as GDR
import obsidia_kx108_decision_store as DS

from test_r9_b6_apply_patch_r8_adaptation import _execute, _prepared, v2_world  # noqa: F401


def test_real_apply_patch_binder_decision_is_independently_reconstructed(v2_world):
    prepared, _ = _prepared(v2_world)
    result = _execute(v2_world, prepared)
    assert result["status"] == "EXECUTED_OK"

    replay = R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert replay["KX108_ref_valid"] == R3.YES
    assert replay["binder_replay_status"] == "RECONSTRUCTED_MATCH"
    assert replay["replay_verdict"] == R3.VERDICT_VERIFIED

    governance = GDR.replay_governance_decision(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert governance["replay_verdict"] == GDR.VERDICT_MATCH
    assert governance["replayed_binder_status"] == "RECONSTRUCTED_MATCH"
    assert governance["binder_match"] == GDR.YES
    assert governance["binder_reconstruction_source"] == "R8_D3_CANONICAL_RECEIPT_REPLAY"
    assert "BINDER_INLINE_STATUS_ONLY_NOT_SEPARATELY_PERSISTED" not in governance["evidence_limits"]
    assert governance["policy_identity_status"] == "MATCH"
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" not in governance["evidence_limits"]
    assert "KX108_POLICY_FINGERPRINT_BOUNDED_COVERAGE" in governance["evidence_limits"]


def test_binder_reconstruction_does_not_clear_missing_policy_identity(v2_world):
    prepared, _ = _prepared(v2_world)
    result = _execute(v2_world, prepared)

    stores = v2_world["stores"]
    receipt_path = stores / "receipts" / f"{result['action_evidence_id']}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    auth = receipt["authorization"]
    kx_path = stores / "kxpre" / f"{auth['kx108_pre_decision_record_id']}.json"
    kx = json.loads(kx_path.read_text(encoding="utf-8"))
    kx["canonical_envelope"].pop("policy_identity", None)
    kx["canonical_envelope"].pop("policy_content_hash", None)
    kx["canonical_envelope"].pop("policy_version", None)
    kx["decision_record_hash"] = DS.compute_kx108_decision_record_hash(kx)
    kx_path.write_text(json.dumps(kx, indent=2, sort_keys=True), encoding="utf-8")
    receipt["authorization"]["kx108_pre_decision_record_hash"] = kx["decision_record_hash"]
    receipt["envelope_hash"] = CRE.compute_envelope_hash(receipt)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")

    governance = GDR.replay_governance_decision(result["action_evidence_id"], stores_base_dir=stores)
    assert governance["replay_verdict"] == GDR.VERDICT_MATCH
    assert governance["replayed_binder_status"] == "RECONSTRUCTED_MATCH"
    assert governance["binder_match"] == GDR.YES
    assert governance["config_version_bound"] == GDR.NO
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" in governance["evidence_limits"]


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
