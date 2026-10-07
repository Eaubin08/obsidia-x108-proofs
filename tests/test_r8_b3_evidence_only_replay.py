from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_batch_execution as E
import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_canonical_receipt_replay_v1 as RPL
import obsidia_kx108_decision_store as DS

OP_SET_CHECKED = "V2_BROWSER_SET_CHECKED"
CAP_SET_CHECKED = "PC_V2_BROWSER_SET_CHECKED_EXECUTE"
OP_SUBMIT = "V2_BROWSER_SUBMIT_FORM_NAVIGATION"
CAP_SUBMIT = "PC_V2_BROWSER_SUBMIT_GET_NAV_EXECUTE"


def _sha(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stores(base: Path) -> dict:
    for n in ("v2exec", "approval", "kxpre", "receipts"):
        (base / n).mkdir(parents=True, exist_ok=True)
    return {"v2exec": base / "v2exec", "approval": base / "approval", "kxpre": base / "kxpre", "receipts": base / "receipts"}


def _eah(op: str, descriptor: dict) -> str:
    return _sha(json.dumps({"v2_schema": "PC_CAPABILITIES_V2_EAH_V0", "operation_type": op, "action_descriptor": descriptor}, sort_keys=True))


def _persist_descriptor(stores, *, op=OP_SET_CHECKED, descriptor=None):
    descriptor = descriptor or {
        "operation_type": op,
        "public_action": "BROWSER_SET_CHECKED",
        "selector": "input#agree",
        "target_checked": True,
        "semantic_intent": "accept_settings",
        "semantic_risk": "LOW",
        "physical_state_anchor": "psa-r8b3",
        "element_identity": {"metadata_sha256": "element-meta", "checked": False},
    }
    eah = _eah(op, descriptor)
    v2id = "v2x-r8b3-" + _sha(op + json.dumps(descriptor, sort_keys=True))[:12]
    rec = {"v2_exec_id": v2id, "operation_type": op, "eah": eah, "descriptor": descriptor, "decision_authority": "KX108_ONLY", "created_at": "2026-10-07T00:00:00+00:00"}
    raw = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    dh = _sha(raw)
    (stores["v2exec"] / f"{v2id}.json").write_text(raw, encoding="utf-8")
    return v2id, eah, dh, descriptor


def _store_approval(stores, *, v2id, child, eah, status="APPROVED_FOR_BOUNDED_EXECUTION"):
    rec = {
        "approval_schema_version": E.SCHEMA_VERSION,
        "approval_id": "apv-r8b3-" + _sha(v2id + child + eah)[:12],
        "created_at": "2026-10-07T00:00:01+00:00",
        "batch_execution_id": v2id,
        "batch_id": v2id,
        "batch_hash": "batchhash",
        "candidate_scope_hash": "scopehash",
        "execution_authority_hash": eah,
        "approved_by": E.APPROVED_BY_HUMAN,
        "approval_status": status,
        "decision_authority": "KX108_ONLY",
    }
    rec["approval_record_hash"] = E.compute_approval_record_hash(rec)
    assert E.store_approval_artifact(rec, stores["approval"])["status"] == "STORED"
    return rec


def _store_kx(stores, *, v2id, child, eah, approval_id, dh, mh, gate="ALLOW"):
    rec = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": "kxpre-r8b3-" + gate.lower() + "-" + _sha(v2id + child + gate)[:8],
        "created_at": "2026-10-07T00:00:02+00:00",
        "decision_phase": DS.PRE_DECISION_PHASE,
        "batch_execution_id": v2id,
        "child_execution_id": child,
        "execution_authority_hash": eah,
        "approval_id": approval_id,
        "pre_execution_context_id": v2id,
        "pre_execution_context_record_hash": dh,
        "test_contract_hash": mh,
        "kx108_input_translation_hash": _sha("translation"),
        "decision_id": "decision-r8b3",
        "trace_id": "trace-r8b3",
        "domain": "PC_BROWSER",
        "x108_gate": gate,
        "reason_code": "R8B3_TEST",
        "severity": "LOW",
        "market_verdict": "TEST",
        "contradictions": [],
        "unknowns": [],
        "risk_flags": [],
        "decision_authority": "KX108_ONLY",
        "canonical_envelope": {"fixture": "r8b3"},
    }
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    assert DS.store_kx108_decision_record(rec, stores["kxpre"])["status"] == DS.STATUS_STORED
    return rec


