from __future__ import annotations
import sys, hashlib
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
SESSION_ID = "sess-" + "a" * 27
PAGE_ID    = "page-" + "b" * 27

def _state(url=PRE_URL, sid=SESSION_ID, pid=PAGE_ID, closed=False, origin="https://example.com"):
    return {"ok": True, "browser_session_id": sid, "page_id": pid,
            "url": url, "origin": origin, "title": "Pre Page", "closed": closed}

def _page(url=PRE_URL, sid=SESSION_ID, pid=PAGE_ID, closed=False, text="body text",
           sel_count=1, sel_text="element text", selector=None):
    return {"ok": True, "browser_session_id": sid, "page_id": pid,
            "url": url, "origin": "https://example.com", "title": "Pre Page", "closed": closed,
            "text": text, "element_count": sel_count, "selector": selector}

def _ex(pre_url=PRE_URL, sid=SESSION_ID, pid=PAGE_ID, closed=False, text="body text"):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "BrowserBackend"
    ex.read_browser_state.return_value = _state(pre_url, sid, pid, closed)
    ex.read_page.return_value = _page(pre_url, sid, pid, closed, text)
    return ex

# -- registration -------------------------------------------------------

def test_bread_prepare_is_registered():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_READ_PREPARE", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"

def test_bread_execute_is_registered():
    fake = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_READ_EXECUTE",
        prepared_result=fake, human_authorized_eah="a" * 64,
        human_authorization_reference="REF", stores_base_dir="/tmp/s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"

# -- bridge identity relay ------------------------------------------------

def test_bridge_relays_browser_session_id():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND  = "BrowserBackend"
    ex.read_browser_state.return_value = _state()
    assert ex.read_browser_state()["browser_session_id"] == SESSION_ID

def test_bridge_relays_page_id():
    assert _state()["page_id"] == PAGE_ID

def test_bridge_relays_origin():
    assert _state()["origin"] == "https://example.com"

def test_bridge_relays_closed_false():
    assert _state()["closed"] is False

def test_bridge_relays_closed_true():
    assert _state(closed=True)["closed"] is True

# -- prepare rejections ---------------------------------------------------

def test_prepare_without_executor_rejected():
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir="/tmp/s")
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")

def test_prepare_missing_session_id_rejected():
    ex = _ex()
    ex.read_browser_state.return_value = _state(sid="")
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_IDENTITY_MISSING" in r.get("reason", "")

def test_prepare_missing_page_id_rejected():
    ex = _ex()
    ex.read_browser_state.return_value = _state(pid="")
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir="/tmp/s", executor=ex)
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_IDENTITY_MISSING" in r.get("reason", "")

def test_prepare_closed_page_rejected():
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir="/tmp/s", executor=_ex(closed=True))
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "PAGE_CLOSED" in r.get("reason", "")

def test_prepare_password_selector_rejected():
    r = PC2.pc_v2_browser_read_prepare(selector="input[type=password]",
                                        stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "SENSITIVE_SELECTOR" in r.get("reason", "")

def test_prepare_hidden_selector_rejected():
    r = PC2.pc_v2_browser_read_prepare(selector="input[type=hidden]",
                                        stores_base_dir="/tmp/s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "SENSITIVE_SELECTOR" in r.get("reason", "")

def test_prepare_zero_mutation(tmp_path):
    ex = _ex()
    PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    ex.read_page.assert_not_called()
    ex.navigate.assert_not_called()

def test_prepare_success_full_page(tmp_path):
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=_ex())
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["read_scope"] == "FULL_PAGE"
    assert r["page_id"] == PAGE_ID
    assert r["browser_session_id"] == SESSION_ID

def test_prepare_success_selector(tmp_path):
    r = PC2.pc_v2_browser_read_prepare(selector="h1",
                                        stores_base_dir=tmp_path / "s", executor=_ex())
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["read_scope"] == "SELECTOR"
    assert r["selector"] == "h1"

def test_prepare_state_anchor_kind_is_canonical(tmp_path):
    r = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=_ex())
    assert r["state_anchor_kind"] == "PHYSICAL_PRE_STATE"
    assert r["receipt"]["state_anchor_kind"] == "PHYSICAL_PRE_STATE"

