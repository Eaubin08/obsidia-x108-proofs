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

URL = "https://example.com/page"
SESSION_ID = "sess-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
PAGE_ID = "page-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
OLD_HASH = PC2._sha256_text("old")
NEW_HASH = PC2._sha256_text("new")


def _field(
    *,
    selector="input#contact",
    sid=SESSION_ID,
    pid=PAGE_ID,
    url=URL,
    origin="https://example.com",
    closed=False,
    count=1,
    tag="input",
    typ="text",
    klass="INPUT_TEXT",
    visible=True,
    enabled=True,
    editable=True,
    readonly=False,
    autocomplete="",
    value_hash=OLD_HASH,
    value_length=3,
    metadata="meta-1",
    main_frame=True,
):
    return {
        "ok": True,
        "browser_session_id": sid,
        "page_id": pid,
        "url": url,
        "origin": origin,
        "closed": closed,
        "selector": selector,
        "element_count": count,
        "tag_name": tag,
        "type": typ,
        "name": "contact",
        "id": "contact",
        "role": "",
        "autocomplete": autocomplete,
        "form_owner": "f1",
        "visible": visible,
        "enabled": enabled,
        "editable": editable,
        "readonly": readonly,
        "supported_field_class": klass,
        "current_value_sha256": value_hash,
        "current_value_length": value_length,
        "metadata_sha256": metadata,
        "main_frame": main_frame,
    }


def _ex(pre=None, post=None, act=None):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "BrowserBackend"
    pre = pre or _field()
    post = post or _field(value_hash=NEW_HASH, value_length=3)
    ex.inspect_field.side_effect = [pre, pre, post, post, post]
    ex.set_field_value.return_value = act or {
        "ok": True,
        "mutation_performed": pre["current_value_sha256"] != NEW_HASH,
        "target_value_sha256": NEW_HASH,
        "post_value_sha256": NEW_HASH,
        "target_value_length": 3,
        "post_value_length": 3,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
    }
    return ex


def _allow_gates(monkeypatch):
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "ALLOW"})


def _prep(tmp_path, ex=None, target="new", intent="set_contact", risk="MEDIUM"):
    return PC2.pc_v2_browser_set_field_value_prepare(
        "input#contact", target, intent, risk, stores_base_dir=tmp_path / "s", executor=ex or _ex())


def _stored_descriptor(tmp_path, prep):
    path = tmp_path / "s" / "v2exec" / f"{prep['v2_exec_id']}.json"
    return json.loads(path.read_text(encoding="utf-8"))["descriptor"]


def test_registration_graph_and_boundaries(tmp_path):
    r = PC2.execute_pc_capability_v2(
        "PC_V2_BROWSER_SET_FIELD_VALUE_PREPARE",
        selector="input#contact", target_value="new",
        semantic_intent="intent", semantic_risk="LOW", stores_base_dir=tmp_path / "s")
    assert r["status"] != "UNKNOWN_CAPABILITY_V2"
    import obsidia_capability_graph_v0 as CG
    g = CG.graph_snapshot()["capabilities"]
    assert g["PC_V2_BROWSER_SET_FIELD_VALUE_PREPARE"]["authority_class"] == "KX108_ONLY"
    assert g["PC_V2_BROWSER_SET_FIELD_VALUE_EXECUTE"]["authority_class"] == "KX108_ONLY"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_FILL")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_CLICK")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_SUBMIT")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert PC2.execute_pc_capability_v2("PC_V2_BROWSER_EXECUTE_JS")["status"] == "UNKNOWN_CAPABILITY_V2"
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "inspect_field")
    assert hasattr(BBRIDGE.JarJarBrowserExecutor, "set_field_value")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "fill")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "submit")
    assert not hasattr(BBRIDGE.JarJarBrowserExecutor, "evaluate")


