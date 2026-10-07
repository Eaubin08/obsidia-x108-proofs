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


def _opt(value, label, text=None, index=0, disabled=False, match_kind=None, match_value=None):
    out = {
        "option_value": value,
        "option_label": label,
        "option_text": text if text is not None else label,
        "option_index": index,
        "option_disabled": disabled,
    }
    if match_kind is not None:
        out.update({"match_kind": match_kind, "match_value": match_value, "match_count": 1})
    return out


def _options(extra=None):
    base = [_opt("basic", "Basic", index=0), _opt("pro", "Pro", index=1)]
    return base + list(extra or [])


def _select(
    *,
    selected=None,
    selector="select#plan",
    sid=SESSION_ID,
    pid=PAGE_ID,
    url=URL,
    origin="https://example.com",
    count=1,
    tag="select",
    multiple=False,
    visible=True,
    enabled=True,
    closed=False,
    metadata="meta-1",
    main_frame=True,
    options=None,
):
    opts = options if options is not None else _options()
    selected = selected or opts[0]
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": origin,
        "select_selector": selector,
        "select_count": count,
        "tag_name": tag,
        "role": "",
        "name": "plan",
        "id": "plan",
        "form_owner": "f1",
        "multiple": multiple,
        "current_value": selected.get("option_value"),
        "current_selected_option": selected,
        "options": opts,
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
    pre = pre or _select()
    target = _opt("pro", "Pro", index=1)
    post = post or _select(selected=target)
    ex.inspect_select.side_effect = [pre, pre, pre, post, post]
    ex.select_option.return_value = act or {
        "ok": True,
        "mutation_performed": pre["current_selected_option"].get("option_value") != "pro",
        "current_selected_option": target,
        "target_option_identity": _opt("pro", "Pro", index=1, match_kind="value", match_value="pro"),
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None, intent="choose_plan", risk="MEDIUM", **target):
    ex = ex or _ex()
    if not target:
        target = {"option_value": "pro"}
    return PC2.pc_v2_browser_select_option_prepare(
        "select#plan", intent, risk, stores_base_dir=tmp_path / "s", executor=ex, **target)


def test_registration_graph_and_boundaries(tmp_path):
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_SELECT_OPTION_PREPARE",
        select_selector="select#plan", option_value="pro",
        semantic_intent="intent", semantic_risk="LOW", stores_base_dir=tmp_path / "s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_SELECT_OPTION_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_SELECT_OPTION_EXECUTE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SELECT")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SUBMIT")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_select")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "select_option")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "click")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")


def test_prepare_success_noop_and_semantic_binding(tmp_path):
    ex = _ex(pre=_select(), post=_select())
    r = _prep(tmp_path, ex, intent="billing_plan", risk="HIGH", option_value="pro")
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert r["public_action"] == "BROWSER_SELECT_OPTION"
    assert r["target_option_identity"]["option_value"] == "pro"
    assert r["target_option_identity"]["match_kind"] == "value"
    assert r["semantic_intent"] == "billing_plan"
    assert r["semantic_risk"] == "HIGH"
    ex.select_option.assert_not_called()


def test_prepare_rejections(tmp_path):
    duplicate_value = _options([_opt("dup", "A", index=2), _opt("dup", "B", index=3)])
    duplicate_label = _options([_opt("x", "Same", index=2), _opt("y", "Same", index=3)])
    cases = [
        (_select(sid=""), {"option_value": "pro"}, "PAGE_IDENTITY_MISSING"),
        (_select(pid=""), {"option_value": "pro"}, "PAGE_IDENTITY_MISSING"),
        (_select(closed=True), {"option_value": "pro"}, "PAGE_CLOSED"),
        (_select(count=0), {"option_value": "pro"}, "SELECTOR_COUNT"),
        (_select(count=2), {"option_value": "pro"}, "SELECTOR_COUNT"),
        (_select(tag="input"), {"option_value": "pro"}, "UNSUPPORTED_SELECT_TARGET"),
        (_select(multiple=True), {"option_value": "pro"}, "UNSUPPORTED_MULTI_SELECT_V0"),
        (_select(visible=False), {"option_value": "pro"}, "ELEMENT_NOT_VISIBLE"),
        (_select(enabled=False), {"option_value": "pro"}, "ELEMENT_NOT_ENABLED"),
        (_select(main_frame=False), {"option_value": "pro"}, "IFRAME_UNSUPPORTED"),
        (_select(options=duplicate_value), {"option_value": "dup"}, "DUPLICATE_OPTION_VALUE"),
        (_select(options=duplicate_label), {"option_label": "Same"}, "DUPLICATE_OPTION_LABEL"),
        (_select(options=_options([_opt("d", "Disabled", index=2, disabled=True)])), {"option_value": "d"}, "OPTION_DISABLED"),
    ]
    for i, (pre, target, reason) in enumerate(cases):
        ex = _ex(pre=pre, post=pre)
        r = _prep(tmp_path / f"s{i}", ex, **target)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]