def _store_envelope(base: Path, *, outcome=CRE.OUTCOME_SUCCESS, mutation=True, gate="ALLOW", op=OP_SET_CHECKED, cap=CAP_SET_CHECKED, include_approval=True, include_kx=True):
    stores = _stores(base)
    if op == OP_SUBMIT:
        descriptor = {
            "operation_type": op,
            "public_action": "BROWSER_SUBMIT_FORM_NAVIGATION_V0",
            "form_selector": "form#search",
            "submitter_selector": "button#go",
            "field_manifest_hash": _sha("secret-query"),
            "resolved_action_hash": _sha("https://example.com/results"),
            "resolved_action_endpoint": "https://example.com/results",
            "submission_class": "NORMAL_GET_NAVIGATION",
            "semantic_intent": "search",
            "semantic_risk": "HIGH",
            "physical_state_anchor": "psa-submit-r8b3",
        }
    else:
        descriptor = None
    v2id, eah, dh, descriptor = _persist_descriptor(stores, op=op, descriptor=descriptor)
    child = "chd-r8b3-" + _sha(v2id)[:8]
    mh = _sha(json.dumps(descriptor, sort_keys=True))[:16]
    approval = _store_approval(stores, v2id=v2id, child=child, eah=eah) if include_approval else None
    kx = _store_kx(stores, v2id=v2id, child=child, eah=eah, approval_id=approval["approval_id"], dh=dh, mh=mh, gate=gate) if include_kx and approval else None
    request_ref = {"public_action": descriptor["public_action"], "selector_hash": CRE.compute_ref_hash(descriptor.get("selector", descriptor.get("form_selector"))), "semantic_intent": descriptor.get("semantic_intent"), "semantic_risk": descriptor.get("semantic_risk")}
    session_ref = {"session_id": "sess-r8b3", "v2_exec_id": v2id, "child_id": child}
    if op == OP_SUBMIT:
        exec_ref = {"public_action": "BROWSER_SUBMIT_FORM_NAVIGATION_V0", "field_manifest_hash": descriptor["field_manifest_hash"], "resolved_action_hash": descriptor["resolved_action_hash"]}
        transport = {"request_observed": True, "request_url_hash": "reqhash", "execution_state": "DISPATCHED_OUTCOME_UNCERTAIN"}
        execution = {"executor_kind": "JARJAR", "executor_backend": "BrowserBackend", "executor_operation": "browser.submit_get_navigation", "executor_status": "INVOKED", "executor_input_ref": exec_ref, "executor_input_hash": CRE.compute_ref_hash(exec_ref), "transport_evidence_ref": transport, "transport_evidence_hash": CRE.compute_ref_hash(transport), "physical_effect_dispatched": True, "execution_state": "DISPATCHED_OUTCOME_UNCERTAIN", "dispatch_boundary": CRE.DISPATCH_POST_UNCERTAINTY}
        realized = {"outcome": CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, "failure_stage": CRE.STAGE_RECONCILIATION, "dispatch_boundary": CRE.DISPATCH_POST_UNCERTAINTY, "physical_effect_dispatched": True, "proof_strength": "UNCERTAIN", "realized_state_verified": False, "mutation_performed": True, "execution_state": "DISPATCHED_OUTCOME_UNCERTAIN", "uncertainty_state": CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, "uncertainty_reason": "NAVIGATION_TIMEOUT", "last_confirmed_state_hash": descriptor["physical_state_anchor"]}
    else:
        exec_ref = {"public_action": "BROWSER_SET_CHECKED", "selector": "input#agree", "element_identity_hash": "element-meta", "target_checked": True, "semantic_intent": "accept_settings", "semantic_risk": "LOW", "physical_state_anchor": descriptor["physical_state_anchor"]}
        physical = outcome == CRE.OUTCOME_REALIZED_STATE_MISMATCH or (outcome == CRE.OUTCOME_SUCCESS and mutation)
        executor_status = CRE.STATUS_NOT_REACHED if outcome in {CRE.OUTCOME_KX108_BLOCK, CRE.OUTCOME_KX108_HOLD, CRE.OUTCOME_TOCTOU_ABORTED} else "INVOKED"
        execution = {"executor_kind": "JARJAR", "executor_backend": "BrowserBackend", "executor_operation": "browser.set_checkbox", "executor_status": executor_status, "executor_input_ref": exec_ref, "executor_input_hash": CRE.compute_ref_hash(exec_ref), "physical_effect_dispatched": physical, "mutation_performed": mutation, "execution_state": "POSTCONDITION_CONFIRMED" if outcome in {CRE.OUTCOME_SUCCESS, CRE.OUTCOME_NOOP} else outcome}
        realized = {"outcome": outcome, "failure_stage": CRE.STATUS_NOT_APPLICABLE, "dispatch_boundary": CRE.DISPATCH_POST_CONFIRMED if physical or outcome in {CRE.OUTCOME_SUCCESS, CRE.OUTCOME_NOOP} else CRE.DISPATCH_PRE_FAILURE, "physical_effect_dispatched": physical, "proof_strength": "STRONG", "realized_state_verified": outcome in {CRE.OUTCOME_SUCCESS, CRE.OUTCOME_NOOP}, "mutation_performed": mutation, "execution_state": execution["execution_state"], "uncertainty_state": "NONE", "uncertainty_reason": ""}
        if outcome == CRE.OUTCOME_TOCTOU_ABORTED:
            realized.update({"failure_stage": CRE.STAGE_TOCTOU, "prepared_pre_state_hash": descriptor["physical_state_anchor"], "current_state_ref": {"element_identity_hash": "changed"}, "current_state_hash": CRE.compute_ref_hash({"element_identity_hash": "changed"})})
        if outcome == CRE.OUTCOME_KX108_BLOCK:
            realized["failure_stage"] = CRE.STAGE_KX108
        if outcome == CRE.OUTCOME_REALIZED_STATE_MISMATCH:
            realized.update({"failure_stage": CRE.STAGE_POST_OBSERVATION, "realized_state_verified": False, "post_state_ref": {"checked": False, "element_identity_hash": "element-meta"}, "post_state_hash": CRE.compute_ref_hash({"checked": False, "element_identity_hash": "element-meta"})})
    auth = {"execution_authority_hash": eah, "approval_id": approval["approval_id"] if approval else CRE.STATUS_NOT_REACHED, "approval_status": approval["approval_status"] if approval else CRE.STATUS_NOT_REACHED, "approved_by": approval["approved_by"] if approval else CRE.STATUS_NOT_REACHED, "approval_record_hash": approval["approval_record_hash"] if approval else CRE.STATUS_NOT_REACHED, "kx108_pre_decision_record_id": kx["decision_record_id"] if kx else CRE.STATUS_NOT_REACHED, "kx108_pre_decision_record_hash": kx["decision_record_hash"] if kx else CRE.STATUS_NOT_REACHED, "kx108_verdict": gate if kx else CRE.STATUS_NOT_REACHED, "binder_verdict_status": "OBSERVED_INLINE_NOT_SEPARATELY_PERSISTED", "binder_verdict_ref": "NOT_SEPARATELY_PERSISTED"}
    receipt = {"existing_runtime_receipt_id": "pcrcp-r8b3", "existing_receipt_hash": _sha("runtime"), "existing_receipt_ref": "runtime_result.receipt"}
    env = CRE.build_canonical_receipt_envelope(capability=cap, operation_type=op, request_ref=request_ref, session_ref=session_ref, action_identity={"schema_version": CRE.SCHEMA_VERSION, "capability": cap, "operation_type": op, "request_ref": request_ref, "session_ref": session_ref, "descriptor_hash": dh, "execution_authority_hash": eah}, prepare={"descriptor_ref": v2id, "descriptor_hash": dh, "physical_state_anchor": descriptor["physical_state_anchor"], "state_anchor_kind": "PHYSICAL_PRE_STATE", "manifest_hash": mh}, authorization=auth, execution=execution, realized_state=realized, receipt=receipt, replay={"physical_replay_allowed": False, "evidence_replay_allowed": True, "automatic_retry": False}, privacy={"redaction_policy": "HASHES_AND_REFS_ONLY", "plaintext_sensitive_data_present": False, "get_query_plaintext_persisted": False})
    assert CRE.store_canonical_receipt_envelope(env, stores["receipts"])["status"] == CRE.STATUS_STORED
    return env, stores