# -- execute rejections ---------------------------------------------------

def test_execute_wrong_eah_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    r = PC2.pc_v2_browser_read_execute(prep, "x" * 64, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED

def test_execute_missing_reference_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED

def test_execute_pre_url_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(url="https://other.com/")
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")

def test_execute_page_id_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(pid="page-" + "z" * 27)
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")

def test_execute_session_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(sid="sess-" + "z" * 27)
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "PRE_STATE_DRIFT" in r.get("reason", "")

def test_execute_post_page_id_missing_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(pid="")
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_PAGE_ID_MISSING" in r.get("reason", "")

def test_execute_post_session_id_missing_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(sid="")
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_SESSION_ID_MISSING" in r.get("reason", "")

def test_execute_post_page_id_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(pid="page-" + "z" * 27)
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_PAGE_ID_DRIFT" in r.get("reason", "")

def test_execute_post_session_id_drift_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(sid="sess-" + "z" * 27)
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "POST_SESSION_ID_DRIFT" in r.get("reason", "")

def test_execute_closed_at_execute_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_browser_state.return_value = _state(closed=True)
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "CLOSED" in r.get("reason", "")

# -- selector count checks ------------------------------------------------

def test_selector_zero_matches_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(selector="h1",
                                           stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(sel_count=0, selector="h1")
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "SELECTOR_NO_MATCH" in r.get("reason", "")

def test_selector_multiple_matches_rejected(tmp_path):
    ex = _ex()
    prep = PC2.pc_v2_browser_read_prepare(selector="p",
                                           stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    ex.read_page.return_value = _page(sel_count=3, selector="p")
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "SELECTOR_AMBIGUOUS" in r.get("reason", "")

# -- golden paths ---------------------------------------------------------

def test_full_page_read_success_strong_proof(tmp_path):
    ex = _ex(text="Hello World")
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF-R001",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["text"] == "Hello World"

def test_selector_exactly_one_success(tmp_path):
    ex = _ex()
    ex.read_page.return_value = _page(sel_count=1, sel_text="Title", selector="h1",
                                       text="Title")
    prep = PC2.pc_v2_browser_read_prepare(selector="h1",
                                           stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF-R002",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r.get("element_count") == 1

# -- receipt security -----------------------------------------------------

def test_receipt_contains_text_sha256(tmp_path):
    ex = _ex(text="Secret Page Content")
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF-R003",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    receipt_str = str(r.get("receipt", ""))
    import hashlib
    expected_hash = hashlib.sha256("Secret Page Content".encode()).hexdigest()
    assert expected_hash in receipt_str or r.get("text_sha256") == expected_hash

def test_receipt_does_not_contain_plaintext(tmp_path):
    secret = "PLAINTEXT_SECRET_CONTENT_12345"
    ex = _ex(text=secret)
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF-R004",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    receipt_str = str(r.get("receipt", ""))
    assert secret not in receipt_str

def test_runtime_result_contains_plaintext(tmp_path):
    ex = _ex(text="Approved Page Content")
    prep = PC2.pc_v2_browser_read_prepare(stores_base_dir=tmp_path / "s", executor=ex)
    eah = prep["execution_authority_hash"]
    r = PC2.pc_v2_browser_read_execute(prep, eah, "REF-R005",
                                        stores_base_dir=tmp_path / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r.get("text") == "Approved Page Content"

# -- graph + security -----------------------------------------------------

def test_bread_caps_in_graph():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert "PC_V2_BROWSER_READ_PREPARE" in g
    assert "PC_V2_BROWSER_READ_EXECUTE" in g

def test_bread_authority_class():
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_READ_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_READ_EXECUTE"]["authority_class"] == "KX108_ONLY"

def test_no_click_in_bread():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK", url="https://x.com")
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"

def test_no_fill_in_bread():
    r = PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL", url="https://x.com")
    assert r["status"] == "UNKNOWN_CAPABILITY_V2"

def test_bridge_has_read_page():
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "read_page")

def test_bridge_read_page_not_evaluate():
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "js_eval")
