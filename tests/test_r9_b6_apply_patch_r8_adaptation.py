from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
TESTS = WORKTREE / "tests"
for p in (SCRIPTS, TESTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_canonical_receipt_replay_v1 as R3
import obsidia_governance_decision_replay_v1 as B5R
import obsidia_realized_state_reconciliation_v1 as B6
from obsidia_pc_capabilities_v2 import pc_v2_apply_patch_execute

from test_r9_b5_obsidure_governed_patch_prepare_adapter import _chain, _patch_alpha, _prepare, v2_world


def _execute(world, prepared):
    return pc_v2_apply_patch_execute(
        prepared,
        prepared["execution_authority_hash"],
        "human-r9-b6-test-authorization",
        stores_base_dir=world["stores"],
        repo_root=world["exec_wt"],
        session_id="r9-b6",
    )


def _prepared(world, patch: str | None = None):
    patch = patch or _patch_alpha()
    proposal, manifest, validation, handoff = _chain(world["base_sha"], patch)
    out = _prepare(world, proposal, manifest, validation, handoff, patch=patch)
    assert out["status"] == "PREPARED_AWAITING_HUMAN_APPROVAL"
    return out, handoff


def _receipt(world, action_evidence_id: str) -> dict:
    p = world["stores"] / "receipts" / f"{action_evidence_id}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_apply_patch_execute_persists_r8_receipt_replay_decision_and_reconciliation(v2_world):
    prepared, handoff = _prepared(v2_world)

    result = _execute(v2_world, prepared)

    assert result["status"] == "EXECUTED_OK"
    assert (v2_world["exec_wt"] / "periphery" / "alpha.txt").read_text(encoding="utf-8") == "alpha v2\n"
    assert result["action_evidence_id"].startswith("aev-")
    assert result["canonical_receipt_store_status"] == CRE.STATUS_STORED

    envelope = _receipt(v2_world, result["action_evidence_id"])
    assert envelope["operation_type"] == "V2_APPLY_PATCH"
    assert envelope["request_ref"]["builder_lineage"]["builder_handoff_id"] == handoff.handoff_id
    assert envelope["execution"]["executor_kind"] == "GIT_APPLY"
    assert envelope["realized_state"]["proof_strength"] == "STRONG"
    assert envelope["replay"]["physical_replay_allowed"] is False

    b3 = R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert b3["replay_verdict"] in {R3.VERDICT_VERIFIED, R3.VERDICT_VERIFIED_WITH_LIMITS}
    b5 = B5R.replay_governance_decision(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert b5["replay_verdict"] == B5R.VERDICT_MATCH
    b6 = B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert b6["reconciliation_status"] == B6.STATUS_MATCH


def test_apply_patch_late_dirty_worktree_aborts_before_dispatch_with_receipt(v2_world):
    prepared, _ = _prepared(v2_world)
    (v2_world["exec_wt"] / "periphery" / "beta.txt").write_text("dirty beta\n", encoding="utf-8")

    result = _execute(v2_world, prepared)

    assert result["status"] == "EXECUTE_REJECTED"
    assert result["action_evidence_id"].startswith("aev-")
    envelope = _receipt(v2_world, result["action_evidence_id"])
    assert envelope["realized_state"]["outcome"] == CRE.OUTCOME_TOCTOU_ABORTED
    assert envelope["realized_state"]["physical_effect_dispatched"] is False
    assert envelope["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
    assert B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])["reconciliation_status"] == B6.STATUS_NOT_REALIZED


def test_apply_patch_tampered_patch_aborts_before_dispatch_with_receipt(v2_world):
    prepared, _ = _prepared(v2_world)
    patch_path = v2_world["stores"] / "v2exec" / f"{prepared['v2_exec_id']}.patch"
    patch_path.write_text(_patch_alpha().replace("alpha v2", "alpha hacked"), encoding="utf-8")

    result = _execute(v2_world, prepared)

    assert result["status"] == "EXECUTE_REJECTED"
    envelope = _receipt(v2_world, result["action_evidence_id"])
    assert envelope["realized_state"]["outcome"] == CRE.OUTCOME_TOCTOU_ABORTED
    assert envelope["realized_state"]["toctou_phase"] == "PATCH_ARTIFACT"
    assert R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])["replay_verdict"] in {
        R3.VERDICT_VERIFIED,
        R3.VERDICT_VERIFIED_WITH_LIMITS,
    }


def test_apply_patch_reconciliation_detects_builder_lineage_and_realized_state_tamper(v2_world):
    prepared, _ = _prepared(v2_world)
    result = _execute(v2_world, prepared)
    rpath = v2_world["stores"] / "receipts" / f"{result['action_evidence_id']}.json"
    envelope = json.loads(rpath.read_text(encoding="utf-8"))
    envelope["realized_state"]["post_state_ref"]["after_digests"]["periphery/alpha.txt"] = prepared["before_digests"]["periphery/alpha.txt"]
    envelope["realized_state"]["post_state_hash"] = CRE.compute_ref_hash(envelope["realized_state"]["post_state_ref"])
    envelope["envelope_hash"] = CRE.compute_envelope_hash(envelope)
    rpath.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

    replay = R3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert replay["replay_verdict"] in {R3.VERDICT_VERIFIED, R3.VERDICT_VERIFIED_WITH_LIMITS}
    rec = B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=v2_world["stores"])
    assert rec["reconciliation_status"] == B6.STATUS_MISMATCH


def test_b5_prepare_still_rejects_scope_widening_before_any_execution(v2_world):
    widened = _patch_alpha().replace("+++ b/periphery/alpha.txt", "+++ b/../outside.txt")
    proposal, manifest, validation, handoff = _chain(v2_world["base_sha"], widened)

    out = _prepare(v2_world, proposal, manifest, validation, handoff, patch=widened)

    assert out["status"] == "PREPARE_REJECTED"
    assert not (v2_world["stores"] / "receipts").exists()
