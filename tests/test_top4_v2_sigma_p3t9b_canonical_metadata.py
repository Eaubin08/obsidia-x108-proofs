"""
TOP4 V2 — P3T9B canonical metadata hardening
SCOPE=V2_ONLY  PATCH=YES_BUT_V2_ONLY  COMMIT=NO  DECISION_AUTHORITY=KX108_ONLY
"""
import sys
import importlib.util
import types

import pytest


def _load_run_pipeline():
    """Import sigma.run_pipeline via spec — stubs out heavy sigma infra."""
    import os, dataclasses
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "sigma", "run_pipeline.py")

    # sigma.contracts — needs dataclass-like classes
    stub_contracts = types.ModuleType("sigma.contracts")
    for _cls_name in ["TradingState", "BankState", "EcomState", "GpsDefenseAviationState"]:
        _cls = dataclasses.make_dataclass(_cls_name, [])
        setattr(stub_contracts, _cls_name, _cls)
    sys.modules["sigma.contracts"] = stub_contracts

    # sigma.protocols — needs pipeline runner functions
    stub_protocols = types.ModuleType("sigma.protocols")
    for _fn_name in [
        "run_trading_pipeline", "run_bank_pipeline",
        "run_ecom_pipeline", "run_gps_defense_aviation_pipeline",
    ]:
        setattr(stub_protocols, _fn_name, lambda *a, **k: dataclasses.make_dataclass("R", [])())
    sys.modules["sigma.protocols"] = stub_protocols

    # sigma.obsidia_sigma_v130 — needs ObsidiaSigmaMonitor
    stub_sigma130 = types.ModuleType("sigma.obsidia_sigma_v130")
    class _FakeSigmaMonitor:
        def __init__(self, *a, **k): pass
        def evaluate_step(self, *a, **k): return {}
        def export_to_proofkit(self): return {"V18_9_sigma_stability": {"status": "PASS"}}
    stub_sigma130.ObsidiaSigmaMonitor = _FakeSigmaMonitor
    sys.modules["sigma.obsidia_sigma_v130"] = stub_sigma130

    # Remaining sigma sub-modules (safe stubs)
    for _mod in ["sigma.guard", "sigma.aggregation", "sigma.base",
                 "sigma.evaluate", "sigma.packets", "sigma.registry"]:
        sys.modules[_mod] = types.ModuleType(_mod)

    # Also make sure "sigma" top-level is present
    if "sigma" not in sys.modules:
        sys.modules["sigma"] = types.ModuleType("sigma")

    spec = importlib.util.spec_from_file_location("sigma.run_pipeline_v2_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rp():
    return _load_run_pipeline()


# ── T1 : caller meta irreversible=True + no trusted source → HOLD ─────────────

def test_caller_irreversible_true_no_trusted_source_is_hold(rp):
    rd = {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW"}
    caller = {"irreversible": True, "action_type": "trade", "intent": "trade_execution_review"}
    result = rp._apply_p3t9b_rule(rd, caller, tuple(caller.keys()))
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_trusted_metadata_available"] is False
    assert result["p3t9b_caller_metadata_ignored"] is True
    assert result["p3t9b_demoted_for_missing_trusted_metadata"] is True
    assert result["p3t9b_reason_code"] == "P3T9B_TRUSTED_METADATA_REQUIRED"


# ── T2 : caller sets irreversible=False to bypass — still HOLD ────────────────

def test_caller_irreversible_false_cannot_bypass(rp):
    rd = {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW"}
    caller = {"irreversible": False, "action_type": "trade", "intent": "trade_execution_review"}
    result = rp._apply_p3t9b_rule(rd, caller, tuple(caller.keys()))
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_demoted_for_missing_trusted_metadata"] is True


# ── T3 : caller sets benign intent — still HOLD (no trusted source) ───────────

def test_caller_benign_intent_still_hold_no_trusted(rp):
    rd = {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW"}
    caller = {"irreversible": True, "action_type": "query", "intent": "read_only_report"}
    result = rp._apply_p3t9b_rule(rd, caller, tuple(caller.keys()))
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_caller_metadata_ignored"] is True


# ── T4 : trusted source present + irreversible=True + correct meta → HOLD ─────

def test_trusted_source_irreversible_true_hold(rp):
    rd = {
        "domain": "trading",
        "x108_gate": "ALLOW",
        "market_verdict": "REVIEW",
        "trusted_action_metadata": {
            "irreversible": True,
            "action_type": "trade",
            "intent": "trade_execution_review",
        },
    }
    caller = {"irreversible": True, "action_type": "trade", "intent": "trade_execution_review"}
    result = rp._apply_p3t9b_rule(rd, caller, tuple(caller.keys()))
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_trusted_metadata_available"] is True
    assert result["p3t9b_trusted_metadata_source"] == "trusted_action_metadata"
    assert result["p3t9b_caller_metadata_ignored"] is False
    assert result["p3t9b_reason_code"] == "IRREVERSIBLE_TRADE_REVIEW_REQUIRES_HOLD"


# ── T5 : trusted source present + reversible → P3T9B NOT applied ──────────────

def test_trusted_source_reversible_no_demotion(rp):
    rd = {
        "domain": "trading",
        "x108_gate": "ALLOW",
        "market_verdict": "REVIEW",
        "trusted_action_metadata": {
            "irreversible": False,
            "action_type": "query",
            "intent": "read",
        },
    }
    caller = {"irreversible": True}
    result = rp._apply_p3t9b_rule(rd, caller, ("irreversible",))
    assert result["x108_gate"] == "ALLOW"
    assert result["p3t9b_reason_code"] == "P3T9B_NOT_APPLIED"
    assert result["p3t9b_trusted_metadata_available"] is True


# ── T6 : contradiction caller vs trusted → trusted wins ──────────────────────

def test_trusted_wins_over_caller_contradiction(rp):
    rd = {
        "domain": "trading",
        "x108_gate": "ALLOW",
        "market_verdict": "REVIEW",
        "trusted_action_metadata": {
            "irreversible": False,
            "action_type": "query",
            "intent": "safe_preview",
        },
    }
    caller = {"irreversible": True, "action_type": "trade", "intent": "trade_execution_review"}
    result = rp._apply_p3t9b_rule(rd, caller, tuple(caller.keys()))
    assert result["x108_gate"] == "ALLOW"
    assert result["p3t9b_trusted_metadata_available"] is True
    assert result["p3t9b_caller_metadata_ignored"] is False
    assert "p3t9b_caller_action_meta_untrusted" in result


# ── T7 : no metadata at all, trading ALLOW+REVIEW → HOLD (fail-safe) ─────────

def test_no_metadata_fail_safe_hold(rp):
    rd = {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW"}
    result = rp._apply_p3t9b_rule(rd, {}, ())
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_trusted_metadata_available"] is False
    assert result["p3t9b_demoted_for_missing_trusted_metadata"] is True


# ── T8 : never produces ACT ───────────────────────────────────────────────────

def test_never_produces_act(rp):
    for rd in [
        {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW"},
        {"domain": "trading", "x108_gate": "BLOCK", "market_verdict": "BLOCK"},
        {"domain": "bank", "x108_gate": "ALLOW", "market_verdict": "APPROVED"},
    ]:
        result = rp._apply_p3t9b_rule(dict(rd), {}, ())
        assert result.get("x108_gate") != "ACT"
        assert result.get("market_verdict") != "ACT"
        assert "emits_act" not in result


# ── T9 : DECISION_AUTHORITY=KX108_ONLY not overridden ────────────────────────

def test_decision_authority_kx108_only_not_overridden(rp):
    rd = {"domain": "trading", "x108_gate": "ALLOW", "market_verdict": "REVIEW",
          "decision_authority": "KX108_ONLY"}
    result = rp._apply_p3t9b_rule(rd, {}, ())
    assert result.get("decision_authority") == "KX108_ONLY"


# ── T10 : _extract_trusted_action_metadata — trusted present ─────────────────

def test_extract_trusted_metadata_present(rp):
    rd = {"kernel_decision": {"irreversible": True, "action_type": "trade"}}
    meta = rp._extract_trusted_action_metadata(rd, {})
    assert meta["trusted"] is True
    assert meta["source"] == "kernel_decision"
    assert meta["irreversible_trusted"] is True


def test_extract_trusted_metadata_absent(rp):
    meta = rp._extract_trusted_action_metadata({}, {"irreversible": True})
    assert meta["trusted"] is False
    assert meta["source"] == "NONE"
    assert meta["reason"] == "MISSING_TRUSTED_ACTION_METADATA"


# ── T11 : non-trading domain not demoted ─────────────────────────────────────

def test_non_trading_domain_not_demoted(rp):
    for domain in ["bank", "gps_defense_aviation", "ecom"]:
        rd = {"domain": domain, "x108_gate": "ALLOW", "market_verdict": "REVIEW"}
        result = rp._apply_p3t9b_rule(rd, {"irreversible": True}, ("irreversible",))
        assert result["x108_gate"] == "ALLOW"
        assert result["p3t9b_reason_code"] == "P3T9B_NOT_APPLIED"


# ── T12 : HOLD/BLOCK preserved unchanged ─────────────────────────────────────

def test_hold_not_downgraded(rp):
    rd = {"domain": "trading", "x108_gate": "HOLD", "market_verdict": "REVIEW"}
    result = rp._apply_p3t9b_rule(rd, {"irreversible": True}, ("irreversible",))
    assert result["x108_gate"] == "HOLD"
    assert result["p3t9b_reason_code"] == "P3T9B_NOT_APPLIED"


def test_block_not_changed(rp):
    rd = {"domain": "trading", "x108_gate": "BLOCK", "market_verdict": "REVIEW"}
    result = rp._apply_p3t9b_rule(rd, {"irreversible": True}, ("irreversible",))
    assert result["x108_gate"] == "BLOCK"


# ── T13 : audit fields always present ────────────────────────────────────────

def test_audit_fields_always_present(rp):
    rd = {"domain": "bank", "x108_gate": "ALLOW", "market_verdict": "APPROVED"}
    result = rp._apply_p3t9b_rule(rd, {}, ())
    for field in [
        "p3t9b_trusted_metadata_available",
        "p3t9b_trusted_metadata_source",
        "p3t9b_caller_metadata_ignored",
        "p3t9b_demoted_for_missing_trusted_metadata",
        "p3t9b_reason_code",
        "p3t9b_caller_action_meta_untrusted",
    ]:
        assert field in result, f"missing audit field: {field}"
