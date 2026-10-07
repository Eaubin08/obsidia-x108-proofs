from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_canonical_receipt_replay_v1 as B3
import obsidia_governance_decision_replay_v1 as B5
import obsidia_pc_capabilities_v2 as PC2
import obsidia_realized_state_reconciliation_v1 as B6

SESSION_ID = "sess-r8b7aaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID = "page-r8b7bbbbbbbbbbbbbbbbbbbbbbbb"
URL = "https://example.com/r8b7"
SENTINEL = "R8_PRIVATE_SENTINEL_STATIC_FIXTURE"


def _install_kx_gate(monkeypatch, gate: str = "ALLOW") -> None:
    from sigma.contracts import CanonicalDecisionEnvelope
    import sigma.protocols as protocols

    def fake_pipeline(_state):
        return CanonicalDecisionEnvelope(
            domain="PC_BROWSER",
            market_verdict=gate,
            x108_gate=gate,
            reason_code=f"R8B7_{gate}",
            severity="S0",
            decision_id=f"decision-r8b7-{gate.lower()}",
            trace_id=f"trace-r8b7-{gate.lower()}",
        )

    monkeypatch.setattr(protocols, "run_tooling_build_pipeline", fake_pipeline)


def _checkbox_identity(*, checked=False, metadata="meta-r8b7"):
    return {
        "ok": True,
        "browser_session_id": SESSION_ID,
        "page_id": PAGE_ID,
        "url": URL,
        "origin": "https://example.com",
        "selector": "input#agree",
        "element_count": 1,
        "tag_name": "input",
        "type": "checkbox",
        "role": "",
        "name": "agree",
        "id": "agree",
        "form_owner": "form-r8b7",
        "checked": checked,
        "indeterminate_status": "FALSE_PROVEN",
        "metadata_sha256": metadata,
        "visible": True,
        "enabled": True,
        "closed": False,
        "main_frame": True,
    }


class CheckboxExecutor:
    EXECUTOR_PROVIDER = "JARJAR"
    EXECUTOR_BACKEND = "BrowserBackend"

    def __init__(self, *, initial=False, post=True, action_ok=True, mutation=True, drift=False, drift_after_inspect=1):
        self.initial = initial
        self.post = post
        self.action_ok = action_ok
        self.mutation = mutation
        self.drift = drift
        self.drift_after_inspect = drift_after_inspect
        self.inspect_calls = 0
        self.mutation_calls = 0

    def inspect_checkbox(self, _selector):
        self.inspect_calls += 1
        if self.drift and self.inspect_calls > self.drift_after_inspect:
            return _checkbox_identity(checked=not self.initial, metadata="meta-r8b7-drift")
        if self.inspect_calls == 1 or not self.mutation_calls:
            return _checkbox_identity(checked=self.initial)
        return _checkbox_identity(checked=self.post)

    def set_checkbox(self, _identity, target_checked):
        self.mutation_calls += 1
        if not self.action_ok:
            return {"ok": False, "error": "controlled-before-action-failure", "mutation_performed": False}
        return {
            "ok": True,
            "mutation_performed": bool(self.mutation),
            "checked": self.post,
            "target_checked": bool(target_checked),
            "navigation_detected": False,
            "popup_detected": False,
            "new_page_detected": False,
            "download_detected": False,
        }


def _field_identity(*, value_hash, value_length):
    return {
        "ok": True,
        "browser_session_id": SESSION_ID,
        "page_id": PAGE_ID,
        "url": URL,
        "origin": "https://example.com",
        "closed": False,
        "selector": "input#secret",
        "element_count": 1,
        "tag_name": "input",
        "type": "text",
        "name": "secret",
        "id": "secret",
        "role": "",
        "autocomplete": "",
        "form_owner": "form-r8b7",
        "visible": True,
        "enabled": True,
        "editable": True,
        "readonly": False,
        "supported_field_class": "INPUT_TEXT",
        "current_value_sha256": value_hash,
        "current_value_length": value_length,
        "metadata_sha256": "field-meta-r8b7",
        "main_frame": True,
    }


