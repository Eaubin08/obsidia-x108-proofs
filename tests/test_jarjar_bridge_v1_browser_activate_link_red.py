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

PRE_URL = "https://example.com/start"
DEST_URL = "https://example.com/dest"
SESSION_ID = "sess-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID = "page-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _link(
    *,
    url=PRE_URL,
    sid=SESSION_ID,
    pid=PAGE_ID,
    selector="a#go",
    count=1,
    href="/dest",
    resolved=DEST_URL,
    visible=True,
    enabled=True,
    closed=False,
    role="link",
    tag_name="a",
    link_class="href_link",
    metadata="meta-1",
):
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": "https://example.com",
        "selector": selector,
        "element_count": count,
        "visible": visible,
        "enabled": enabled,
        "closed": closed,
        "tag_name": tag_name,
        "role": role,
        "href": href,
        "resolved_href": resolved,
        "name": "",
        "aria_label": "",
        "text_sha256": "text-sha",
        "metadata_sha256": metadata,
        "main_frame": True,
        "link_class": link_class,
    }


def _state(url=DEST_URL, sid=SESSION_ID, pid=PAGE_ID, closed=False):
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": "https://example.com",
        "title": "Post",
        "closed": closed,
    }


def _ex():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    ex.inspect_link.return_value = _link()
    ex.activate_link.return_value = {
        "ok": True,
        "final_url": DEST_URL,
        "browser_session_id": SESSION_ID,
        "page_id": PAGE_ID,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    ex.read_browser_state.return_value = _state()
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None):
    ex = ex or _ex()
    return PC2.pc_v2_browser_activate_link_prepare("a#go", stores_base_dir=tmp_path / "s", executor=ex)


def test_activate_link_caps_registered():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_ACTIVATE_LINK_PREPARE", selector="a#go", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"


def test_prepare_no_mutation(tmp_path):
    ex = _ex()
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    ex.activate_link.assert_not_called()


def test_prepare_identity_missing_and_closed_rejected(tmp_path):
    for link, reason in (
        (_link(sid=""), "PAGE_IDENTITY_MISSING"),
        (_link(pid=""), "PAGE_IDENTITY_MISSING"),
        (_link(closed=True), "PAGE_CLOSED"),
    ):
        ex = _ex()
        ex.inspect_link.return_value = link
        r = _prep(tmp_path, ex)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_selector_count_rejections(tmp_path):
    for count in (0, 2):
        ex = _ex()
        ex.inspect_link.return_value = _link(count=count)
        r = _prep(tmp_path, ex)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert "SELECTOR_COUNT" in r["reason"]


def test_non_link_missing_href_blocked_schemes_rejected(tmp_path):
    cases = [
        _link(tag_name="", role="", link_class=""),
        _link(href="", resolved=""),
        _link(href="javascript:alert(1)", resolved="javascript:alert(1)"),
        _link(href="data:text/plain,x", resolved="data:text/plain,x"),
        _link(href="file:///tmp/x", resolved="file:///tmp/x"),
        _link(href="mailto:x@y", resolved="mailto:x@y"),
        _link(href="tel:123", resolved="tel:123"),
    ]
    for link in cases:
        ex = _ex()
        ex.inspect_link.return_value = link
        assert _prep(tmp_path, ex)["status"] == PC2.PREPARE_REJECTED


def test_visibility_enabled_and_iframe_rejected(tmp_path):
    for link, reason in (
        (_link(visible=False), "ELEMENT_NOT_VISIBLE"),
        (_link(enabled=False), "ELEMENT_NOT_ENABLED"),
        ({**_link(), "main_frame": False}, "IFRAME_UNSUPPORTED"),
    ):
        ex = _ex()
        ex.inspect_link.return_value = link
        r = _prep(tmp_path, ex)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_relative_href_resolved_and_bound_into_eah(tmp_path):
    ex = _ex()
    r = _prep(tmp_path, ex)
    assert r["resolved_href"] == DEST_URL
    assert r["href"] == "/dest"
    assert r["execution_authority_hash"]
    assert r["element_identity"]["metadata_sha256"] == "meta-1"


