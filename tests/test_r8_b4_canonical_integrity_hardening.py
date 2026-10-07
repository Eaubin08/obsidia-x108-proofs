from __future__ import annotations

import copy
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
import obsidia_canonical_receipt_replay_v1 as RPL
import test_r8_b3_evidence_only_replay as F


def _make(tmp_path, name="a", *, outcome=CRE.OUTCOME_SUCCESS, mutation=True, op=F.OP_SET_CHECKED, cap=F.CAP_SET_CHECKED):
    return F._store_envelope(tmp_path / name / "s", outcome=outcome, mutation=mutation, op=op, cap=cap)


def _path(stores, env):
    return stores["receipts"] / f"{env['action_evidence_id']}.json"


def _rewrite(stores, env, payload):
    _path(stores, env).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _replay(tmp_path, name, env):
    return RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / name / "s")


def _tamper_bound_field(tmp_path, name, field_path, value, *, outcome=CRE.OUTCOME_SUCCESS, mutation=True):
    env, stores = _make(tmp_path, name, outcome=outcome, mutation=mutation)
    data = copy.deepcopy(env)
    cur = data
    for key in field_path[:-1]:
        cur = cur[key]
    cur[field_path[-1]] = value
    _rewrite(stores, env, data)
    result = _replay(tmp_path, name, env)
    assert result["replay_verdict"] == RPL.VERDICT_TAMPERED
    return result


def test_bound_envelope_field_mutations_are_detected_for_success_block_and_uncertain(tmp_path):
    fields = [
        (["capability"], "PC_V2_OTHER"),
        (["operation_type"], "V2_OTHER"),
        (["prepare", "descriptor_ref"], "v2x-other"),
        (["prepare", "descriptor_hash"], "0" * 64),
        (["authorization", "execution_authority_hash"], "1" * 64),
        (["authorization", "approval_id"], "apv-other"),
        (["authorization", "kx108_pre_decision_record_id"], "kx-other"),
        (["authorization", "kx108_verdict"], "BLOCK"),
        (["authorization", "binder_verdict_status"], "REJECTED_INLINE"),
        (["execution", "executor_input_hash"], "2" * 64),
        (["realized_state", "outcome"], CRE.OUTCOME_NOOP),
        (["realized_state", "physical_effect_dispatched"], False),
        (["realized_state", "uncertainty_state"], "CHANGED"),
        (["replay", "physical_replay_allowed"], True),
        (["privacy", "plaintext_sensitive_data_present"], True),
    ]
    for i, (path, value) in enumerate(fields):
        _tamper_bound_field(tmp_path, f"success{i}", path, value)
    _tamper_bound_field(tmp_path, "block", ["realized_state", "physical_effect_dispatched"], True, outcome=CRE.OUTCOME_KX108_BLOCK, mutation=False)
    env, stores = _make(tmp_path, "uncertain", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)
    data = copy.deepcopy(env); data["realized_state"]["uncertainty_reason"] = "CHANGED"
    _rewrite(stores, env, data)
    assert _replay(tmp_path, "uncertain", env)["replay_verdict"] == RPL.VERDICT_TAMPERED


def test_action_id_swap_and_filename_payload_mismatch_are_detected(tmp_path):
    env_a, stores_a = _make(tmp_path, "a")
    env_b, _ = _make(tmp_path, "b", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)
    _rewrite(stores_a, env_a, env_b)
    result = _replay(tmp_path, "a", env_a)
    assert result["replay_verdict"] == RPL.VERDICT_TAMPERED
    assert "ACTION_EVIDENCE_ID_PATH_PAYLOAD_MISMATCH" in result["evidence_conflicts"]

    env, stores = _make(tmp_path, "swap")
    data = copy.deepcopy(env)
    data["action_evidence_id"] = "aev-" + "1" * 32
    data["envelope_hash"] = CRE.compute_envelope_hash(data)
    _rewrite(stores, env, data)
    assert _replay(tmp_path, "swap", env)["replay_verdict"] == RPL.VERDICT_TAMPERED


