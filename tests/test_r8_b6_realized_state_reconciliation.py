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
import obsidia_realized_state_reconciliation_v1 as REC
import test_r8_b3_evidence_only_replay as F


def _make(tmp_path, name, *, outcome=CRE.OUTCOME_SUCCESS, mutation=True, gate="ALLOW", op=F.OP_SET_CHECKED, cap=F.CAP_SET_CHECKED):
    return F._store_envelope(tmp_path / name / "s", outcome=outcome, mutation=mutation, gate=gate, op=op, cap=cap)


def _replay(tmp_path, name, env):
    return REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / name / "s")


def _receipt_path(stores, env):
    return stores["receipts"] / f"{env['action_evidence_id']}.json"


def _rewrite_receipt(path: Path, data: dict) -> None:
    data["envelope_hash"] = CRE.compute_envelope_hash(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _store_custom(base: Path, *, operation: str, capability: str, descriptor: dict, request_ref: dict, realized_state: dict, execution: dict | None = None):
    stores = F._stores(base)
    v2id, eah, dh, descriptor = F._persist_descriptor(stores, op=operation, descriptor=descriptor)
    child = "chd-r8b6-" + F._sha(v2id)[:8]
    mh = F._sha(json.dumps(descriptor, sort_keys=True))[:16]
    approval = F._store_approval(stores, v2id=v2id, child=child, eah=eah)
    kx = F._store_kx(stores, v2id=v2id, child=child, eah=eah, approval_id=approval["approval_id"], dh=dh, mh=mh)
    auth = {
        "execution_authority_hash": eah,
        "approval_id": approval["approval_id"],
        "approval_status": approval["approval_status"],
        "approved_by": approval["approved_by"],
        "approval_record_hash": approval["approval_record_hash"],
        "kx108_pre_decision_record_id": kx["decision_record_id"],
        "kx108_pre_decision_record_hash": kx["decision_record_hash"],
        "kx108_verdict": "ALLOW",
        "binder_verdict_status": "OBSERVED_INLINE_NOT_SEPARATELY_PERSISTED",
        "binder_verdict_ref": "NOT_SEPARATELY_PERSISTED",
    }
    session_ref = {"session_id": "sess-r8b6", "v2_exec_id": v2id, "child_id": child}
    env = CRE.build_canonical_receipt_envelope(
        capability=capability,
        operation_type=operation,
        request_ref=request_ref,
        session_ref=session_ref,
        action_identity={
            "schema_version": CRE.SCHEMA_VERSION,
            "capability": capability,
            "operation_type": operation,
            "request_ref": request_ref,
            "session_ref": session_ref,
            "descriptor_hash": dh,
            "execution_authority_hash": eah,
        },
        prepare={"descriptor_ref": v2id, "descriptor_hash": dh, "physical_state_anchor": descriptor.get("physical_state_anchor", "psa-r8b6"), "state_anchor_kind": "PHYSICAL_PRE_STATE", "manifest_hash": mh},
        authorization=auth,
        execution=execution or {"executor_kind": "JARJAR", "executor_backend": "BrowserBackend", "executor_operation": "test", "executor_status": "INVOKED", "executor_input_ref": request_ref, "executor_input_hash": CRE.compute_ref_hash(request_ref), "physical_effect_dispatched": realized_state.get("physical_effect_dispatched"), "mutation_performed": realized_state.get("mutation_performed"), "execution_state": realized_state.get("execution_state", "POSTCONDITION_CONFIRMED")},
        realized_state=realized_state,
        receipt={"existing_runtime_receipt_id": "pcrcp-r8b6", "existing_receipt_hash": F._sha("runtime-r8b6"), "existing_receipt_ref": "runtime_result.receipt"},
        replay={"physical_replay_allowed": False, "evidence_replay_allowed": True, "automatic_retry": False},
        privacy={"redaction_policy": "HASHES_AND_REFS_ONLY", "plaintext_sensitive_data_present": False},
    )
    assert CRE.store_canonical_receipt_envelope(env, stores["receipts"])["status"] == CRE.STATUS_STORED
    return env, stores


def test_checkbox_match_noop_and_mismatch(tmp_path):
    descriptor = {
        "operation_type": "V2_BROWSER_SET_CHECKED",
        "public_action": "BROWSER_SET_CHECKED",
        "selector": "input#agree",
        "target_checked": True,
        "physical_state_anchor": "psa-check",
    }
    post = {"checked": True, "element_identity_hash": "element-meta"}
    env, _ = _store_custom(
        tmp_path / "match" / "s",
        operation="V2_BROWSER_SET_CHECKED",
        capability="PC_V2_BROWSER_SET_CHECKED_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_SET_CHECKED", "selector_hash": "sel", "target_checked": True},
        realized_state={"outcome": CRE.OUTCOME_SUCCESS, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": True, "proof_strength": "STRONG", "realized_state_verified": True, "mutation_performed": True, "post_state_hash": CRE.compute_ref_hash(post), "post_state_ref": post, "execution_state": "POSTCONDITION_CONFIRMED", "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    assert REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "match" / "s")["reconciliation_status"] == REC.STATUS_MATCH

    env, _ = _store_custom(
        tmp_path / "noop" / "s",
        operation="V2_BROWSER_SET_CHECKED",
        capability="PC_V2_BROWSER_SET_CHECKED_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_SET_CHECKED", "selector_hash": "sel", "target_checked": True},
        realized_state={"outcome": CRE.OUTCOME_NOOP, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": False, "proof_strength": "STRONG", "realized_state_verified": True, "mutation_performed": False, "post_state_hash": CRE.compute_ref_hash(post), "post_state_ref": post, "execution_state": "POSTCONDITION_CONFIRMED", "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    result = REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "noop" / "s")
    assert result["reconciliation_status"] == REC.STATUS_NOOP_CONFIRMED

    post_bad = {"checked": False, "element_identity_hash": "element-meta"}
    env, _ = _store_custom(
        tmp_path / "mismatch" / "s",
        operation="V2_BROWSER_SET_CHECKED",
        capability="PC_V2_BROWSER_SET_CHECKED_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_SET_CHECKED", "selector_hash": "sel", "target_checked": True},
        realized_state={"outcome": CRE.OUTCOME_REALIZED_STATE_MISMATCH, "failure_stage": CRE.STAGE_POST_OBSERVATION, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": True, "proof_strength": "STRONG", "realized_state_verified": False, "mutation_performed": True, "post_state_hash": CRE.compute_ref_hash(post_bad), "post_state_ref": post_bad, "execution_state": CRE.OUTCOME_REALIZED_STATE_MISMATCH, "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    result = REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "mismatch" / "s")
    assert result["reconciliation_status"] == REC.STATUS_MISMATCH
    assert result["integrity_replay_verdict"] in {"VERIFIED", "VERIFIED_WITH_LIMITS"}


def test_field_value_match_and_hash_mismatch_without_plaintext(tmp_path):
    target = F._sha("secret")
    descriptor = {
        "operation_type": "V2_BROWSER_SET_FIELD_VALUE",
        "public_action": "BROWSER_SET_FIELD_VALUE",
        "selector": "input#contact",
        "target_value_sha256": target,
        "target_value_length": 6,
        "physical_state_anchor": "psa-field",
    }
    post = {"post_value_sha256": target, "post_value_length": 6, "field_identity_hash": "field-meta"}
    env, _ = _store_custom(
        tmp_path / "field" / "s",
        operation="V2_BROWSER_SET_FIELD_VALUE",
        capability="PC_V2_BROWSER_SET_FIELD_VALUE_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_SET_FIELD_VALUE", "selector_hash": "sel", "target_value_sha256": target, "target_value_length": 6},
        realized_state={"outcome": CRE.OUTCOME_SUCCESS, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": True, "proof_strength": "STRONG", "realized_state_verified": True, "mutation_performed": True, "post_state_hash": CRE.compute_ref_hash(post), "post_state_ref": post, "execution_state": "POSTCONDITION_CONFIRMED", "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    result = REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "field" / "s")
    assert result["reconciliation_status"] == REC.STATUS_MATCH
    assert "secret" not in json.dumps(result, sort_keys=True)

    rpath = tmp_path / "field" / "s" / "receipts" / f"{env['action_evidence_id']}.json"
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["realized_state"]["post_state_ref"]["post_value_sha256"] = F._sha("other")
    rec["realized_state"]["post_state_hash"] = CRE.compute_ref_hash(rec["realized_state"]["post_state_ref"])
    _rewrite_receipt(rpath, rec)
    assert REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "field" / "s")["reconciliation_status"] == REC.STATUS_MISMATCH


