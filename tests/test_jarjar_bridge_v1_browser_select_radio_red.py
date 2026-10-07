from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import jarjar_browser_bridge_v0 as BBRIDGE
import obsidia_pc_capabilities_v2 as PC2

URL = "https://example.com/page"
SESSION_ID = "sess-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID = "page-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
GROUP = "group-111"


def _rad(
    *,
    checked=False,
    selector="input#pro",
    sid=SESSION_ID,
    pid=PAGE_ID,
    url=URL,
    origin="https://example.com",
    count=1,
    tag="input",
    typ="radio",
    visible=True,
    enabled=True,
    closed=False,
    metadata="meta-1",
    group=GROUP,
    main_frame=True,
    name="plan",
    element_id="pro",
    form_owner="f1",
):
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": origin,
        "selector": selector,
        "element_count": count,
        "tag_name": tag,
        "type": typ,
        "role": "",
        "name": name,
        "id": element_id,
        "form_owner": form_owner,
        "checked": checked,
        "radio_group_identity": group,
        "metadata_sha256": metadata,
        "visible": visible,
        "enabled": enabled,
        "closed": closed,
        "main_frame": main_frame,
    }


def _ex(pre=None, post=None, act=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = pre or _rad()
    post = post or _rad(checked=True)
    ex.inspect_radio.side_effect = [pre, pre, pre, post, post]
    ex.select_radio.return_value = act or {
        "ok": True,
        "mutation_performed": pre["checked"] is not True,
        "checked": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None, intent="choose_plan", risk="MEDIUM"):
    ex = ex or _ex()
    return PC2.pc_v2_browser_select_radio_prepare(
        "input#pro", intent, risk, stores_base_dir=tmp_path / "s", executor=ex)


def test_registration_graph_and_boundaries(tmp_path):
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_SELECT_RADIO_PREPARE",
        selector="input#pro", semantic_intent="intent",
        semantic_risk="LOW", stores_base_dir=tmp_path / "s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_SELECT_RADIO_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_SELECT_RADIO_EXECUTE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SET_RADIO")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SUBMIT")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_radio")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "select_radio")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")


def test_prepare_non_mutating_success_and_semantic_binding(tmp_path):
    for pre in (_rad(checked=False), _rad(checked=True)):
        ex = _ex(pre=pre, post=pre)
        r = PC2.pc_v2_browser_select_radio_prepare(
            pre["selector"], "billing_choice", "HIGH",
            stores_base_dir=tmp_path / str(pre["checked"]), executor=ex)
        assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
        assert r["public_action"] == "BROWSER_SELECT_RADIO"
        assert r["desired_selected"] is True
        assert r["semantic_intent"] == "billing_choice"
        assert r["semantic_risk"] == "HIGH"
        assert r["radio_group_identity"] == GROUP
        ex.select_radio.assert_not_called()


def test_prepare_rejections(tmp_path):
    cases = [
        (_rad(sid=""), "PAGE_IDENTITY_MISSING"),
        (_rad(pid=""), "PAGE_IDENTITY_MISSING"),
        (_rad(closed=True), "PAGE_CLOSED"),
        (_rad(count=0), "SELECTOR_COUNT"),
        (_rad(count=2), "SELECTOR_COUNT"),
        (_rad(tag="button"), "UNSUPPORTED_RADIO_TARGET"),
        (_rad(typ="checkbox"), "UNSUPPORTED_RADIO_TARGET"),
        (_rad(visible=False), "ELEMENT_NOT_VISIBLE"),
        (_rad(enabled=False), "ELEMENT_NOT_ENABLED"),
        (_rad(name="", group=""), "RADIO_GROUP_IDENTITY_INVALID"),
        (_rad(group=""), "RADIO_GROUP_IDENTITY_INVALID"),
        (_rad(main_frame=False), "IFRAME_UNSUPPORTED"),
    ]
    for i, (pre, reason) in enumerate(cases):
        ex = _ex(pre=pre, post=pre)
        r = PC2.pc_v2_browser_select_radio_prepare(
            "input#pro", "intent", "LOW", stores_base_dir=tmp_path / f"s{i}", executor=ex)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_prepare_semantic_rejections(tmp_path):
    for intent, risk, reason in (
        ("", "LOW", "SEMANTIC_INTENT_REQUIRED"),
        ("intent", "", "SEMANTIC_RISK_INVALID"),
        ("intent", "CRITICAL", "SEMANTIC_RISK_INVALID"),
    ):
        r = PC2.pc_v2_browser_select_radio_prepare(
            "input#pro", intent, risk, stores_base_dir=tmp_path / reason, executor=_ex())
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_execute_eah_missing_approval_binder_kx_reject(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_select_radio_execute(
        prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert "DESCRIPTOR_EAH_MISMATCH" in PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "other", executor=ex)["reason"]

    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "FAILED"})
    r = PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert "APPROVAL_STORE_FAILED" in r["reason"]

    ex = _ex()
    prep = _prep(tmp_path / "kx", ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    r = PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "kx" / "s", executor=ex)
    assert "KX108_PRE_GATE:BLOCK" in r["reason"]


