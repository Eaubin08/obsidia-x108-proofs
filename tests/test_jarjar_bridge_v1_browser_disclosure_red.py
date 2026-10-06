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


def _disc(
    *,
    cls="DETAILS_OPEN",
    expanded=False,
    selector="details#x",
    sid=SESSION_ID,
    pid=PAGE_ID,
    url=URL,
    origin="https://example.com",
    count=1,
    visible=True,
    enabled=True,
    closed=False,
    metadata="meta-1",
    aria_expanded=None,
    aria_controls="panel",
    main_frame=True,
):
    if aria_expanded is None and cls == "ARIA_EXPANDED":
        aria_expanded = "true" if expanded else "false"
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": origin,
        "selector": selector,
        "element_count": count,
        "visible": visible,
        "enabled": enabled,
        "closed": closed,
        "tag_name": "details" if cls == "DETAILS_OPEN" else "button",
        "role": "",
        "aria_expanded": aria_expanded,
        "aria_controls": aria_controls,
        "open": bool(expanded) if cls == "DETAILS_OPEN" else False,
        "disclosure_class": cls,
        "current_expanded": expanded,
        "text_sha256": "text-sha",
        "metadata_sha256": metadata,
        "main_frame": main_frame,
    }


def _ex(pre=None, post=None, act=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = pre or _disc()
    post = post or _disc(expanded=True)
    ex.inspect_disclosure.side_effect = [pre, pre, post, post, post]
    ex.set_disclosure.return_value = act or {
        "ok": True,
        "mutation_performed": pre["current_expanded"] is not True,
        "current_expanded": True,
        "target_expanded": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None, target=True):
    ex = ex or _ex()
    return PC2.pc_v2_browser_set_disclosure_prepare(
        "details#x", target, stores_base_dir=tmp_path / "s", executor=ex)


def test_registration_graph_and_boundaries():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_SET_DISCLOSURE_PREPARE",
        selector="details#x", target_expanded=True, stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_SET_DISCLOSURE_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_SET_DISCLOSURE_EXECUTE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_disclosure")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "set_disclosure")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")


def test_prepare_no_mutation_and_success_classes(tmp_path):
    for pre, target in (
        (_disc(cls="DETAILS_OPEN", expanded=False), True),
        (_disc(cls="DETAILS_OPEN", expanded=True), False),
        (_disc(cls="ARIA_EXPANDED", expanded=False, selector="button#x"), True),
        (_disc(cls="ARIA_EXPANDED", expanded=True, selector="button#x"), False),
    ):
        ex = _ex(pre=pre, post=pre)
        r = PC2.pc_v2_browser_set_disclosure_prepare(
            pre["selector"], target, stores_base_dir=tmp_path / ("s" + pre["disclosure_class"] + str(target)), executor=ex)
        assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
        assert r["public_action"] == "BROWSER_SET_DISCLOSURE"
        assert r["target_expanded"] is target
        ex.set_disclosure.assert_not_called()


def test_prepare_rejections(tmp_path):
    cases = [
        (_disc(sid=""), "PAGE_IDENTITY_MISSING"),
        (_disc(pid=""), "PAGE_IDENTITY_MISSING"),
        (_disc(closed=True), "PAGE_CLOSED"),
        (_disc(count=0), "SELECTOR_COUNT"),
        (_disc(count=2), "SELECTOR_COUNT"),
        (_disc(visible=False), "ELEMENT_NOT_VISIBLE"),
        (_disc(enabled=False), "ELEMENT_NOT_ENABLED"),
        (_disc(cls="", expanded=None), "UNSUPPORTED_DISCLOSURE_CLASS"),
        (_disc(cls="ARIA_EXPANDED", aria_expanded="mixed", expanded=None), "DISCLOSURE_STATE_UNREADABLE"),
        (_disc(main_frame=False), "IFRAME_UNSUPPORTED"),
    ]
    for i, (pre, reason) in enumerate(cases):
        ex = _ex(pre=pre, post=pre)
        r = PC2.pc_v2_browser_set_disclosure_prepare(
            pre.get("selector") or "details#x", True, stores_base_dir=tmp_path / f"s{i}", executor=ex)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_execute_eah_missing_approval_binder_kx_reject(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_set_disclosure_execute(
        prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert PC2.pc_v2_browser_set_disclosure_execute(
        prep, prep["execution_authority_hash"], "", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED

    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "FAILED"})
    r = PC2.pc_v2_browser_set_disclosure_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert "APPROVAL_STORE_FAILED" in r["reason"]

    ex = _ex()
    prep = _prep(tmp_path / "kx", ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    r = PC2.pc_v2_browser_set_disclosure_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "kx" / "s", executor=ex)
    assert "KX108_PRE_GATE:BLOCK" in r["reason"]


def test_toctou_drifts_rejected(tmp_path):
    cases = [
        _disc(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _disc(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _disc(url="https://example.com/other"),
        _disc(origin="https://other.example.com"),
        _disc(metadata="meta-2"),
        _disc(expanded=True),
        _disc(visible=False),
        _disc(enabled=False),
    ]
    for i, drift in enumerate(cases):
        ex = _ex()
        prep = _prep(tmp_path / f"d{i}", ex)
        ex.inspect_disclosure.side_effect = [drift]
        r = PC2.pc_v2_browser_set_disclosure_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"d{i}" / "s", executor=ex)
        assert r["status"] == PC2.EXECUTE_REJECTED
        ex.set_disclosure.assert_not_called()


def test_success_mutation_noop_and_side_effect_rejections(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    ex = _ex(pre=_disc(expanded=False), post=_disc(expanded=True))
    prep = _prep(tmp_path / "ok", ex, True)
    r = PC2.pc_v2_browser_set_disclosure_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "ok" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["mutation_performed"] is True
    assert r["current_expanded"] is True

    ex = _ex(pre=_disc(expanded=True), post=_disc(expanded=True),
             act={"ok": True, "mutation_performed": False})
    prep = _prep(tmp_path / "noop", ex, True)
    r = PC2.pc_v2_browser_set_disclosure_execute(
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
        prep = _prep(tmp_path / flag, ex, True)
        r = PC2.pc_v2_browser_set_disclosure_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / flag / "s", executor=ex)
        assert reason in r["reason"]


def test_post_identity_and_state_mismatch_reject(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    cases = [
        (_disc(sid="", expanded=True), "POST_SESSION_ID_MISSING"),
        (_disc(pid="", expanded=True), "POST_PAGE_ID_MISSING"),
        (_disc(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", expanded=True), "POST_SESSION_ID_DRIFT"),
        (_disc(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", expanded=True), "POST_PAGE_ID_DRIFT"),
        (_disc(metadata="meta-2", expanded=True), "POST_ELEMENT_IDENTITY_DRIFT"),
        (_disc(expanded=False), PC2.REALIZED_STATE_MISMATCH),
    ]
    for i, (post, reason) in enumerate(cases):
        ex = _ex(pre=_disc(expanded=False), post=post)
        prep = _prep(tmp_path / f"p{i}", ex, True)
        r = PC2.pc_v2_browser_set_disclosure_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"p{i}" / "s", executor=ex)
        assert reason in r["reason"]
