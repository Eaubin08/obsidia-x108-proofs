from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_pc_capabilities_v2 as PC2

URL = "https://example.com/page"
SESSION_ID = "sess-r8b2"
PAGE_ID = "page-r8b2"


def _chk(*, checked=False, metadata="meta-r8b2", sid=SESSION_ID, pid=PAGE_ID):
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": URL,
        "origin": "https://example.com",
        "selector": "input#agree",
        "element_count": 1,
        "tag_name": "input",
        "type": "checkbox",
        "role": "",
        "name": "agree",
        "id": "agree",
        "form_owner": "f1",
        "checked": checked,
        "indeterminate_status": "FALSE_PROVEN",
        "metadata_sha256": metadata,
        "visible": True,
        "enabled": True,
        "closed": False,
        "main_frame": True,
    }


def _checkbox_executor(pre=None, post=None, act=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = pre or _chk()
    post = post or _chk(checked=True)
    ex.inspect_checkbox.side_effect = [pre, pre, post]
    ex.set_checkbox.return_value = act or {
        "ok": True,
        "mutation_performed": pre["checked"] is not True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    return ex


def _store_approval(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})


def _kx(monkeypatch, gate="ALLOW"):
    monkeypatch.setattr(
        PC2,
        "_kx108_pre",
        lambda *_a, **_k: {
            "verify_ok": True,
            "x108_gate": gate,
            "decision_record_id": f"kxpre-r8b2-{gate.lower()}",
            "record": {"decision_record_hash": PC2._sha256_text("kx-" + gate)},
        },
    )


def _prep_checked(tmp_path, ex):
    return PC2.pc_v2_browser_set_checked_prepare(
        "input#agree", True, "accept_settings", "LOW",
        stores_base_dir=tmp_path / "s", executor=ex)


def _execute_checked(tmp_path, prep, ex):
    return PC2.pc_v2_browser_set_checked_execute(
        prep, prep["execution_authority_hash"], "HUMAN_REF",
        stores_base_dir=tmp_path / "s", executor=ex)


def test_kx108_block_persists_failure_envelope_and_does_not_call_executor(monkeypatch, tmp_path):
    _store_approval(monkeypatch)
    _kx(monkeypatch, "BLOCK")
    ex = _checkbox_executor()
    prep = _prep_checked(tmp_path, ex)

    result = _execute_checked(tmp_path, prep, ex)
    env = result["canonical_receipt_envelope"]

    assert result["status"] == PC2.EXECUTE_REJECTED
    assert env["realized_state"]["outcome"] == CRE.OUTCOME_KX108_BLOCK
    assert env["realized_state"]["failure_stage"] == CRE.STAGE_KX108
    assert env["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
    assert env["execution"]["physical_effect_dispatched"] is False
    assert env["authorization"]["kx108_verdict"] == "BLOCK"
    assert env["authorization"]["kx108_pre_decision_record_id"] == "kxpre-r8b2-block"
    assert result["action_evidence_id"] == env["action_evidence_id"]
    assert result["canonical_receipt_store_status"] == CRE.STATUS_STORED
    ex.set_checkbox.assert_not_called()
    assert CRE.verify_canonical_receipt_envelope(env)[0]




def test_kx108_hold_persists_failure_envelope_and_does_not_call_executor(monkeypatch, tmp_path):
    _store_approval(monkeypatch)
    _kx(monkeypatch, "HOLD")
    ex = _checkbox_executor()
    prep = _prep_checked(tmp_path, ex)

    result = _execute_checked(tmp_path, prep, ex)
    env = result["canonical_receipt_envelope"]

    assert result["status"] == PC2.EXECUTE_REJECTED
    assert env["realized_state"]["outcome"] == CRE.OUTCOME_KX108_HOLD
    assert env["realized_state"]["failure_stage"] == CRE.STAGE_KX108
    assert env["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
    assert env["execution"]["physical_effect_dispatched"] is False
    assert env["authorization"]["kx108_verdict"] == "HOLD"
    ex.set_checkbox.assert_not_called()
    assert CRE.verify_canonical_receipt_envelope(env)[0]

def test_toctou_abort_persists_pre_and_current_evidence_without_executor(tmp_path):
    ex = _checkbox_executor()
    prep = _prep_checked(tmp_path, ex)
    ex.inspect_checkbox.side_effect = [_chk(metadata="changed-meta")]

    result = _execute_checked(tmp_path, prep, ex)
    env = result["canonical_receipt_envelope"]

    assert result["status"] == PC2.EXECUTE_REJECTED
    assert env["realized_state"]["outcome"] == CRE.OUTCOME_TOCTOU_ABORTED
    assert env["realized_state"]["failure_stage"] == CRE.STAGE_TOCTOU
    assert env["realized_state"]["prepared_pre_state_hash"] == prep["physical_state_anchor"]
    assert env["realized_state"]["current_state_hash"]
    assert env["authorization"]["approval_status"] == CRE.STATUS_NOT_REACHED
    assert env["authorization"]["kx108_verdict"] == CRE.STATUS_NOT_REACHED
    assert env["execution"]["physical_effect_dispatched"] is False
    assert env["execution"]["executor_status"] == CRE.STATUS_NOT_REACHED
    ex.set_checkbox.assert_not_called()
    assert CRE.verify_canonical_receipt_envelope(env)[0]


def test_postcondition_mismatch_persists_dispatched_mismatch(monkeypatch, tmp_path):
    _store_approval(monkeypatch)
    _kx(monkeypatch, "ALLOW")
    ex = _checkbox_executor(pre=_chk(checked=False), post=_chk(checked=False))
    prep = _prep_checked(tmp_path, ex)

    result = _execute_checked(tmp_path, prep, ex)
    env = result["canonical_receipt_envelope"]

    assert result["status"] == PC2.EXECUTE_REJECTED
    assert env["realized_state"]["outcome"] == CRE.OUTCOME_REALIZED_STATE_MISMATCH
    assert env["realized_state"]["failure_stage"] == CRE.STAGE_POST_OBSERVATION
    assert env["execution"]["executor_status"] == "INVOKED"
    assert env["execution"]["physical_effect_dispatched"] is True
    assert env["execution"]["executor_evidence_hash"]
    assert env["realized_state"]["post_state_hash"]
    assert env["realized_state"]["post_state_ref"]["checked"] is False
    ex.set_checkbox.assert_called_once()
    assert CRE.verify_canonical_receipt_envelope(env)[0]


def _form(**kw):
    d = {
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
        "id": "f1",
        "autocomplete": "",
        "same_origin_action": True,
        "submitter_selector": "button#go",
        "submitter_count": 1,
        "submitter_tag": "button",
        "submitter_type": "submit",
        "submitter_name": "go",
        "submitter_value_sha256": PC2._sha256_text("Search"),
        "submitter_value_length": 6,
        "submitter_form_owner": "",
        "submitter_belongs_to_form": True,
        "submitter_visible": True,
        "submitter_enabled": True,
        "submitter_text_sha256": PC2._sha256_text("Search"),
        "field_manifest_hash": PC2._sha256_text("plain-query-value"),
        "field_count": 2,
        "contains_password": False,
        "contains_otp_sensitive": False,
        "contains_payment_sensitive": False,
        "metadata_sha256": "form-meta",
        "submitter_metadata_sha256": "submit-meta",
        "main_frame_only": True,
        "physical_state_anchor": "psa-submit",
        "redirect_policy": "SAME_ORIGIN_REDIRECT_CHAIN",
        "expected_effect": "NAVIGATION",
    }
    d.update(kw)
    return d


def _submit_executor(act):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = _form()
    ex.inspect_form_submission.side_effect = [pre, pre]
    ex.submit_get_navigation.return_value = act
    return ex


def test_submit_dispatched_uncertain_persists_post_dispatch_uncertainty(monkeypatch, tmp_path):
    _store_approval(monkeypatch)
    _kx(monkeypatch, "ALLOW")
    ex = _submit_executor({
        "ok": True,
        "request_observed": True,
        "request_method": "GET",
        "request_url_hash": "req-hash",
        "request_endpoint": "https://example.com/results",
        "request_fingerprint": "fp",
        "response_observed": False,
        "final_url_hash": "final-hash",
        "execution_state": "DISPATCHED_OUTCOME_UNCERTAIN",
        "uncertain_reason": "NAVIGATION_TIMEOUT_AFTER_REQUEST",
        "transport_proof": "STRONG",
        "navigation_proof": "UNCERTAIN",
    })
    prep = PC2.pc_v2_browser_submit_get_navigation_prepare(
        "form#search", "button#go", "search", "HIGH", "NORMAL_GET_NAVIGATION",
        stores_base_dir=tmp_path / "s", executor=ex)

    result = PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "HUMAN_REF",
        stores_base_dir=tmp_path / "s", executor=ex)
    env = result["canonical_receipt_envelope"]

    assert result["status"] == "EXECUTED_OUTCOME_UNCERTAIN"
    assert env["realized_state"]["outcome"] == CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN
    assert env["realized_state"]["dispatch_boundary"] == CRE.DISPATCH_POST_UNCERTAINTY
    assert env["realized_state"]["physical_effect_dispatched"] is True
    assert env["execution"]["automatic_retry"] is False
    assert env["replay"]["physical_replay_allowed"] is False
    assert env["privacy"]["get_query_plaintext_persisted"] is False
    assert "plain-query-value" not in json.dumps(env, sort_keys=True)
    assert CRE.verify_canonical_receipt_envelope(env)[0]


def test_failure_envelope_immutability_tamper_and_determinism(monkeypatch, tmp_path):
    _store_approval(monkeypatch)
    _kx(monkeypatch, "BLOCK")
    ex = _checkbox_executor()
    prep = _prep_checked(tmp_path, ex)
    result = _execute_checked(tmp_path, prep, ex)
    env = result["canonical_receipt_envelope"]

    assert CRE.canonical_json(env) == CRE.canonical_json(copy.deepcopy(env))
    assert CRE.compute_envelope_hash(env) == env["envelope_hash"]
    assert CRE.store_canonical_receipt_envelope(env, tmp_path / "s" / "receipts")["status"] == CRE.STATUS_IDEMPOTENT

    tampered = copy.deepcopy(env)
    tampered["created_at"] = "2026-10-07T00:00:01+00:00"
    tampered["envelope_hash"] = CRE.compute_envelope_hash(tampered)
    assert tampered["action_evidence_id"] == env["action_evidence_id"]
    assert CRE.store_canonical_receipt_envelope(tampered, tmp_path / "s" / "receipts")["status"] == CRE.STATUS_IMMUTABILITY_VIOLATION
    assert CRE.verify_canonical_receipt_envelope(tampered)[0]