def _replay(env, tmp_path):
    return RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "s")


def test_replays_success_noop_negative_and_uncertain_outcomes(tmp_path):
    cases = [
        (CRE.OUTCOME_SUCCESS, True, OP_SET_CHECKED),
        (CRE.OUTCOME_NOOP, False, OP_SET_CHECKED),
        (CRE.OUTCOME_KX108_BLOCK, False, OP_SET_CHECKED),
        (CRE.OUTCOME_TOCTOU_ABORTED, False, OP_SET_CHECKED),
        (CRE.OUTCOME_REALIZED_STATE_MISMATCH, True, OP_SET_CHECKED),
        (CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, True, OP_SUBMIT),
    ]
    for i, (outcome, mutation, op) in enumerate(cases):
        env, _ = _store_envelope(tmp_path / f"case{i}" / "s", outcome=outcome, mutation=mutation, op=op, cap=CAP_SUBMIT if op == OP_SUBMIT else CAP_SET_CHECKED)
        result = RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / f"case{i}" / "s")
        assert result["receipt_found"] is True
        assert result["envelope_hash_valid"] is True
        assert result["descriptor_ref_valid"] == RPL.YES
        assert result["EAH_binding_valid"] == RPL.YES
        assert result["approval_ref_valid"] == RPL.YES
        assert result["KX108_ref_valid"] == RPL.YES
        assert result["executor_binding_valid"] == RPL.YES
        assert result["realized_state_evidence_valid"] == RPL.YES
        assert result["outcome_consistency_valid"] == RPL.YES
        assert result["outcome"] == outcome
        assert result["replay_verdict"] == RPL.VERDICT_VERIFIED_WITH_LIMITS
        assert result["binder_replay_status"] == RPL.INLINE_STATUS_ONLY


