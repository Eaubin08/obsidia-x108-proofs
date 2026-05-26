import pytest
from periphery.bias.bias_gate import apply_bias_gate


def test_unvalidated_bias_holds():
    r = apply_bias_gate("bg1", bias_score=0.8, bias_validated=False)
    assert r.gate_result == "HOLD"
    assert r.bias_detected is True
    assert r.bias_validated is False


def test_validated_bias_passes():
    r = apply_bias_gate("bg2", bias_score=0.3, bias_validated=True)
    assert r.gate_result == "PASS"
    assert r.bias_validated is True


def test_high_severity_unvalidated_holds():
    r = apply_bias_gate("bg3", bias_score=0.95, bias_validated=False)
    assert r.gate_result == "HOLD"
    assert r.bias_detected is True


def test_zero_bias_no_detection():
    r = apply_bias_gate("bg4", bias_score=0.0, bias_validated=True)
    assert r.gate_result == "PASS"
    assert r.bias_detected is False


def test_dict_has_required_fields():
    r = apply_bias_gate("bg5", bias_score=0.5, bias_validated=False)
    d = r.to_dict()
    assert "gate_result" in d and "bias_detected" in d and "bias_validated" in d and "reason" in d
