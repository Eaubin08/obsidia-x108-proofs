from __future__ import annotations

import copy
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
SESSION_ID = "sess-r8b1"
PAGE_ID = "page-r8b1"


def _minimal_envelope(created_at="2026-10-07T00:00:00+00:00"):
    return CRE.build_canonical_receipt_envelope(
        capability="PC_V2_BROWSER_SET_CHECKED_EXECUTE",
        operation_type="V2_BROWSER_SET_CHECKED",
        created_at=created_at,
        request_ref={"public_action": "BROWSER_SET_CHECKED", "selector_hash": "h", "target_checked": True},
        session_ref={"session_id": "s", "v2_exec_id": "v2x", "child_id": "chd"},
        prepare={
            "descriptor_ref": "v2x",
            "descriptor_hash": "dh",
            "physical_state_anchor": "psa",
            "state_anchor_kind": "PHYSICAL_PRE_STATE",
        },
        authorization={
            "execution_authority_hash": "a" * 64,
            "approval_id": "apv-test",
            "approval_status": "APPROVED_FOR_BOUNDED_EXECUTION",
            "approved_by": "HUMAN",
            "kx108_pre_decision_record_id": "kxpre-test",
            "kx108_pre_decision_record_hash": "b" * 64,
            "kx108_verdict": "ALLOW",
            "binder_verdict_status": "OBSERVED_INLINE",
            "binder_verdict_ref": "NOT_SEPARATELY_PERSISTED",
        },
        execution={
            "executor_kind": "JARJAR",
            "executor_backend": "BrowserBackend",
            "executor_operation": "browser.set_checkbox",
            "executor_input_hash": "c" * 64,
            "mutation_performed": True,
            "execution_state": "POSTCONDITION_CONFIRMED",
        },
        realized_state={
            "proof_strength": "STRONG",
            "realized_state_verified": True,
            "mutation_performed": True,
            "post_state_hash": "d" * 64,
            "execution_state": "POSTCONDITION_CONFIRMED",
            "uncertainty_state": "NONE",
            "uncertainty_reason": "",
        },
        receipt={
            "existing_runtime_receipt_id": "pcrcp-v2-test",
            "existing_receipt_hash": "e" * 64,
            "existing_receipt_ref": "runtime_result.receipt",
        },
    )


def test_canonical_schema_identity_hash_and_serialization_are_deterministic():
    a = _minimal_envelope()
    b = _minimal_envelope()
    assert a["schema_version"] == CRE.SCHEMA_VERSION
    assert a["action_evidence_id"].startswith("aev-")
    assert a["action_evidence_id"] == b["action_evidence_id"]
    assert a["envelope_hash"] == b["envelope_hash"]
    assert CRE.canonical_json(a) == CRE.canonical_json(b)
    ok, reason = CRE.verify_canonical_receipt_envelope(a)
    assert ok, reason


def test_tamper_changes_hash_and_conflicting_overwrite_is_rejected(tmp_path):
    env = _minimal_envelope()
    stored = CRE.store_canonical_receipt_envelope(env, tmp_path)
    assert stored["status"] == CRE.STATUS_STORED
    assert CRE.store_canonical_receipt_envelope(env, tmp_path)["status"] == CRE.STATUS_IDEMPOTENT

    tampered = copy.deepcopy(env)
    tampered["created_at"] = "2026-10-07T00:00:01+00:00"
    tampered["envelope_hash"] = CRE.compute_envelope_hash(tampered)
    assert tampered["action_evidence_id"] == env["action_evidence_id"]
    assert tampered["envelope_hash"] != env["envelope_hash"]
    assert CRE.store_canonical_receipt_envelope(tampered, tmp_path)["status"] == CRE.STATUS_IMMUTABILITY_VIOLATION