def test_same_url_link_deferred(tmp_path):
    ex = _ex()
    ex.inspect_link.return_value = _link(url=DEST_URL, resolved=DEST_URL)
    r = _prep(tmp_path, ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "SAME_URL_LINK_DEFERRED" in r["reason"]


def test_execute_missing_approval_and_eah_mismatch_rejected(tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_activate_link_execute(
        prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex
    )["status"] == PC2.EXECUTE_REJECTED
    assert PC2.pc_v2_browser_activate_link_execute(
        prep, prep["execution_authority_hash"], "", stores_base_dir=tmp_path / "s", executor=ex
    )["status"] == PC2.EXECUTE_REJECTED


def test_execute_toctou_drifts_rejected(tmp_path):
    for link in (
        _link(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _link(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _link(url="https://example.com/other"),
        _link(href="/other", resolved="https://example.com/other"),
        _link(count=2),
        _link(visible=False),
        _link(enabled=False),
        _link(metadata="meta-2"),
    ):
        ex = _ex()
        prep = _prep(tmp_path, ex)
        ex.inspect_link.return_value = link
        r = PC2.pc_v2_browser_activate_link_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / "s", executor=ex,
        )
        assert r["status"] == PC2.EXECUTE_REJECTED
        ex.activate_link.assert_not_called()


def test_binder_and_kx_reject(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "FAILED"})
    r = PC2.pc_v2_browser_activate_link_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert "APPROVAL_STORE_FAILED" in r["reason"]

    ex = _ex()
    prep = _prep(tmp_path, ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    r = PC2.pc_v2_browser_activate_link_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert "KX108_PRE_GATE:BLOCK" in r["reason"]


def test_popup_new_page_download_reject(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    for flag, reason in (
        ("popup_detected", "UNEXPECTED_POPUP"),
        ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
        ("download_detected", "UNEXPECTED_DOWNLOAD"),
    ):
        ex = _ex()
        prep = _prep(tmp_path, ex)
        ex.activate_link.return_value = {"ok": True, flag: True}
        r = PC2.pc_v2_browser_activate_link_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / "s", executor=ex,
        )
        assert reason in r["reason"]


def test_success_strong_final_url_proof(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    ex = _ex()
    prep = _prep(tmp_path, ex)
    r = PC2.pc_v2_browser_activate_link_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "s", executor=ex,
    )
    assert r["status"] == PC2.EXECUTED_OK
    assert r["public_action"] == "BROWSER_ACTIVATE_LINK"
    assert r["post_url"] == DEST_URL
    assert r["page_id"] == PAGE_ID
    assert r["browser_session_id"] == SESSION_ID
    assert r["proof_strength"] == "STRONG"
    assert r["independent_post_read"] is True


def test_redirect_and_post_identity_mismatch_reject(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    for state, reason in (
        (_state(url="https://example.com/redirect"), PC2.REALIZED_STATE_MISMATCH),
        (_state(pid=""), "POST_PAGE_ID_MISSING"),
        (_state(sid=""), "POST_SESSION_ID_MISSING"),
        (_state(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"), "POST_PAGE_ID_DRIFT"),
        (_state(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"), "POST_SESSION_ID_DRIFT"),
    ):
        ex = _ex()
        prep = _prep(tmp_path, ex)
        ex.read_browser_state.return_value = state
        r = PC2.pc_v2_browser_activate_link_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / "s", executor=ex,
        )
        assert reason in r["reason"]


def test_graph_and_no_generic_surfaces():
    import obsidia_capability_graph_v0 as CG

    g = CG.graph_snapshot()["capabilities"]
    assert "PC_V2_BROWSER_ACTIVATE_LINK_PREPARE" in g
    assert "PC_V2_BROWSER_ACTIVATE_LINK_EXECUTE" in g
    assert g["PC_V2_BROWSER_ACTIVATE_LINK_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_link")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "activate_link")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")
