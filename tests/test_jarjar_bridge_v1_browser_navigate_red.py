from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import jarjar_browser_bridge_v0 as BBRIDGE

PRE_URL    = "https://example.com/start"
DEST_URL   = "https://example.com/dashboard"
SESSION_ID = "sess-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID    = "page-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _state(url=PRE_URL, sid=SESSION_ID, pid=PAGE_ID, closed=False, origin="https://example.com"):
    return {
        "ok": True, "url": url, "title": "Pre Page",
        "browser_session_id": sid, "page_id": pid,
        "origin": origin, "closed": closed,
    }


def _ex(*, pre_url=PRE_URL, post_url=DEST_URL, nav_ok=True, nav_url=None, status=200,
        sid=SESSION_ID, pid=PAGE_ID, closed=False):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "BrowserBackend"
    ex.read_browser_state.return_value = _state(pre_url, sid, pid, closed)
    ex.navigate.return_value = {
        "ok": nav_ok,
        "nav_url": nav_url or post_url,
        "nav_status": status,
        "nav_title": "Post Page",
        "executor": "BrowserBackend",
    }
    return ex


def _ex_post(ex, post_url, post_pid=PAGE_ID):
    ex.read_browser_state.side_effect = [
        _state(PRE_URL),
        _state(PRE_URL),
        _state(post_url, pid=post_pid),
    ]
    return ex


# registration

def test_bnav_prepare_is_registered():
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_NAVIGATE_PREPARE",
        requested_url=DEST_URL, stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"


def test_bnav_execute_is_registered():
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_NAVIGATE_EXECUTE",
        prepared_result=fake, human_authorized_eah="a" * 64,
        human_authorization_reference="REF", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"


# prepare

def test_prepare_reads_pre_url():
    ex = _ex()
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["pre_url"] == PRE_URL
    assert r["requested_url"] == DEST_URL
    ex.navigate.assert_not_called()


def test_prepare_no_navigation():
    ex = _ex()
    PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    ex.navigate.assert_not_called()


def test_prepare_without_executor_rejected():
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")


def test_prepare_empty_url_rejected():
    r = PC2.pc_v2_browser_navigate_prepare("  ", stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "REQUESTED_URL_REQUIRED" in r.get("reason", "")


def test_prepare_unknown_redirect_policy_rejected():
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, redirect_policy="ALLOW_ALL",
                                            stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "UNSUPPORTED_REDIRECT_POLICY" in r.get("reason", "")


def test_prepare_missing_browser_session_id_rejected():
    ex = _ex(sid="")
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_IDENTITY_MISSING" in r.get("reason", "")


def test_prepare_missing_page_id_rejected():
    ex = _ex(pid="")
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_IDENTITY_MISSING" in r.get("reason", "")


def test_prepare_closed_page_rejected():
    ex = _ex(closed=True)
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_CLOSED" in r.get("reason", "")


def test_prepare_captures_browser_session_id():
    ex = _ex()
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["browser_session_id"] == SESSION_ID


def test_prepare_captures_page_id():
    ex = _ex()
    r = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    assert r["page_id"] == PAGE_ID


def test_prepare_psa_v1_different_page_id():
    ex  = _ex()
    r   = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s", executor=ex)
    ex2 = _ex(pid="page-ccccccccccccccccccccccccccccccc")
    r2  = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir="/tmp/s2", executor=ex2)
    assert r["physical_state_anchor"] != r2["physical_state_anchor"]


def test_prepare_psa_same_for_different_dest():
    ex = _ex(pre_url="https://example.com/a")
    p1 = PC2.pc_v2_browser_navigate_prepare("https://example.com/x",
                                             stores_base_dir="/tmp/s1", executor=ex)
    p2 = PC2.pc_v2_browser_navigate_prepare("https://example.com/y",
                                             stores_base_dir="/tmp/s2", executor=ex)
    assert p1["physical_state_anchor"] == p2["physical_state_anchor"]
    assert p1["execution_authority_hash"] != p2["execution_authority_hash"]


# execute rejections