def test_prepare_target_and_semantic_rejections(tmp_path):
    cases = [
        ({"option_value": "pro", "option_label": "Pro"}, "EXACTLY_ONE_OPTION_IDENTITY_MODE_REQUIRED"),
        ({"option_value": "missing"}, "OPTION_TARGET_NOT_FOUND"),
    ]
    r = PC2.pc_v2_browser_select_option_prepare(
        "select#plan", "choose_plan", "MEDIUM", stores_base_dir=tmp_path / "missing" / "s", executor=_ex())
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXACTLY_ONE_OPTION_IDENTITY_MODE_REQUIRED" in r["reason"]
    for target, reason in cases:
        r = _prep(tmp_path / reason, _ex(), **target)
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]
    assert "SEMANTIC_INTENT_REQUIRED" in _prep(tmp_path / "intent", _ex(), intent="", option_value="pro")["reason"]
    assert "SEMANTIC_RISK_INVALID" in _prep(tmp_path / "risk", _ex(), risk="CRITICAL", option_value="pro")["reason"]


def test_execute_eah_approval_binder_kx_reject(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_select_option_execute(
        prep, "x" * 64, "REF", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert "DESCRIPTOR_EAH_MISMATCH" in PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "other", executor=ex)["reason"]
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "FAILED"})
    assert "APPROVAL_STORE_FAILED" in PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "s", executor=ex)["reason"]
    ex = _ex()
    prep = _prep(tmp_path / "kx", ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    assert "KX108_PRE_GATE:BLOCK" in PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "REF", stores_base_dir=tmp_path / "kx" / "s", executor=ex)["reason"]


def test_toctou_and_side_effect_rejections(tmp_path):
    drifts = [
        _select(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _select(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _select(url="https://example.com/other"),
        _select(origin="https://other.example.com"),
        _select(metadata="meta-2"),
        _select(selected=_opt("pro", "Pro", index=1)),
    ]
    for i, drift in enumerate(drifts):
        ex = _ex()
        prep = _prep(tmp_path / f"d{i}", ex)
        ex.inspect_select.side_effect = [drift]
        r = PC2.pc_v2_browser_select_option_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"d{i}" / "s", executor=ex)
        assert r["status"] == PC2.EXECUTE_REJECTED
        ex.select_option.assert_not_called()

    ex = _ex()
    prep = _prep(tmp_path / "dup", ex)
    ex.inspect_select.side_effect = [
        _select(options=_options([_opt("pro", "Pro duplicate", index=2)])),
    ]
    r = PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "dup" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTE_REJECTED
    assert "DUPLICATE_OPTION_VALUE" in r["reason"]
    ex.select_option.assert_not_called()


def test_success_noop_side_effect_and_post_rejections(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    ex = _ex(pre=_select(), post=_select(selected=_opt("pro", "Pro", index=1)))
    prep = _prep(tmp_path / "ok", ex)
    r = PC2.pc_v2_browser_select_option_execute(
        prep, prep["execution_authority_hash"], "REF",
        stores_base_dir=tmp_path / "ok" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["mutation_performed"] is True
    assert r["realized_state_verified"] is True

    selected = _opt("pro", "Pro", index=1)
    ex = _ex(pre=_select(selected=selected), post=_select(selected=selected),
             act={"ok": True, "mutation_performed": False})
    prep = _prep(tmp_path / "noop", ex)
    r = PC2.pc_v2_browser_select_option_execute(
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
        r = PC2.pc_v2_browser_select_option_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / flag / "s", executor=ex)
        assert reason in r["reason"]

    for i, (post, reason) in enumerate((
        (_select(sid="", selected=_opt("pro", "Pro", index=1)), "POST_SESSION_ID_MISSING"),
        (_select(pid="", selected=_opt("pro", "Pro", index=1)), "POST_PAGE_ID_MISSING"),
        (_select(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", selected=_opt("pro", "Pro", index=1)), "POST_SESSION_ID_DRIFT"),
        (_select(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", selected=_opt("pro", "Pro", index=1)), "POST_PAGE_ID_DRIFT"),
        (_select(metadata="meta-2", selected=_opt("pro", "Pro", index=1)), "POST_SELECT_IDENTITY_DRIFT"),
        (_select(selected=_opt("basic", "Basic", index=0)), PC2.REALIZED_STATE_MISMATCH),
    )):
        ex = _ex(pre=_select(), post=post)
        prep = _prep(tmp_path / f"p{i}", ex)
        r = PC2.pc_v2_browser_select_option_execute(
            prep, prep["execution_authority_hash"], "REF",
            stores_base_dir=tmp_path / f"p{i}" / "s", executor=ex)
        assert reason in r["reason"]
