"""
TOP4 V4 — Connectors Sigma Free Variable fix
SCOPE=V4_ONLY  PATCH=YES_BUT_V4_ONLY  COMMIT=NO  DECISION_AUTHORITY=KX108_ONLY
"""
import sys
import importlib
import types

import pytest


def _load_connector(module_name: str, path: str):
    """Import a connector module by file path without network calls."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    # Stub 'requests' so the import doesn't fail on missing network dep
    stub = types.ModuleType("requests")
    stub.get = lambda *a, **k: None
    stub.post = lambda *a, **k: None
    sys.modules.setdefault("requests", stub)
    spec.loader.exec_module(mod)
    return mod


import os as _os
_BASE = _os.path.join(_os.path.dirname(__file__), "..", "connectors")
AVIATION = _os.path.abspath(_os.path.join(_BASE, "aviation_robo.py"))
BANK = _os.path.abspath(_os.path.join(_BASE, "bank_normal_flow.py"))
TRADING = _os.path.abspath(_os.path.join(_BASE, "trading_live.py"))


@pytest.fixture(scope="module")
def aviation():
    return _load_connector("aviation_robo", AVIATION)


@pytest.fixture(scope="module")
def bank():
    return _load_connector("bank_normal_flow", BANK)


@pytest.fixture(scope="module")
def trading():
    return _load_connector("trading_live", TRADING)


# ── T1-T3 : no crash with minimal data (no sigma in data) ─────────────────────

def test_aviation_no_sigma_no_crash(aviation):
    # gate is looked up in kernel_decision first, then sigma — not at data root
    result = aviation._extract_runtime_summary({"kernel_decision": {"x108_gate": "HOLD"}})
    assert isinstance(result, dict)
    assert result["gate"] == "HOLD"


def test_bank_no_sigma_no_crash(bank):
    result = bank._extract_runtime_summary({"kernel_decision": {"x108_gate": "HOLD"}})
    assert isinstance(result, dict)
    assert result["gate"] == "HOLD"


def test_trading_no_sigma_no_crash(trading):
    result = trading._extract_runtime_summary({"kernel_decision": {"x108_gate": "HOLD"}})
    assert isinstance(result, dict)
    assert result["gate"] == "HOLD"


# ── T4-T6 : empty data — no crash ─────────────────────────────────────────────

def test_aviation_empty_data_no_crash(aviation):
    result = aviation._extract_runtime_summary({})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


def test_bank_empty_data_no_crash(bank):
    result = bank._extract_runtime_summary({})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


def test_trading_empty_data_no_crash(trading):
    result = trading._extract_runtime_summary({})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


# ── T7-T9 : sigma in data — values picked up correctly ────────────────────────

def test_aviation_sigma_in_data(aviation):
    data = {"sigma": {"x108_gate": "BLOCK", "reason_code": "SIGMA_ANOMALY"}}
    result = aviation._extract_runtime_summary(data)
    assert result["gate"] == "BLOCK"
    assert result["reason"] == "SIGMA_ANOMALY"


def test_bank_sigma_in_data(bank):
    data = {"sigma": {"x108_gate": "ALLOW", "market_verdict": "APPROVED"}}
    result = bank._extract_runtime_summary(data)
    assert result["gate"] == "ALLOW"
    assert result["verdict"] == "APPROVED"


def test_trading_sigma_in_data(trading):
    data = {"sigma": {"x108_gate": "HOLD", "severity": "S2"}}
    result = trading._extract_runtime_summary(data)
    assert result["gate"] == "HOLD"
    assert result["severity"] == "S2"


# ── T10-T12 : sigma in raw_engine ─────────────────────────────────────────────

def test_aviation_sigma_in_raw_engine(aviation):
    data = {"raw_engine": {"sigma": {"x108_gate": "HOLD", "domain": "GPS"}}}
    result = aviation._extract_runtime_summary(data)
    assert result["gate"] == "HOLD"
    assert result["domain"] == "GPS"


def test_bank_sigma_in_raw_engine(bank):
    data = {"raw_engine": {"sigma": {"x108_gate": "BLOCK"}}}
    result = bank._extract_runtime_summary(data)
    assert result["gate"] == "BLOCK"


def test_trading_sigma_in_raw_engine(trading):
    data = {"raw_engine": {"sigma": {"x108_gate": "ALLOW"}}}
    result = trading._extract_runtime_summary(data)
    assert result["gate"] == "ALLOW"


# ── T13-T15 : kernel_decision takes priority over sigma ───────────────────────

def test_aviation_kd_priority_over_sigma(aviation):
    data = {
        "kernel_decision": {"x108_gate": "BLOCK", "reason_code": "KD_REASON"},
        "sigma": {"x108_gate": "ALLOW", "reason_code": "SIGMA_REASON"},
    }
    result = aviation._extract_runtime_summary(data)
    assert result["gate"] == "BLOCK"
    assert result["reason"] == "KD_REASON"


def test_bank_kd_priority_over_sigma(bank):
    data = {
        "kernel_decision": {"x108_gate": "HOLD"},
        "sigma": {"x108_gate": "ALLOW"},
    }
    result = bank._extract_runtime_summary(data)
    assert result["gate"] == "HOLD"


def test_trading_kd_priority_over_sigma(trading):
    data = {
        "kernel_decision": {"market_verdict": "VALIDATED"},
        "sigma": {"market_verdict": "SIGMA_VERDICT"},
    }
    result = trading._extract_runtime_summary(data)
    assert result["verdict"] == "VALIDATED"


# ── T16-T18 : sigma non-dict is sanitized to {} ───────────────────────────────

def test_aviation_sigma_non_dict_sanitized(aviation):
    result = aviation._extract_runtime_summary({"sigma": "not_a_dict"})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


def test_bank_sigma_non_dict_sanitized(bank):
    result = bank._extract_runtime_summary({"sigma": 42})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


def test_trading_sigma_non_dict_sanitized(trading):
    result = trading._extract_runtime_summary({"sigma": None})
    assert isinstance(result, dict)
    assert result["gate"] == "UNKNOWN"


# ── T19-T20 : KX108_ONLY invariants — no ACT, no mutation ─────────────────────

def test_no_act_in_result(aviation, bank, trading):
    for mod in [aviation, bank, trading]:
        result = mod._extract_runtime_summary({"sigma": {"x108_gate": "ALLOW"}})
        assert "ACT" not in str(result.get("gate", "")).upper() or result["gate"] == "ALLOW"
        assert "emits_act" not in result


def test_no_sigma_free_variable_in_module(aviation, bank, trading):
    import inspect
    for mod in [aviation, bank, trading]:
        src = inspect.getsource(mod._extract_runtime_summary)
        # sigma must be assigned locally before first use
        lines = src.strip().splitlines()
        sigma_assign_idx = next(
            (i for i, l in enumerate(lines) if "sigma = " in l and "kd.get" not in l),
            None,
        )
        assert sigma_assign_idx is not None, "sigma local assignment not found"
        first_sigma_use = next(
            (i for i, l in enumerate(lines) if "sigma.get" in l),
            None,
        )
        assert first_sigma_use is not None
        assert sigma_assign_idx < first_sigma_use, "sigma must be assigned before first sigma.get"