def test_execute_wrong_eah_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    r = PC2.pc_v2_browser_navigate_execute(prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    ex.navigate.assert_not_called()


def test_execute_missing_reference_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED


def test_execute_pre_state_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state("https://other.com/")
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")
    ex.navigate.assert_not_called()


def test_execute_page_id_drift_at_toctou_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(PRE_URL, pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")
    ex.navigate.assert_not_called()


def test_execute_session_drift_at_toctou_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(PRE_URL, sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")
    ex.navigate.assert_not_called()


def test_execute_closed_page_at_toctou_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(PRE_URL, closed=True)
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PAGE_CLOSED_AT_EXECUTE" in r.get("reason", "")
    ex.navigate.assert_not_called()


# golden paths

def test_navigate_success_strong_proof(tmp_path):
    ex = _ex_post(_ex(), DEST_URL)
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    assert prep["pre_url"] == PRE_URL
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N001", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["realized_state_verified"] is True
    assert r["independent_post_read"] is True
    assert r["post_url"] == DEST_URL
    assert r["mutation_performed"] is True
    ex.navigate.assert_called_once_with(DEST_URL)


def test_navigate_return_url_ignored_if_post_read_mismatches(tmp_path):
    ex = _ex_post(_ex(), "https://redirect.example.com/")
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N002", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")


def test_redirect_different_url_fail_closed(tmp_path):
    ex = _ex_post(_ex(), "https://login.example.com/sso")
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N003", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")


def test_post_navigate_page_id_drift_fail_closed(tmp_path):
    ex = _ex_post(_ex(), DEST_URL, post_pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N012", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_PAGE_ID_DRIFT" in r.get("reason", "")


def test_status_none_allowed_if_post_read_ok(tmp_path):
    ex = _ex(status=None)
    ex.read_browser_state.side_effect = [
        _state(PRE_URL),
        _state(PRE_URL),
        _state(DEST_URL),
    ]
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N004", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["nav_status"] is None


def test_navigate_exception_fail_closed(tmp_path):
    ex = _ex()
    ex.navigate.return_value = {"ok": False, "error": "NAVIGATE_FAILED:timeout"}
    ex.read_browser_state.return_value = _state(PRE_URL)
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N005", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "NAVIGATE_FAILED" in r.get("reason", "")


def test_post_read_exception_fail_closed(tmp_path):
    ex = _ex()
    ex.read_browser_state.side_effect = [
        _state(PRE_URL),
        _state(PRE_URL),
        {"ok": False, "error": "READ_BROWSER_STATE_FAILED:crash"},
    ]
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N006", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_READ_FAILED" in r.get("reason", "")


# no-op path

def test_noop_already_on_target_url(tmp_path):
    ex = _ex(pre_url=DEST_URL)
    ex.read_browser_state.side_effect = [
        _state(DEST_URL),
        _state(DEST_URL),
        _state(DEST_URL),
    ]
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N007", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["mutation_performed"] is False
    assert r["realized_state_verified"] is True
    ex.navigate.assert_not_called()


def test_noop_post_read_mismatch_fail_closed(tmp_path):
    ex = _ex(pre_url=DEST_URL)
    ex.read_browser_state.side_effect = [
        _state(DEST_URL),
        _state(DEST_URL),
        _state("https://other.com/"),
    ]
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N008", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")


def test_noop_preserves_page_id(tmp_path):
    ex = _ex(pre_url=DEST_URL)
    ex.read_browser_state.side_effect = [
        _state(DEST_URL),
        _state(DEST_URL),
        _state(DEST_URL, pid=PAGE_ID),
    ]
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N013", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["mutation_performed"] is False


# URL normalization

def test_canon_strips_default_https_port(tmp_path):
    ex = _ex_post(_ex(), "https://example.com/dashboard")
    prep = PC2.pc_v2_browser_navigate_prepare("https://example.com:443/dashboard",
                                               stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N009", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK


def test_canon_strips_default_http_port(tmp_path):
    ex = _ex_post(_ex(), "http://example.com/path")
    prep = PC2.pc_v2_browser_navigate_prepare("http://example.com:80/path",
                                               stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N010", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK


def test_canon_different_path_still_mismatch(tmp_path):
    ex = _ex_post(_ex(), "https://example.com/other")
    prep = PC2.pc_v2_browser_navigate_prepare(DEST_URL, stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_navigate_execute(prep, eah, "REF-N011", stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "REALIZED_STATE_MISMATCH" in r.get("reason", "")


# graph + security

def test_bnav_caps_in_graph():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert "PC_V2_BROWSER_NAVIGATE_PREPARE" in g
    assert "PC_V2_BROWSER_NAVIGATE_EXECUTE" in g


def test_bnav_authority_class():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_NAVIGATE_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_NAVIGATE_EXECUTE"]["authority_class"] == "KX108_ONLY"


def test_no_browser_click_capability():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK", url=DEST_URL)
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"


def test_no_browser_fill_capability():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL", url=DEST_URL)
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"


def test_no_js_execute_capability():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS", script="alert(1)")
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"


def test_bridge_has_read_browser_state():
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "read_browser_state")


def test_bridge_has_navigate():
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "navigate")


def test_bridge_has_no_click():
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")


def test_bridge_has_no_fill():
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
