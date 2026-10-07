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
import obsidia_governance_decision_replay_v1 as GDR
import obsidia_kx108_decision_store as DS
import test_r8_b3_evidence_only_replay as F


def _make(tmp_path, name, *, outcome=CRE.OUTCOME_SUCCESS, mutation=True, gate="ALLOW"):
    return F._store_envelope(tmp_path / name / "s", outcome=outcome, mutation=mutation, gate=gate)


def _replay(tmp_path, name, env):
    return GDR.replay_governance_decision(env["action_evidence_id"], stores_base_dir=tmp_path / name / "s")


def _receipt_path(stores, env):
    return stores["receipts"] / f"{env['action_evidence_id']}.json"


def test_allow_hold_and_block_decision_replay_match(tmp_path):
    cases = [
        ("allow", CRE.OUTCOME_SUCCESS, True, "ALLOW"),
        ("hold", CRE.OUTCOME_KX108_HOLD, False, "HOLD"),
        ("block", CRE.OUTCOME_KX108_BLOCK, False, "BLOCK"),
    ]
    for name, outcome, mutation, gate in cases:
        env, _ = _make(tmp_path, name, outcome=outcome, mutation=mutation, gate=gate)
        result = _replay(tmp_path, name, env)
        assert result["replay_verdict"] == GDR.VERDICT_MATCH
        assert result["historical_kx108_verdict"] == gate
        assert result["replayed_kx108_verdict"] == gate
        assert result["kx108_match"] == GDR.YES
        assert result["binder_match"] == GDR.PARTIAL
        assert result["EAH_valid"] == GDR.YES
        assert result["approval_valid"] == GDR.YES
        assert result["deterministic_inputs_hash"]


def test_execution_outcome_mismatch_does_not_change_governance_replay(tmp_path):
    env, _ = _make(tmp_path, "mismatch", outcome=CRE.OUTCOME_REALIZED_STATE_MISMATCH, mutation=True, gate="ALLOW")
    result = _replay(tmp_path, "mismatch", env)
    assert result["replay_verdict"] == GDR.VERDICT_MATCH
    assert result["historical_kx108_verdict"] == "ALLOW"
    assert result["replayed_kx108_verdict"] == "ALLOW"


def test_repeated_replay_is_deterministic(tmp_path):
    env, _ = _make(tmp_path, "det", outcome=CRE.OUTCOME_SUCCESS, mutation=True, gate="ALLOW")
    a = _replay(tmp_path, "det", env)
    b = _replay(tmp_path, "det", env)
    assert a == b


def test_descriptor_eah_approval_kx_and_binder_tamper_fail_closed(tmp_path):
    env, stores = _make(tmp_path, "desc")
    dpath = stores["v2exec"] / f"{env['prepare']['descriptor_ref']}.json"
    desc = json.loads(dpath.read_text(encoding="utf-8")); desc["descriptor"]["semantic_risk"] = "HIGH"
    dpath.write_text(json.dumps(desc, sort_keys=True), encoding="utf-8")
    assert _replay(tmp_path, "desc", env)["replay_verdict"] == GDR.VERDICT_TAMPERED

    env, stores = _make(tmp_path, "approval")
    apath = stores["approval"] / "approvals" / env["authorization"]["approval_id"] / "approval.json"
    appr = json.loads(apath.read_text(encoding="utf-8")); appr["execution_authority_hash"] = "0" * 64
    apath.write_text(json.dumps(appr), encoding="utf-8")
    assert _replay(tmp_path, "approval", env)["replay_verdict"] == GDR.VERDICT_TAMPERED

    env, stores = _make(tmp_path, "kx")
    kpath = stores["kxpre"] / f"{env['authorization']['kx108_pre_decision_record_id']}.json"
    kx = json.loads(kpath.read_text(encoding="utf-8")); kx["x108_gate"] = "BLOCK"
    kpath.write_text(json.dumps(kx), encoding="utf-8")
    assert _replay(tmp_path, "kx", env)["replay_verdict"] == GDR.VERDICT_TAMPERED

    env, stores = _make(tmp_path, "binder")
    rpath = _receipt_path(stores, env)
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["authorization"]["binder_verdict_status"] = "UNKNOWN_BINDER"
    rec["envelope_hash"] = CRE.compute_envelope_hash(rec)
    rpath.write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    result = _replay(tmp_path, "binder", env)
    assert result["replay_verdict"] == GDR.VERDICT_MISMATCH
    assert result["binder_match"] == GDR.NO


def test_missing_historical_inputs_are_incomplete_not_reconstructed(tmp_path):
    env, stores = _make(tmp_path, "missing")
    (stores["kxpre"] / f"{env['authorization']['kx108_pre_decision_record_id']}.json").unlink()
    result = _replay(tmp_path, "missing", env)
    assert result["replay_verdict"] == GDR.VERDICT_INCOMPLETE
    assert "DECISION_RECORD_MISSING" in result["missing_inputs"]


def test_current_runtime_policy_drift_is_not_used_when_version_unavailable(tmp_path, monkeypatch):
    env, _ = _make(tmp_path, "drift")
    def boom(*_a, **_k):
        raise AssertionError("live KX108 persistence path must not be called")
    monkeypatch.setattr(DS, "run_and_persist_kx108_pre_execution_decision", boom)
    result = _replay(tmp_path, "drift", env)
    assert result["replay_verdict"] == GDR.VERDICT_MATCH
    assert result["current_runtime_policy_dependence"] == GDR.NO
    assert result["config_version_bound"] == GDR.NO
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" in result["evidence_limits"]


def test_historical_policy_version_when_present_is_bound_in_replay_inputs(tmp_path):
    env, stores = _make(tmp_path, "versioned")
    kpath = stores["kxpre"] / f"{env['authorization']['kx108_pre_decision_record_id']}.json"
    kx = json.loads(kpath.read_text(encoding="utf-8"))
    kx["canonical_envelope"]["policy_version"] = "kx-policy-r8b5"
    kx["decision_record_hash"] = DS.compute_kx108_decision_record_hash(kx)
    kpath.write_text(json.dumps(kx, indent=2, sort_keys=True), encoding="utf-8")
    rpath = _receipt_path(stores, env)
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["authorization"]["kx108_pre_decision_record_hash"] = kx["decision_record_hash"]
    rec["envelope_hash"] = CRE.compute_envelope_hash(rec)
    rpath.write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    result = _replay(tmp_path, "versioned", env)
    assert result["replay_verdict"] == GDR.VERDICT_MATCH
    assert result["config_version_bound"] == GDR.YES
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" not in result["evidence_limits"]


def test_static_decision_replay_has_no_executor_network_world_or_write_surface():
    src = (SCRIPTS / "obsidia_governance_decision_replay_v1.py").read_text(encoding="utf-8")
    banned = [
        "JarJarBrowserExecutor", "playwright", "requests", "httpx", "socket", "subprocess",
        "openai", "anthropic", "run_and_persist_kx108_pre_execution_decision",
        "store_kx108_decision_record", "store_approval_artifact", "write_text", "unlink",
        "mkdir", "replace", "rename", "set_checkbox", "submit_get_navigation",
    ]
    for token in banned:
        assert token not in src
    import inspect
    sig = inspect.signature(GDR.replay_governance_decision)
    assert "executor" not in sig.parameters
    assert "state_provider" not in sig.parameters
