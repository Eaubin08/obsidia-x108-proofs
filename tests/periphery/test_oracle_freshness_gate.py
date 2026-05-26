import pytest
from datetime import datetime, timezone, timedelta
from periphery.blockchain.oracle_freshness_gate import evaluate_oracle_freshness


def test_none_timestamp_stale():
    r = evaluate_oracle_freshness("oracle1", None)
    assert r.gate == "HOLD"
    assert r.is_fresh is False
    assert r.stale_risk_flag is True


def test_fresh_data_allowed():
    now = datetime.now(timezone.utc) - timedelta(seconds=30)
    r = evaluate_oracle_freshness("oracle2", now.isoformat())
    assert r.gate == "ALLOW"
    assert r.is_fresh is True


def test_stale_data_hold():
    old = datetime.now(timezone.utc) - timedelta(seconds=600)
    r = evaluate_oracle_freshness("oracle3", old.isoformat())
    assert r.gate == "HOLD"
    assert r.is_fresh is False


def test_invalid_timestamp_hold():
    r = evaluate_oracle_freshness("oracle4", "NOT_A_DATE")
    assert r.gate == "HOLD"
    assert r.stale_risk_flag is True


def test_dict_fields():
    r = evaluate_oracle_freshness("oracle5", None)
    d = r.to_dict()
    assert "gate" in d and "is_fresh" in d and "stale_risk_flag" in d