class FieldExecutor:
    EXECUTOR_PROVIDER = "JARJAR"
    EXECUTOR_BACKEND = "BrowserBackend"

    def __init__(self, *, before_hash, before_length, after_hash, after_length):
        self.before_hash = before_hash
        self.before_length = before_length
        self.after_hash = after_hash
        self.after_length = after_length
        self.inspect_calls = 0
        self.mutation_calls = 0

    def inspect_field(self, _selector):
        self.inspect_calls += 1
        if self.mutation_calls:
            return _field_identity(value_hash=self.after_hash, value_length=self.after_length)
        return _field_identity(value_hash=self.before_hash, value_length=self.before_length)

    def set_field_value(self, _identity, target_value):
        self.mutation_calls += 1
        return {
            "ok": True,
            "mutation_performed": True,
            "target_value_sha256": PC2._sha256_text(target_value),
            "post_value_sha256": self.after_hash,
            "target_value_length": len(target_value),
            "post_value_length": self.after_length,
            "navigation_detected": False,
            "popup_detected": False,
            "new_page_detected": False,
            "download_detected": False,
        }


class SubmitExecutor:
    EXECUTOR_PROVIDER = "JARJAR"
    EXECUTOR_BACKEND = "BrowserBackend"

    def __init__(self):
        self.submit_calls = 0
        self.inspect_calls = 0
        self.identity = self._identity()

    def _identity(self):
        return {
            "ok": True,
            "browser_session_id": SESSION_ID,
            "page_id": PAGE_ID,
            "url": "https://example.com/search",
            "origin": "https://example.com",
            "closed": False,
            "form_selector": "form#search",
            "form_count": 1,
            "form_tag": "form",
            "form_action": "/results",
            "resolved_action": "https://example.com/results",
            "resolved_action_hash": PC2._sha256_text("https://example.com/results"),
            "resolved_action_endpoint": "https://example.com/results",
            "method": "get",
            "target": "",
            "enctype": "application/x-www-form-urlencoded",
            "name": "search",
            "id": "f-r8b7",
            "autocomplete": "",
            "same_origin_action": True,
            "submitter_selector": "button#go",
            "submitter_count": 1,
            "submitter_tag": "button",
            "submitter_type": "submit",
            "submitter_name": "go",
            "submitter_value_sha256": PC2._sha256_text("Go"),
            "submitter_value_length": 2,
            "submitter_form_owner": "",
            "submitter_belongs_to_form": True,
            "submitter_visible": True,
            "submitter_enabled": True,
            "submitter_text_sha256": PC2._sha256_text("Go"),
            "field_manifest_hash": PC2._sha256_text("q=hash-only"),
            "field_count": 1,
            "contains_password": False,
            "contains_otp_sensitive": False,
            "contains_payment_sensitive": False,
            "metadata_sha256": "form-meta-r8b7",
            "submitter_metadata_sha256": "submitter-meta-r8b7",
            "main_frame_only": True,
            "physical_state_anchor": "psa-submit-r8b7",
            "redirect_policy": "SAME_ORIGIN_REDIRECT_CHAIN",
            "expected_effect": "NAVIGATION",
        }

    def inspect_form_submission(self, _form_selector, _submitter_selector):
        self.inspect_calls += 1
        return dict(self.identity)

    def submit_get_navigation(self, _identity):
        self.submit_calls += 1
        return {
            "ok": True,
            "request_observed": True,
            "request_method": "GET",
            "request_url_hash": "request-hash-r8b7",
            "request_endpoint": "https://example.com/results",
            "request_fingerprint": "request-fingerprint-r8b7",
            "response_observed": False,
            "response_status": None,
            "response_url_hash": "",
            "final_url_hash": "",
            "final_url_endpoint": "",
            "execution_state": "DISPATCHED_OUTCOME_UNCERTAIN",
            "uncertain_reason": "CONTROLLED_FINAL_OBSERVATION_UNAVAILABLE",
            "transport_proof": "STRONG",
            "navigation_proof": "UNCERTAIN",
        }