def test_replay_is_deterministic_and_uses_action_evidence_id_root(tmp_path):
    env, _ = _store_envelope(tmp_path / "s", outcome=CRE.OUTCOME_SUCCESS)
    a = _replay(env, tmp_path)
    b = _replay(env, tmp_path)
    assert a == b
    assert a["action_evidence_id"] == env["action_evidence_id"]
    assert a["linked_ids"]["descriptor_ref"] == env["prepare"]["descriptor_ref"]


def test_unknown_action_id_returns_not_found(tmp_path):
    result = RPL.replay_action_evidence("aev-" + "0" * 32, stores_base_dir=tmp_path / "s")
    assert result["replay_verdict"] == RPL.VERDICT_NOT_FOUND
    assert result["receipt_found"] is False


def test_tampered_envelope_stops_trust_propagation(tmp_path):
    env, stores = _store_envelope(tmp_path / "s", outcome=CRE.OUTCOME_SUCCESS)
    p = stores["receipts"] / f"{env['action_evidence_id']}.json"
    tampered = json.loads(p.read_text(encoding="utf-8"))
    tampered["realized_state"]["outcome"] = CRE.OUTCOME_NOOP
    p.write_text(json.dumps(tampered, indent=2, sort_keys=True), encoding="utf-8")
    result = _replay(env, tmp_path)
    assert result["replay_verdict"] == RPL.VERDICT_TAMPERED
    assert result["descriptor_ref_valid"] == RPL.UNAVAILABLE


