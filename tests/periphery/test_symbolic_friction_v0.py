"""SYMBOLIC_FRICTION_V0 — properties P1-P7, input guards, characterization of existing defects.

The component is imported lazily so that the characterization tests also run where it does not exist yet.
"""
import importlib.util
import math
import re
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM"


def _measure(*args, **kwargs):
    from periphery.math_core.symbolic_friction import measure_symbolic_friction

    return measure_symbolic_friction(*args, **kwargs)


def _numbers(record):
    out = []
    for value in record.values():
        if isinstance(value, dict):
            out.extend(_numbers(value))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            out.append(value)
    return out


def test_friction_above_threshold_keeps_both_values_never_their_mean():
    r = _measure("t", 0.9, 0.1, threshold=0.3)
    assert r["status"] == "FRICTION"
    assert r["paradox"] == {"logical": 0.9, "diffuse": 0.1}
    assert r["divergence"] == pytest.approx(0.8)
    assert all(x != pytest.approx(0.5) for x in _numbers(r))


@pytest.mark.parametrize("logical, diffuse, threshold", [(0.75, 0.5, 0.25), (0.4, 0.3, 0.3), (0.6, 0.6, 0.15), (0.6, 0.6, 0.0)])
def test_convergence_at_or_below_threshold(logical, diffuse, threshold):
    assert _measure("t", logical, diffuse, threshold=threshold)["status"] == "CONVERGENCE_OK"


@pytest.mark.parametrize("bad", [None, math.nan, math.inf, -math.inf, "0.5", True, False, [0.5], object()])
def test_invalid_or_unknown_value_is_not_comparable(bad):
    for logical, diffuse in ((bad, 0.5), (0.5, bad)):
        r = _measure("t", logical, diffuse, threshold=0.3)
        assert r["status"] == "NOT_COMPARABLE"
        assert r["divergence"] is None
        assert r["not_comparable_reasons"]
        assert r["paradox"]["logical"] is logical and r["paradox"]["diffuse"] is diffuse


def test_divergence_overflow_is_not_comparable():
    r = _measure("t", 1e308, -1e308, threshold=0.3)
    assert r["status"] == "NOT_COMPARABLE"
    assert r["not_comparable_reasons"] == ["DIVERGENCE_NOT_FINITE"]


@pytest.mark.parametrize("threshold", [None, math.nan, math.inf, -0.1, True, "0.3"])
def test_invalid_threshold_is_rejected(threshold):
    with pytest.raises(ValueError):
        _measure("t", 0.5, 0.3, threshold=threshold)


def test_threshold_is_required_and_keyword_only():
    with pytest.raises(TypeError):
        _measure("t", 0.5, 0.3)
    with pytest.raises(TypeError):
        _measure("t", 0.5, 0.3, 0.3)


def test_trigger_must_be_text():
    with pytest.raises(ValueError):
        _measure(None, 0.5, 0.3, threshold=0.3)


@pytest.mark.parametrize("threshold, expected", [(0.15, "FRICTION"), (0.3, "CONVERGENCE_OK")])
def test_threshold_is_explicit_and_recorded(threshold, expected):
    r = _measure("t", 0.5, 0.3, threshold=threshold)
    assert r["status"] == expected
    assert r["threshold"] == threshold


def test_record_and_trigger_digest_are_deterministic():
    a = _measure("même entrée", 0.9, 0.1, threshold=0.3)
    assert a == _measure("même entrée", 0.9, 0.1, threshold=0.3)
    assert a["trigger_digest"] != _measure("autre entrée", 0.9, 0.1, threshold=0.3)["trigger_digest"]
    assert len(a["trigger_digest"]) == 64


def test_no_decision_no_memory_write():
    with mock.patch("builtins.open", side_effect=AssertionError("no IO")):
        r = _measure("t", 0.9, 0.1, threshold=0.3)
    assert r["decision_authority"] == "KX108_ONLY" and r["advisory_only"] is True
    assert r["can_decide"] is False and r["emits_act"] is False and r["memory_write"] is False
    words = set(re.findall(r"[A-Z]+", " ".join(map(str, r.values())).upper()))
    assert not words & {"ALLOW", "BLOCK", "ACT", "HOLD", "VETO"}


def test_divergence_and_status_are_symmetric():
    a = _measure("t", 0.9, 0.1, threshold=0.3)
    b = _measure("t", 0.1, 0.9, threshold=0.3)
    assert (a["divergence"], a["status"]) == (b["divergence"], b["status"])
    assert b["paradox"] == {"logical": 0.1, "diffuse": 0.9}


def test_scale_comparability_is_not_claimed():
    r = _measure("t", 0.9, 0.1, threshold=0.3)
    assert "SCALE_COMPARABILITY_NOT_DEMONSTRATED" in r["limitations"]
    assert r["provenance"].endswith("protocole_friction_symbolique")


def _load_pack(name):
    spec = importlib.util.spec_from_file_location(f"pack_{name}", PACK / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_pack_stub_characterization():
    """Unchanged historical stub: a bare float, a crash on None, NaN read as 'no incoherence'."""
    friction = _load_pack("friction_symbolique").friction
    check = _load_pack("check_incoherence").check
    assert friction(0.9, 0.1) == pytest.approx(0.8)
    with pytest.raises(TypeError):
        friction(0.9, None)
    assert check(friction(0.9, math.nan)) is False


def test_existing_drift_classifier_characterization():
    """Unchanged periphery.math_core.drift_classifier: NaN is classified STABLE with decision_allowed True."""
    from periphery.math_core import drift_classifier

    report = drift_classifier.DriftReport.compute([0.9], [math.nan])
    assert report.drift_class == drift_classifier.DriftClass.STABLE
    assert report.decision_allowed is True
