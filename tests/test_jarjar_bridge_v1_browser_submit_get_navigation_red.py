from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import jarjar_browser_bridge_v0 as BBRIDGE
import obsidia_pc_capabilities_v2 as PC2


URL = "https://example.com/search"
SESSION_ID = "sess-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID = "page-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _form(**kw):
    d = {
        "ok": True,
        "browser_session_id": SESSION_ID,
        "page_id": PAGE_ID,
        "url": URL,
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
        "field_manifest_hash": "manifest-hash",
        "field_count": 2,
        "contains_password": False,
        "contains_otp_sensitive": False,
        "contains_payment_sensitive": False,
        "metadata_sha256": "form-meta",
        "submitter_metadata_sha256": "submit-meta",
        "main_frame_only": True,
        "physical_state_anchor": "psa-1",
        "redirect_policy": "SAME_ORIGIN_REDIRECT_CHAIN",
        "expected_effect": "NAVIGATION",
    }
    d.update(kw)
    return d


def _ex(pre=None, act=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = pre or _form()
    ex.inspect_form_submission.side_effect = [pre, pre, pre]
    ex.submit_get_navigation.return_value = act or {
        "ok": True,
        "request_observed": True,
        "request_method": "GET",
        "request_url_hash": "req-hash",
        "request_endpoint": "https://example.com/results",
        "request_fingerprint": "req-fp",
        "response_observed": True,
        "response_status": 200,
        "response_url_hash": "resp-hash",
        "final_url_hash": "final-hash",
        "final_url_endpoint": "https://example.com/results",
        "execution_state": "POSTCONDITION_CONFIRMED",
        "transport_proof": "STRONG",
        "navigation_proof": "STRONG",
        "application_proof": "NOT_CLAIMED",
    }
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None, cls="NORMAL_GET_NAVIGATION", risk="HIGH", intent="search"):
    return PC2.pc_v2_browser_submit_get_navigation_prepare(
        "form#search", "button#go", intent, risk, cls,
        stores_base_dir=tmp_path / "s", executor=ex or _ex())


def _stored_descriptor(tmp_path, prep):
    path = tmp_path / "s" / "v2exec" / f"{prep['v2_exec_id']}.json"
    return json.loads(path.read_text(encoding="utf-8"))["descriptor"]


def test_registration_graph_bridge_and_no_generic_surfaces(tmp_path):
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_SUBMIT_GET_NAV_PREPARE",
        form_selector="form#search", submitter_selector="button#go",
        semantic_intent="search", semantic_risk="LOW",
        submission_class="NORMAL_GET_NAVIGATION", stores_base_dir=tmp_path / "s",
    )
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_SUBMIT_GET_NAV_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_SUBMIT_GET_NAV_EXECUTE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SUBMIT")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_POST")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_form_submission")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "submit_get_navigation")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "submit")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")


def test_prepare_accepts_get_same_origin_and_persists_hash_only(tmp_path):
    secret = "plain-query-value"
    ex = _ex(pre=_form(field_manifest_hash=PC2._sha256_text(secret)))
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["public_action"] == "BROWSER_SUBMIT_FORM_NAVIGATION_V0"
    assert r["field_manifest_hash"] == PC2._sha256_text(secret)
    assert r["plaintext_form_data_persisted"] is False
    assert secret not in json.dumps(r, sort_keys=True)
    assert secret not in json.dumps(_stored_descriptor(tmp_path, r), sort_keys=True)
    ex.submit_get_navigation.assert_not_called()