def test_navigation_match_and_post_url_mismatch(tmp_path):
    descriptor = {"operation_type": "V2_BROWSER_NAVIGATE", "public_action": "BROWSER_NAVIGATE", "requested_url": "https://example.com/a", "canon_requested_url": "https://example.com/a", "physical_state_anchor": "psa-nav"}
    post = {"post_url": "https://example.com/a", "browser_session_id": "sess", "page_id": "page"}
    env, _ = _store_custom(
        tmp_path / "nav" / "s",
        operation="V2_BROWSER_NAVIGATE",
        capability="PC_V2_BROWSER_NAVIGATE_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_NAVIGATE", "requested_url_hash": CRE.compute_ref_hash("https://example.com/a")},
        realized_state={"outcome": CRE.OUTCOME_SUCCESS, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": True, "proof_strength": "STRONG", "realized_state_verified": True, "mutation_performed": True, "post_state_hash": CRE.compute_ref_hash(post), "post_state_ref": post, "execution_state": "POSTCONDITION_CONFIRMED", "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    assert REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "nav" / "s")["reconciliation_status"] == REC.STATUS_MATCH
    rpath = tmp_path / "nav" / "s" / "receipts" / f"{env['action_evidence_id']}.json"
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["realized_state"]["post_state_ref"]["post_url"] = "https://example.com/other"
    rec["realized_state"]["post_state_hash"] = CRE.compute_ref_hash(rec["realized_state"]["post_state_ref"])
    _rewrite_receipt(rpath, rec)
    assert REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "nav" / "s")["reconciliation_status"] == REC.STATUS_MISMATCH