def test_toctou_drifts_rejected(tmp_path):
    cases = [
        _rad(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _rad(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _rad(url="https://example.com/other"),
        _rad(origin="https://other.example.com"),
        _rad(metadata="meta-2"),
        _rad(group="group-222"),
        _rad(checked=True),
        _rad(visible=False),
        _rad(enabled=False),
    ]
    for i, drift in enumerate(cases):
        ex = _ex()
        prep = _prep(tmp_path / f"d{i}", ex)
        ex.inspect_radio.side_effect = [drift]
        r = PC2.pc_v2_browser_select_radio_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"d{i}" / "s", executor=ex)
        assert r["status"] == PC2.EXECUTE_REJECTED
        ex.select_radio.assert_not_called()


def test_success_mutation_noop_and_side_effect_rejections(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    ex = _ex(pre=_rad(checked=False), post=_rad(checked=True))
    prep = _prep(tmp_path / "ok", ex)
    r = PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "ok" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["mutation_performed"] is True
    assert r["current_checked"] is True
    assert r["realized_state_verified"] is True
    assert r["peer_deselection_proof"] == "DEFER_V1"

    ex = _ex(pre=_rad(checked=True), post=_rad(checked=True),
             act={"ok": True, "mutation_performed": False})
    prep = _prep(tmp_path / "noop", ex)
    r = PC2.pc_v2_browser_select_radio_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "noop" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["mutation_performed"] is False

    for flag, reason in (
        ("navigation_detected", "UNEXPECTED_NAVIGATION"),
        ("popup_detected", "UNEXPECTED_POPUP"),
        ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
        ("download_detected", "UNEXPECTED_DOWNLOAD"),
    ):
        ex = _ex(act={"ok": True, flag: True})
        prep = _prep(tmp_path / flag, ex)
        r = PC2.pc_v2_browser_select_radio_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / flag / "s", executor=ex)
        assert reason in r["reason"]


def test_post_identity_group_and_state_mismatch_reject(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    cases = [
        (_rad(sid="", checked=True), "POST_SESSION_ID_MISSING"),
        (_rad(pid="", checked=True), "POST_PAGE_ID_MISSING"),
        (_rad(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", checked=True), "POST_SESSION_ID_DRIFT"),
        (_rad(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", checked=True), "POST_PAGE_ID_DRIFT"),
        (_rad(metadata="meta-2", checked=True), "POST_ELEMENT_IDENTITY_DRIFT"),
        (_rad(group="group-222", checked=True), "POST_ELEMENT_IDENTITY_DRIFT"),
        (_rad(checked=False), PC2.REALIZED_STATE_MISMATCH),
    ]
    for i, (post, reason) in enumerate(cases):
        ex = _ex(pre=_rad(checked=False), post=post)
        prep = _prep(tmp_path / f"p{i}", ex)
        r = PC2.pc_v2_browser_select_radio_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"p{i}" / "s", executor=ex)
        assert reason in r["reason"]