def test_prepare_rejections(tmp_path):
    cases = [
        (_form(form_count=0), "FORM_COUNT_NOT_ONE"),
        (_form(form_count=2), "FORM_COUNT_NOT_ONE"),
        (_form(form_tag="div"), "FORM_TAG_REQUIRED"),
        (_form(method="post"), "FORM_METHOD_NOT_GET"),
        (_form(same_origin_action=False), "CROSS_ORIGIN_ACTION_UNSUPPORTED"),
        (_form(target="_blank"), "FORM_TARGET_NEW_CONTEXT_UNSUPPORTED"),
        (_form(submitter_count=0), "SUBMITTER_COUNT_NOT_ONE"),
        (_form(submitter_count=2), "SUBMITTER_COUNT_NOT_ONE"),
        (_form(submitter_belongs_to_form=False), "SUBMITTER_FORM_OWNER_MISMATCH"),
        (_form(contains_password=True), "PASSWORD_FORM_DEFERRED"),
        (_form(contains_otp_sensitive=True), "OTP_FORM_DEFERRED"),
        (_form(contains_payment_sensitive=True), "PAYMENT_FORM_DEFERRED"),
        (_form(main_frame_only=False), "IFRAME_UNSUPPORTED"),
    ]
    for i, (pre, reason) in enumerate(cases):
        r = _prep(tmp_path / f"r{i}", _ex(pre=pre))
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]
    assert "SEMANTIC_INTENT_REQUIRED" in _prep(tmp_path / "intent", _ex(), intent="")["reason"]
    assert "SEMANTIC_RISK_INVALID" in _prep(tmp_path / "risk", _ex(), risk="CRITICAL")["reason"]
    assert "SUBMISSION_CLASS_UNSUPPORTED" in _prep(tmp_path / "login", _ex(), cls="LOGIN")["reason"]
    assert "SUBMISSION_CLASS_INVALID" in _prep(tmp_path / "unknown", _ex(), cls="SOMETHING")["reason"]


def test_execute_eah_approval_kx_and_toctou(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED" in PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "", stores_base_dir=tmp_path / "s", executor=ex)["reason"]
    assert "DESCRIPTOR_EAH_MISMATCH" in PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "other", executor=ex)["reason"]

    ex = _ex()
    prep = _prep(tmp_path / "drift", ex)
    ex.inspect_form_submission.side_effect = [_form(field_manifest_hash="changed")]
    r = PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "drift" / "s", executor=ex)
    assert "FORM_SUBMISSION_IDENTITY_DRIFT" in r["reason"]
    ex.submit_get_navigation.assert_not_called()

    ex = _ex()
    prep = _prep(tmp_path / "kx", ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    assert "KX108_PRE_GATE:BLOCK" in PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "kx" / "s", executor=ex)["reason"]


def test_execute_states_privacy_replay_and_no_retry(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    for state, expected_status in [
        ("POSTCONDITION_CONFIRMED", PC2.EXECUTED_OK),
        ("DISPATCHED_OUTCOME_UNCERTAIN", "EXECUTED_OUTCOME_UNCERTAIN"),
        ("RESPONSE_OBSERVED", "EXECUTED_OUTCOME_UNCERTAIN"),
        ("DISPATCHED", "EXECUTED_OUTCOME_UNCERTAIN"),
    ]:
        ex = _ex(act={
            "ok": True,
            "request_observed": True,
            "request_method": "GET",
            "request_url_hash": "req-hash",
            "request_fingerprint": "fp",
            "response_observed": state in {"RESPONSE_OBSERVED", "POSTCONDITION_CONFIRMED"},
            "response_status": 200,
            "response_url_hash": "resp-hash",
            "final_url_hash": "final-hash",
            "execution_state": state,
            "transport_proof": "STRONG",
            "navigation_proof": "STRONG" if state == "POSTCONDITION_CONFIRMED" else "UNCERTAIN",
        })
        prep = _prep(tmp_path / state, ex)
        r = PC2.pc_v2_browser_submit_get_navigation_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / state / "s", executor=ex)
        assert r["status"] == expected_status
        assert r["execution_state"] == state
        assert r["automatic_retry"] is False
        assert r["replay_physical_action_allowed"] is False
        assert r["idempotency_assumed"] is False
        assert r["application_proof"] is False
        assert "plain-query-value" not in json.dumps(r, sort_keys=True)

    ex = _ex(act={"ok": False, "error": "REQUEST_NOT_OBSERVED", "execution_state": "NOT_DISPATCHED"})
    prep = _prep(tmp_path / "none", ex)
    r = PC2.pc_v2_browser_submit_get_navigation_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "none" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "SUBMIT_GET_NAVIGATION_FAILED" in r["reason"]