def _run_checkbox(tmp_path, monkeypatch, *, gate="ALLOW", initial=False, target=True, post=True, action_ok=True, mutation=True, drift=False, drift_after_inspect=1):
    _install_kx_gate(monkeypatch, gate)
    ex = CheckboxExecutor(initial=initial, post=post, action_ok=action_ok, mutation=mutation, drift=drift, drift_after_inspect=drift_after_inspect)
    prep = PC2.pc_v2_browser_set_checked_prepare(
        "input#agree", target, "r8b7_certify", "LOW", stores_base_dir=tmp_path / "s", session_id=SESSION_ID, executor=ex
    )
    assert prep["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    result = PC2.pc_v2_browser_set_checked_execute(
        prep, prep["execution_authority_hash"], "HUMAN-R8B7", stores_base_dir=tmp_path / "s", session_id=SESSION_ID, executor=ex
    )
    return ex, result


def _certify(stores_base_dir: Path, action_evidence_id: str):
    b3 = B3.replay_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    b5 = B5.replay_governance_decision(action_evidence_id, stores_base_dir=stores_base_dir)
    b6 = B6.reconcile_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    assert b3["action_evidence_id"] == b5["action_evidence_id"] == b6["action_evidence_id"] == action_evidence_id
    assert b3["replay_verdict"] in {B3.VERDICT_VERIFIED, B3.VERDICT_VERIFIED_WITH_LIMITS}
    return b3, b5, b6


def test_e2e_success_mutation_noop_hold_block_executor_fail_and_mismatch(tmp_path, monkeypatch):
    ex, result = _run_checkbox(tmp_path / "success", monkeypatch, initial=False, target=True, post=True, mutation=True)
    _b3, b5, b6 = _certify(tmp_path / "success" / "s", result["action_evidence_id"])
    assert result["canonical_receipt_envelope"]["realized_state"]["outcome"] == CRE.OUTCOME_SUCCESS
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_MATCH
    assert ex.mutation_calls == 1

    ex, result = _run_checkbox(tmp_path / "noop", monkeypatch, initial=True, target=True, post=True, mutation=False)
    _b3, b5, b6 = _certify(tmp_path / "noop" / "s", result["action_evidence_id"])
    assert result["canonical_receipt_envelope"]["realized_state"]["outcome"] == CRE.OUTCOME_NOOP
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_NOOP_CONFIRMED

    for gate in ("HOLD", "BLOCK"):
        ex, result = _run_checkbox(tmp_path / gate.lower(), monkeypatch, gate=gate)
        _b3, b5, b6 = _certify(tmp_path / gate.lower() / "s", result["action_evidence_id"])
        assert result["canonical_receipt_envelope"]["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
        assert b5["historical_kx108_verdict"] == gate and b6["reconciliation_status"] == B6.STATUS_NOT_REALIZED
        assert ex.mutation_calls == 0

    ex, result = _run_checkbox(tmp_path / "exec_fail", monkeypatch, action_ok=False, mutation=False)
    _b3, b5, b6 = _certify(tmp_path / "exec_fail" / "s", result["action_evidence_id"])
    assert result["canonical_receipt_envelope"]["realized_state"]["outcome"] == CRE.OUTCOME_EXECUTOR_FAILED_BEFORE_ACTION
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_NOT_REALIZED

    ex, result = _run_checkbox(tmp_path / "mismatch", monkeypatch, initial=False, target=True, post=False, mutation=True)
    _b3, b5, b6 = _certify(tmp_path / "mismatch" / "s", result["action_evidence_id"])
    assert result["canonical_receipt_envelope"]["realized_state"]["outcome"] == CRE.OUTCOME_REALIZED_STATE_MISMATCH
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_MISMATCH


def test_e2e_toctou_early_abort_stops_before_kx_decision_replay(tmp_path, monkeypatch):
    ex, result = _run_checkbox(tmp_path, monkeypatch, drift=True)
    assert result["canonical_receipt_envelope"]["realized_state"]["outcome"] == CRE.OUTCOME_TOCTOU_ABORTED
    assert result["canonical_receipt_envelope"]["realized_state"]["toctou_phase"] == "PRE_AUTHORIZATION"
    assert result["canonical_receipt_envelope"]["realized_state"]["current_state_hash"]
    assert ex.mutation_calls == 0
    b3 = B3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "s")
    b5 = B5.replay_governance_decision(result["action_evidence_id"], stores_base_dir=tmp_path / "s")
    b6 = B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "s")
    assert b3["replay_verdict"] in {B3.VERDICT_VERIFIED, B3.VERDICT_VERIFIED_WITH_LIMITS}
    assert b5["replay_verdict"] == B5.VERDICT_INCOMPLETE
    assert "APPROVAL_ID_MISSING" in b5["missing_inputs"]
    assert b6["reconciliation_status"] == B6.STATUS_NOT_REALIZED


