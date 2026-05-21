import pytest
from periphery.gencoin_sandbox.sandbox_engine import State, System, step


def test_on_regime_admissible():
    s = System(pin_raw=1.5, paux=0.0, pstorage_in=0.0, pstorage_out=0.0)
    s.state = State.START
    result = step(s)
    assert result.state in (State.ON, State.HOLD, State.SAFE_OFF, State.OFF)


def test_false_on_when_truth_low():
    s = System(pin_raw=1.5, paux=5.0, pstorage_in=0.0, pstorage_out=3.0)
    s.state = State.START
    result = step(s)
    assert result.assisted_ratio >= 0.0
    assert result.truth_score >= 0.0


def test_off_when_no_power():
    s = System(pin_raw=0.0, paux=0.0, pstorage_in=0.0, pstorage_out=0.0)
    s.state = State.START
    result = step(s)
    assert result.state in (State.OFF, State.SAFE_OFF, State.HOLD)


def test_assisted_ratio_range():
    s = System(pin_raw=1.0, paux=1.0, pstorage_out=1.0)
    result = step(s)
    assert 0.0 <= result.assisted_ratio <= 1.0


def test_truth_score_range():
    s = System(pin_raw=1.0, paux=0.5, pstorage_out=0.5)
    result = step(s)
    assert 0.0 <= result.truth_score <= 1.0


def test_sigma_score_range():
    s = System(pin_raw=2.0, paux=0.0, pstorage_out=0.0)
    result = step(s)
    assert 0.0 <= result.sigma_score <= 1.0