def test_prepare_supported_types_privacy_and_hash_binding(tmp_path):
    cases = [
        ("input", "text", "INPUT_TEXT"),
        ("input", "search", "INPUT_SEARCH"),
        ("input", "email", "INPUT_EMAIL"),
        ("input", "url", "INPUT_URL"),
        ("input", "tel", "INPUT_TEL"),
        ("textarea", "", "TEXTAREA"),
    ]
    for tag, typ, klass in cases:
        secret = "plain-secret-42"
        secret_hash = PC2._sha256_text(secret)
        ex = _ex(pre=_field(tag=tag, typ=typ, klass=klass))
        r = _prep(tmp_path / klass, ex, target=secret, intent="profile", risk="HIGH")
        assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
        assert r["public_action"] == "BROWSER_SET_FIELD_VALUE"
        assert r["target_value_sha256"] == secret_hash
        assert r["target_value_length"] == len(secret)
        blob = json.dumps(r, sort_keys=True)
        desc_blob = json.dumps(_stored_descriptor(tmp_path / klass, r), sort_keys=True)
        assert secret not in blob
        assert secret not in desc_blob
        assert "target_value" not in _stored_descriptor(tmp_path / klass, r)
        ex.set_field_value.assert_not_called()


def test_prepare_rejections(tmp_path):
    cases = [
        (_field(sid=""), "SESSION_ID_MISSING"),
        (_field(pid=""), "PAGE_ID_MISSING"),
        (_field(closed=True), "PAGE_CLOSED"),
        (_field(count=0), "FIELD_COUNT_NOT_ONE"),
        (_field(count=2), "FIELD_COUNT_NOT_ONE"),
        (_field(typ="password", klass="DEFERRED"), "PASSWORD_FIELD_DEFERRED"),
        (_field(typ="file", klass="BLOCKED"), "FILE_FIELD_BLOCKED"),
        (_field(typ="hidden", klass="BLOCKED"), "HIDDEN_FIELD_BLOCKED"),
        (_field(typ="number", klass="DEFERRED"), "FIELD_TYPE_DEFERRED"),
        (_field(typ="date", klass="DEFERRED"), "FIELD_TYPE_DEFERRED"),
        (_field(typ="time", klass="DEFERRED"), "FIELD_TYPE_DEFERRED"),
        (_field(typ="datetime-local", klass="DEFERRED"), "FIELD_TYPE_DEFERRED"),
        (_field(tag="div", typ="", klass="UNSUPPORTED"), "UNSUPPORTED_FIELD_TARGET"),
        (_field(visible=False), "ELEMENT_NOT_VISIBLE"),
        (_field(enabled=False), "ELEMENT_NOT_ENABLED"),
        (_field(editable=False), "ELEMENT_NOT_EDITABLE"),
        (_field(readonly=True), "ELEMENT_READONLY"),
        (_field(main_frame=False), "IFRAME_UNSUPPORTED"),
        (_field(autocomplete="current-password"), "SENSITIVE_AUTOCOMPLETE_DEFERRED"),
        (_field(autocomplete="one-time-code"), "SENSITIVE_AUTOCOMPLETE_DEFERRED"),
        (_field(autocomplete="cc-number"), "SENSITIVE_AUTOCOMPLETE_DEFERRED"),
    ]
    for i, (pre, reason) in enumerate(cases):
        r = _prep(tmp_path / f"r{i}", _ex(pre=pre, post=pre))
        assert r["status"] == PC2.PREPARE_REJECTED
        assert reason in r["reason"]
    assert "SEMANTIC_INTENT_REQUIRED" in _prep(tmp_path / "intent", _ex(), intent="")["reason"]
    assert "SEMANTIC_RISK_INVALID" in _prep(tmp_path / "risk", _ex(), risk="CRITICAL")["reason"]
    assert "TARGET_VALUE_STRING_REQUIRED" in PC2.pc_v2_browser_set_field_value_prepare(
        "input#contact", 123, "intent", "LOW", stores_base_dir=tmp_path / "type" / "s", executor=_ex())["reason"]
    assert "TARGET_VALUE_TOO_LONG" in _prep(tmp_path / "long", _ex(), target="x" * 4097)["reason"]