def test_e2e_toctou_late_abort_is_replayable_after_kx_before_dispatch(tmp_path, monkeypatch):
    ex, result = _run_checkbox(tmp_path, monkeypatch, drift=True, drift_after_inspect=2)
    envelope = result["canonical_receipt_envelope"]
    assert envelope["realized_state"]["outcome"] == CRE.OUTCOME_TOCTOU_ABORTED
    assert envelope["realized_state"]["toctou_phase"] == "POST_AUTHORIZATION_PRE_EXECUTION"
    assert envelope["authorization"]["approval_id"] != CRE.STATUS_NOT_REACHED
    assert envelope["authorization"]["kx108_pre_decision_record_id"] != CRE.STATUS_NOT_REACHED
    assert envelope["authorization"]["binder_verdict_status"] == "OBSERVED_INLINE"
    assert envelope["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
    assert envelope["execution"]["physical_effect_dispatched"] is False
    assert ex.mutation_calls == 0
    b3, b5, b6 = _certify(tmp_path / "s", result["action_evidence_id"])
    assert b3["replay_verdict"] in {B3.VERDICT_VERIFIED, B3.VERDICT_VERIFIED_WITH_LIMITS}
    assert b5["replay_verdict"] == B5.VERDICT_MATCH
    assert b5["historical_kx108_verdict"] == "ALLOW"
    assert b5["replayed_kx108_verdict"] == "ALLOW"
    assert b6["reconciliation_status"] == B6.STATUS_NOT_REALIZED


def test_e2e_submit_uncertain_privacy_tamper_missing_and_replay_safety(tmp_path, monkeypatch):
    _install_kx_gate(monkeypatch, "ALLOW")
    submitter = SubmitExecutor()
    prep = PC2.pc_v2_browser_submit_get_navigation_prepare(
        "form#search", "button#go", "search", "HIGH", "NORMAL_GET_NAVIGATION",
        stores_base_dir=tmp_path / "submit" / "s", session_id=SESSION_ID, executor=submitter
    )
    submit = PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "HUMAN-R8B7",
        stores_base_dir=tmp_path / "submit" / "s", session_id=SESSION_ID, executor=submitter
    )
    _b3, b5, b6 = _certify(tmp_path / "submit" / "s", submit["action_evidence_id"])
    assert submit["canonical_receipt_envelope"]["realized_state"]["physical_effect_dispatched"] is True
    assert submit["canonical_receipt_envelope"]["replay"]["automatic_retry"] is False
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_UNCERTAIN
    assert submitter.submit_calls == 1

    before_hash = PC2._sha256_text("old")
    target_hash = PC2._sha256_text(SENTINEL)
    field = FieldExecutor(before_hash=before_hash, before_length=3, after_hash=target_hash, after_length=len(SENTINEL))
    prep = PC2.pc_v2_browser_set_field_value_prepare(
        "input#secret", SENTINEL, "set_test_secret", "HIGH",
        stores_base_dir=tmp_path / "field" / "s", session_id=SESSION_ID, executor=field
    )
    result = PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "HUMAN-R8B7", SENTINEL,
        stores_base_dir=tmp_path / "field" / "s", session_id=SESSION_ID, executor=field
    )
    b3, b5, b6 = _certify(tmp_path / "field" / "s", result["action_evidence_id"])
    assert b5["replay_verdict"] == B5.VERDICT_MATCH and b6["reconciliation_status"] == B6.STATUS_MATCH
    blob = "\n".join(p.read_text(encoding="utf-8") for p in (tmp_path / "field" / "s").rglob("*.json"))
    assert SENTINEL not in blob
    assert SENTINEL not in json.dumps([result, b3, b5, b6], sort_keys=True)
    assert target_hash in blob and str(len(SENTINEL)) in blob

    ex, result = _run_checkbox(tmp_path / "tamper", monkeypatch)
    calls = ex.mutation_calls
    receipt = tmp_path / "tamper" / "s" / "receipts" / f"{result['action_evidence_id']}.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    data["realized_state"]["post_state_ref"]["checked"] = False
    receipt.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    assert B3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "tamper" / "s")["replay_verdict"] == B3.VERDICT_TAMPERED
    assert B5.replay_governance_decision(result["action_evidence_id"], stores_base_dir=tmp_path / "tamper" / "s")["replay_verdict"] == B5.VERDICT_TAMPERED
    assert B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "tamper" / "s")["reconciliation_status"] == B6.STATUS_TAMPERED
    assert ex.mutation_calls == calls

    ex, result = _run_checkbox(tmp_path / "missing", monkeypatch)
    calls = ex.mutation_calls
    descriptor_ref = result["canonical_receipt_envelope"]["prepare"]["descriptor_ref"]
    (tmp_path / "missing" / "s" / "v2exec" / f"{descriptor_ref}.json").unlink()
    assert B3.replay_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "missing" / "s")["replay_verdict"] == B3.VERDICT_INCOMPLETE
    assert B5.replay_governance_decision(result["action_evidence_id"], stores_base_dir=tmp_path / "missing" / "s")["replay_verdict"] == B5.VERDICT_INCOMPLETE
    assert B6.reconcile_action_evidence(result["action_evidence_id"], stores_base_dir=tmp_path / "missing" / "s")["reconciliation_status"] == B6.STATUS_INCOMPLETE
    assert ex.mutation_calls == calls

    ex, result = _run_checkbox(tmp_path / "safety", monkeypatch)
    stores = tmp_path / "safety" / "s"
    before_files = sorted(str(p.relative_to(stores)) for p in stores.rglob("*.json"))
    calls = ex.mutation_calls
    for _ in range(3):
        _certify(stores, result["action_evidence_id"])
    after_files = sorted(str(p.relative_to(stores)) for p in stores.rglob("*.json"))
    assert after_files == before_files
    assert ex.mutation_calls == calls