def test_cross_artifact_substitution_descriptor_approval_kx_and_realized_state(tmp_path):
    env_a, stores_a = _make(tmp_path, "a", outcome=CRE.OUTCOME_REALIZED_STATE_MISMATCH, mutation=True)
    env_b, stores_b = _make(tmp_path, "b", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)

    # Descriptor B bytes under descriptor A path: individually valid JSON, wrong relationship.
    desc_b = (stores_b["v2exec"] / f"{env_b['prepare']['descriptor_ref']}.json").read_text(encoding="utf-8")
    (stores_a["v2exec"] / f"{env_a['prepare']['descriptor_ref']}.json").write_text(desc_b, encoding="utf-8")
    assert _replay(tmp_path, "a", env_a)["replay_verdict"] == RPL.VERDICT_TAMPERED

    env_a, stores_a = _make(tmp_path, "ap_a")
    env_b, stores_b = _make(tmp_path, "ap_b", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)
    ap_b = (stores_b["approval"] / "approvals" / env_b["authorization"]["approval_id"] / "approval.json").read_text(encoding="utf-8")
    (stores_a["approval"] / "approvals" / env_a["authorization"]["approval_id"] / "approval.json").write_text(ap_b, encoding="utf-8")
    assert _replay(tmp_path, "ap_a", env_a)["replay_verdict"] == RPL.VERDICT_CONFLICTING

    env_a, stores_a = _make(tmp_path, "kx_a")
    env_b, stores_b = _make(tmp_path, "kx_b", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)
    kx_b = (stores_b["kxpre"] / f"{env_b['authorization']['kx108_pre_decision_record_id']}.json").read_text(encoding="utf-8")
    (stores_a["kxpre"] / f"{env_a['authorization']['kx108_pre_decision_record_id']}.json").write_text(kx_b, encoding="utf-8")
    assert _replay(tmp_path, "kx_a", env_a)["replay_verdict"] == RPL.VERDICT_CONFLICTING

    env, stores = _make(tmp_path, "rs", outcome=CRE.OUTCOME_REALIZED_STATE_MISMATCH, mutation=True)
    data = copy.deepcopy(env)
    data["realized_state"]["post_state_ref"] = {"checked": False, "element_identity_hash": "other-action"}
    data["realized_state"]["post_state_hash"] = CRE.compute_ref_hash(data["realized_state"]["post_state_ref"])
    data["envelope_hash"] = CRE.compute_envelope_hash(data)
    _rewrite(stores, env, data)
    result = _replay(tmp_path, "rs", env)
    assert result["replay_verdict"] == RPL.VERDICT_CONFLICTING
    assert "REALIZED_STATE_IDENTITY_MISMATCH" in result["evidence_conflicts"]


def test_create_once_duplicate_and_conflicting_overwrite_semantics(tmp_path):
    env, stores = _make(tmp_path, "dup")
    assert CRE.store_canonical_receipt_envelope(env, stores["receipts"])["status"] == CRE.STATUS_IDEMPOTENT
    changed = copy.deepcopy(env)
    changed["created_at"] = "2026-10-07T00:00:09+00:00"
    changed["envelope_hash"] = CRE.compute_envelope_hash(changed)
    assert CRE.store_canonical_receipt_envelope(changed, stores["receipts"])["status"] == CRE.STATUS_IMMUTABILITY_VIOLATION


def test_truncated_empty_and_malformed_envelopes_fail_closed(tmp_path):
    for name, payload in (("trunc", '{"schema_version":'), ("empty", ""), ("bad", "not-json")):
        env, stores = _make(tmp_path, name)
        _path(stores, env).write_text(payload, encoding="utf-8")
        result = _replay(tmp_path, name, env)
        assert result["replay_verdict"] == RPL.VERDICT_TAMPERED
        assert result["receipt_found"] is True


def test_success_negative_and_uncertain_integrity_all_use_same_replay_oracle(tmp_path):
    cases = [
        ("success", CRE.OUTCOME_SUCCESS, True, F.OP_SET_CHECKED, F.CAP_SET_CHECKED),
        ("noop", CRE.OUTCOME_NOOP, False, F.OP_SET_CHECKED, F.CAP_SET_CHECKED),
        ("block", CRE.OUTCOME_KX108_BLOCK, False, F.OP_SET_CHECKED, F.CAP_SET_CHECKED),
        ("mismatch", CRE.OUTCOME_REALIZED_STATE_MISMATCH, True, F.OP_SET_CHECKED, F.CAP_SET_CHECKED),
        ("uncertain", CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, True, F.OP_SUBMIT, F.CAP_SUBMIT),
    ]
    for name, outcome, mutation, op, cap in cases:
        env, _ = _make(tmp_path, name, outcome=outcome, mutation=mutation, op=op, cap=cap)
        result = _replay(tmp_path, name, env)
        assert result["replay_verdict"] == RPL.VERDICT_VERIFIED_WITH_LIMITS


def test_replay_static_safety_still_has_zero_physical_executor_surface():
    src = (SCRIPTS / "obsidia_canonical_receipt_replay_v1.py").read_text(encoding="utf-8")
    banned = ["JarJarBrowserExecutor", "playwright", "requests", "httpx", "socket", "subprocess", "openai", "anthropic", "store_canonical_receipt_envelope", "store_approval_artifact", "store_kx108_decision_record", "write_text", "unlink", "mkdir", "replace", "rename"]
    for token in banned:
        assert token not in src