def test_execute_value_handoff_eah_approval_and_kx(monkeypatch, tmp_path):
    ex = _ex()
    prep = _prep(tmp_path, ex)
    assert PC2.pc_v2_browser_set_field_value_execute(
        prep, "x" * 64, "REF", "new", stores_base_dir=tmp_path / "s", executor=ex)["status"] == PC2.EXECUTE_REJECTED
    assert "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED" in PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "", "new", stores_base_dir=tmp_path / "s", executor=ex)["reason"]
    assert "TARGET_VALUE_HASH_MISMATCH" in PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", "wrong", stores_base_dir=tmp_path / "s", executor=ex)["reason"]
    assert "DESCRIPTOR_EAH_MISMATCH" in PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", "new", stores_base_dir=tmp_path / "other", executor=ex)["reason"]
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "FAILED"})
    assert "APPROVAL_STORE_FAILED" in PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", "new", stores_base_dir=tmp_path / "s", executor=ex)["reason"]
    ex = _ex()
    prep = _prep(tmp_path / "kx", ex)
    monkeypatch.setattr(PC2._E, "store_approval_artifact", lambda *_a, **_k: {"status": "STORED"})
    monkeypatch.setattr(PC2, "_kx108_pre", lambda *_a, **_k: {"verify_ok": True, "x108_gate": "BLOCK"})
    assert "KX108_PRE_GATE:BLOCK" in PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", "new", stores_base_dir=tmp_path / "kx" / "s", executor=ex)["reason"]


def test_toctou_drifts_reject_before_mutation(tmp_path):
    drifts = [
        _field(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _field(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"),
        _field(url="https://example.com/other"),
        _field(origin="https://other.example.com"),
        _field(metadata="meta-2"),
        _field(value_hash=NEW_HASH),
        _field(value_length=9),
        _field(editable=False),
    ]
    for i, drift in enumerate(drifts):
        ex = _ex()
        prep = _prep(tmp_path / f"d{i}", ex)
        ex.inspect_field.side_effect = [drift]
        r = PC2.pc_v2_browser_set_field_value_execute(
            prep, prep["execution_authority_hash"], "REF", "new",
            stores_base_dir=tmp_path / f"d{i}" / "s", executor=ex)
        assert r["status"] == PC2.EXECUTE_REJECTED
        ex.set_field_value.assert_not_called()


def test_success_noop_side_effect_post_and_runtime_privacy(monkeypatch, tmp_path):
    _allow_gates(monkeypatch)
    secret = "plain-secret-42"
    secret_hash = PC2._sha256_text(secret)
    ex = _ex(post=_field(value_hash=secret_hash, value_length=len(secret)))
    prep = _prep(tmp_path / "ok", ex, target=secret)
    r = PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", secret,
        stores_base_dir=tmp_path / "ok" / "s", executor=ex)
    assert r["status"] == PC2.EXECUTED_OK
    assert r["proof_strength"] == "STRONG"
    assert r["mutation_performed"] is True
    assert r["plaintext_value_returned"] is False
    assert secret not in json.dumps(r, sort_keys=True)

    ex = _ex(pre=_field(value_hash=NEW_HASH, value_length=3),
             post=_field(value_hash=NEW_HASH, value_length=3),
             act={"ok": True, "mutation_performed": False})
    prep = _prep(tmp_path / "noop", ex)
    r = PC2.pc_v2_browser_set_field_value_execute(
        prep, prep["execution_authority_hash"], "REF", "new",
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
        r = PC2.pc_v2_browser_set_field_value_execute(
            prep, prep["execution_authority_hash"], "REF", "new",
            stores_base_dir=tmp_path / flag / "s", executor=ex)
        assert reason in r["reason"]

    for i, (post, reason) in enumerate((
        (_field(sid="", value_hash=NEW_HASH, value_length=3), "POST_SESSION_ID_MISSING"),
        (_field(pid="", value_hash=NEW_HASH, value_length=3), "POST_PAGE_ID_MISSING"),
        (_field(sid="sess-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", value_hash=NEW_HASH, value_length=3), "POST_SESSION_ID_DRIFT"),
        (_field(pid="page-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", value_hash=NEW_HASH, value_length=3), "POST_PAGE_ID_DRIFT"),
        (_field(metadata="meta-2", value_hash=NEW_HASH, value_length=3), "POST_FIELD_IDENTITY_DRIFT"),
        (_field(value_hash=OLD_HASH, value_length=3), PC2.REALIZED_STATE_MISMATCH),
        (_field(value_hash=NEW_HASH, value_length=4), "REALIZED_STATE_LENGTH_MISMATCH"),
    )):
        ex = _ex(pre=_field(), post=post)
        prep = _prep(tmp_path / f"p{i}", ex)
        r = PC2.pc_v2_browser_set_field_value_execute(
            prep, prep["execution_authority_hash"], "REF", "new",
            stores_base_dir=tmp_path / f"p{i}" / "s", executor=ex)
        assert reason in r["reason"]