def test_descriptor_approval_kx_and_post_state_tamper_are_detected(tmp_path):
    env, stores = _store_envelope(tmp_path / "desc" / "s", outcome=CRE.OUTCOME_SUCCESS)
    dpath = stores["v2exec"] / f"{env['prepare']['descriptor_ref']}.json"
    desc = json.loads(dpath.read_text(encoding="utf-8")); desc["descriptor"]["semantic_risk"] = "HIGH"
    dpath.write_text(json.dumps(desc, sort_keys=True), encoding="utf-8")
    assert RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "desc" / "s")["replay_verdict"] == RPL.VERDICT_TAMPERED

    env, stores = _store_envelope(tmp_path / "approval" / "s", outcome=CRE.OUTCOME_SUCCESS)
    apath = stores["approval"] / "approvals" / env["authorization"]["approval_id"] / "approval.json"
    appr = json.loads(apath.read_text(encoding="utf-8")); appr["approval_status"] = "CHANGED"
    apath.write_text(json.dumps(appr), encoding="utf-8")
    assert RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "approval" / "s")["replay_verdict"] == RPL.VERDICT_TAMPERED

    env, stores = _store_envelope(tmp_path / "kx" / "s", outcome=CRE.OUTCOME_SUCCESS)
    kpath = stores["kxpre"] / f"{env['authorization']['kx108_pre_decision_record_id']}.json"
    kx = json.loads(kpath.read_text(encoding="utf-8")); kx["x108_gate"] = "BLOCK"
    kpath.write_text(json.dumps(kx), encoding="utf-8")
    assert RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "kx" / "s")["replay_verdict"] == RPL.VERDICT_TAMPERED

    env, stores = _store_envelope(tmp_path / "post" / "s", outcome=CRE.OUTCOME_REALIZED_STATE_MISMATCH)
    p = stores["receipts"] / f"{env['action_evidence_id']}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["realized_state"]["post_state_ref"]["checked"] = True
    data["envelope_hash"] = CRE.compute_envelope_hash(data)
    p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    result = RPL.replay_action_evidence(env["action_evidence_id"], stores_base_dir=tmp_path / "post" / "s")
    assert result["replay_verdict"] == RPL.VERDICT_TAMPERED
    assert "POST_STATE_HASH_MISMATCH" in result["evidence_conflicts"]


def test_missing_artifact_is_incomplete_not_tampered(tmp_path):
    env, stores = _store_envelope(tmp_path / "s", outcome=CRE.OUTCOME_SUCCESS)
    (stores["v2exec"] / f"{env['prepare']['descriptor_ref']}.json").unlink()
    result = _replay(env, tmp_path)
    assert result["replay_verdict"] == RPL.VERDICT_INCOMPLETE
    assert "DESCRIPTOR_MISSING" in result["evidence_missing"]


def test_replay_api_has_no_executor_parameter_and_does_not_expose_secret_plaintext(tmp_path):
    import inspect
    sig = inspect.signature(RPL.replay_action_evidence)
    assert "executor" not in sig.parameters
    env, _ = _store_envelope(tmp_path / "s", outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN, op=OP_SUBMIT, cap=CAP_SUBMIT)
    result = _replay(env, tmp_path)
    assert "secret-query" not in json.dumps(result, sort_keys=True)
    assert result["physical_effect_dispatched"] is True


def test_static_replay_module_has_no_execution_network_or_mutation_imports():
    src = (SCRIPTS / "obsidia_canonical_receipt_replay_v1.py").read_text(encoding="utf-8")
    banned = ["JarJarBrowserExecutor", "set_checkbox", "submit_get_navigation", "playwright", "requests", "httpx", "socket", "subprocess", "openai", "anthropic", "store_canonical_receipt_envelope", "store_approval_artifact", "store_kx108_decision_record"]
    for token in banned:
        assert token not in src