def test_rejects_plaintext_sensitive_or_physical_replay():
    env = _minimal_envelope()
    bad = copy.deepcopy(env)
    bad["privacy"]["plaintext_sensitive_data_present"] = True
    bad["envelope_hash"] = CRE.compute_envelope_hash(bad)
    assert CRE.verify_canonical_receipt_envelope(bad)[1] == "PLAINTEXT_SENSITIVE_DATA_PRESENT"

    replay = copy.deepcopy(env)
    replay["replay"]["physical_replay_allowed"] = True
    replay["envelope_hash"] = CRE.compute_envelope_hash(replay)
    assert CRE.verify_canonical_receipt_envelope(replay)[1] == "PHYSICAL_REPLAY_ALLOWED"


def _chk(*, checked=False, metadata="meta-r8b1"):
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
        "form_owner": "f1",
        "checked": checked,
        "indeterminate_status": "FALSE_PROVEN",
        "metadata_sha256": metadata,
        "visible": True,
        "enabled": True,
        "closed": False,
        "main_frame": True,
    }


def _ex(pre=None, post=None, act=None):
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


def _allow(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(
        PC2,
        "_kx108_pre",
        lambda *_a, **_k: {
            "verify_ok": True,
            "x108_gate": "ALLOW",
            "decision_record_id": "kxpre-r8b1",
            "record": {"decision_record_hash": "b" * 64},
        },
    )


def _run_set_checked(tmp_path, monkeypatch, *, pre_checked):
    _allow(monkeypatch)
    ex = _ex(pre=_chk(checked=pre_checked), post=_chk(checked=True))
    prep = PC2.pc_v2_browser_set_checked_prepare(
        "input#agree",
        True,
        "accept_settings",
        "LOW",
        stores_base_dir=tmp_path / "s",
        executor=ex,
    )
    return PC2.pc_v2_browser_set_checked_execute(
        prep,
        prep["execution_authority_hash"],
        "HUMAN_REF",
        stores_base_dir=tmp_path / "s",
        executor=ex,
    )


def test_browser_set_checked_success_emits_canonical_envelope(monkeypatch, tmp_path):
    result = _run_set_checked(tmp_path, monkeypatch, pre_checked=False)
    env = result["canonical_receipt_envelope"]
    assert result["status"] == PC2.EXECUTED_OK
    assert result["action_evidence_id"] == env["action_evidence_id"]
    assert result["canonical_receipt_store_status"] == CRE.STATUS_STORED
    assert env["prepare"]["descriptor_ref"].startswith("v2x-")
    assert env["prepare"]["descriptor_hash"] == result["canonical_receipt_envelope"]["prepare"]["descriptor_hash"]
    assert env["prepare"]["physical_state_anchor"]
    assert env["prepare"]["state_anchor_kind"] == "PHYSICAL_PRE_STATE"
    assert env["authorization"]["execution_authority_hash"]
    assert env["authorization"]["approval_id"].startswith("apv-")
    assert env["authorization"]["kx108_pre_decision_record_id"] == "kxpre-r8b1"
    assert env["authorization"]["binder_verdict_status"] == "OBSERVED_INLINE"
    assert env["authorization"]["binder_verdict_ref"] == "NOT_SEPARATELY_PERSISTED"
    assert env["execution"]["executor_input_hash"]
    assert env["execution"]["mutation_performed"] is True
    assert env["realized_state"]["realized_state_verified"] is True
    assert env["realized_state"]["uncertainty_state"] == "NONE"
    assert env["replay"]["physical_replay_allowed"] is False
    assert env["replay"]["evidence_replay_allowed"] is True
    assert env["privacy"]["plaintext_sensitive_data_present"] is False
    assert "secret" not in CRE.canonical_json(env).lower()
    ok, reason = CRE.verify_canonical_receipt_envelope(env)
    assert ok, reason


def test_browser_set_checked_noop_emits_canonical_envelope(monkeypatch, tmp_path):
    result = _run_set_checked(tmp_path, monkeypatch, pre_checked=True)
    env = result["canonical_receipt_envelope"]
    assert result["status"] == PC2.EXECUTED_OK
    assert result["mutation_performed"] is False
    assert env["execution"]["mutation_performed"] is False
    assert env["realized_state"]["mutation_performed"] is False
    assert env["realized_state"]["execution_state"] == "POSTCONDITION_CONFIRMED"
    assert env["realized_state"]["proof_strength"] == "STRONG"