def test_submit_postcondition_confirmed_and_uncertain(tmp_path):
    env, _ = _make(tmp_path, "submit_uncertain", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, mutation=True, op=F.OP_SUBMIT, cap=F.CAP_SUBMIT)
    result = _replay(tmp_path, "submit_uncertain", env)
    assert result["reconciliation_status"] == REC.STATUS_UNCERTAIN

    descriptor = {
        "operation_type": "V2_BROWSER_SUBMIT_FORM_NAVIGATION",
        "public_action": "BROWSER_SUBMIT_FORM_NAVIGATION_V0",
        "field_manifest_hash": "manifest",
        "resolved_action_hash": "final-hash",
        "physical_state_anchor": "psa-submit",
    }
    transport = {"final_url_hash": "final-hash", "navigation_proof": "STRONG", "execution_state": "POSTCONDITION_CONFIRMED"}
    env, _ = _store_custom(
        tmp_path / "submit_match" / "s",
        operation="V2_BROWSER_SUBMIT_FORM_NAVIGATION",
        capability="PC_V2_BROWSER_SUBMIT_GET_NAV_EXECUTE",
        descriptor=descriptor,
        request_ref={"public_action": "BROWSER_SUBMIT_FORM_NAVIGATION_V0", "field_manifest_hash": "manifest", "resolved_action_hash": "final-hash"},
        execution={"executor_kind": "JARJAR", "executor_backend": "BrowserBackend", "executor_operation": "browser.submit_get_navigation", "executor_status": "INVOKED", "executor_input_ref": {"field_manifest_hash": "manifest", "resolved_action_hash": "final-hash"}, "executor_input_hash": CRE.compute_ref_hash({"field_manifest_hash": "manifest", "resolved_action_hash": "final-hash"}), "transport_evidence_ref": transport, "transport_evidence_hash": CRE.compute_ref_hash(transport), "physical_effect_dispatched": True, "execution_state": "POSTCONDITION_CONFIRMED", "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED},
        realized_state={"outcome": CRE.OUTCOME_SUCCESS, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED, "physical_effect_dispatched": True, "proof_strength": "STRONG", "realized_state_verified": True, "mutation_performed": True, "execution_state": "POSTCONDITION_CONFIRMED", "uncertainty_state": "NONE", "uncertainty_reason": ""},
    )
    result = REC.reconcile_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "submit_match" / "s")
    assert result["reconciliation_status"] == REC.STATUS_MATCH
    assert "APPLICATION_SUCCESS_NOT_CLAIMED" in result["evidence_limits"]


def test_negative_governance_and_toctou_are_not_realized(tmp_path):
    for name, outcome, gate in (("block", CRE.OUTCOME_KX108_BLOCK, "BLOCK"), ("toctou", CRE.OUTCOME_TOCTOU_ABORTED, "ALLOW")):
        env, _ = _make(tmp_path, name, outcome=outcome, mutation=False, gate=gate)
        assert _replay(tmp_path, name, env)["reconciliation_status"] == REC.STATUS_NOT_REALIZED


def test_success_missing_post_evidence_is_incomplete(tmp_path):
    env, stores = _make(tmp_path, "missing_post")
    rpath = _receipt_path(stores, env)
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["realized_state"].pop("post_state_ref", None)
    rec["realized_state"].pop("post_state_hash", None)
    _rewrite_receipt(rpath, rec)
    result = _replay(tmp_path, "missing_post", env)
    assert result["reconciliation_status"] == REC.STATUS_INCOMPLETE
    assert "POST_CHECKED_MISSING" in result["missing_evidence"]


def test_tampered_envelope_and_unknown_action_id_stop_reconciliation(tmp_path):
    env, stores = _make(tmp_path, "tamper")
    rpath = _receipt_path(stores, env)
    rec = json.loads(rpath.read_text(encoding="utf-8"))
    rec["realized_state"]["outcome"] = CRE.OUTCOME_NOOP
    rpath.write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    assert _replay(tmp_path, "tamper", env)["reconciliation_status"] == REC.STATUS_TAMPERED
    assert REC.reconcile_action_evidence("aev-" + "0" * 32, stores_base_dir=tmp_path / "none")["reconciliation_status"] == REC.STATUS_NOT_FOUND


def test_reconciliation_is_deterministic_and_static_safe(tmp_path):
    env, _ = _make(tmp_path, "det")
    a = _replay(tmp_path, "det", env)
    b = _replay(tmp_path, "det", env)
    assert a == b
    src = (SCRIPTS / "obsidia_realized_state_reconciliation_v1.py").read_text(encoding="utf-8")
    banned = [
        "JarJarBrowserExecutor", "playwright", "requests", "httpx", "socket", "subprocess",
        "openai", "anthropic", "executor.", "retry", "rollback", "store_canonical_receipt_envelope",
        "store_approval_artifact", "store_kx108_decision_record", "write_text", "unlink", "mkdir",
        "set_checkbox", "set_field_value", "navigate(", "submit_get_navigation",
    ]
    for token in banned:
        assert token not in src