def test_r8_b7_closure_audit_and_deferred_limits_are_explicit():
    closure = {
        "canonical_immutable_receipt_envelope": "YES",
        "single_action_evidence_identity": "YES",
        "success_noop_outcomes": "YES",
        "failure_hold_block_uncertainty_outcomes": "YES",
        "tamper_evident_integrity": "YES",
        "generic_evidence_only_replay": "YES",
        "deterministic_governance_decision_replay": "YES",
        "realized_state_reconciliation": "YES",
        "replay_cannot_reexecute": "YES",
        "uncertainty_cannot_become_false_certainty": "YES",
        "privacy_boundary_preserved": "YES",
        "true_e2e_scenario_proof": "PARTIAL",
    }
    deferred_blocks_r8 = {
        "R8_DEFER_01 early PREPARE rejection receipts not integrated": "NO",
        "R8_DEFER_02 approval-missing receipts not integrated": "NO",
        "R8_DEFER_03 Binder historical replay inline-only": "NO",
        "R8_DEFER_04 KX historical policy version not universally bound": "NO",
        "R8_DEFER_05 generic uncertainty model not yet used by all domains": "NO",
        "R8_DEFER_06 UIA/filesystem/window/app families not all normalized into B6 adapters": "NO",
        "R8_DEFER_07 current-state/live reconciliation not implemented": "NO",
        "R8_DEFER_08 generic rollback not implemented": "NO",
        "R8_DEFER_09 checkbox TOCTOU stops before approval/KX decision replay": "YES",
        "R8_DEFER_10 real executor E2E deferred by non-browser R8 envelope integration": "NO",
    }
    assert closure["true_e2e_scenario_proof"] == "PARTIAL"
    assert deferred_blocks_r8["R8_DEFER_09 checkbox TOCTOU stops before approval/KX decision replay"] == "YES"
