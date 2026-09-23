import pytest
from periphery.world_calls.world_call_classifier import WorldCallClass, classify_world_call, is_blocked


def test_payment_forbidden():
    wcc = classify_world_call("transfer", "payment", False)
    assert wcc == WorldCallClass.FORBIDDEN_WORLD_CALL


def test_query_read_only():
    wcc = classify_world_call("query", "bank", False)
    assert wcc == WorldCallClass.READ_ONLY_WORLD_CALL


def test_irreversible_flag():
    wcc = classify_world_call("update", "bank", True)
    assert wcc == WorldCallClass.IRREVERSIBLE_WORLD_CALL


def test_reversible_update():
    wcc = classify_world_call("update", "bank", False)
    assert wcc == WorldCallClass.REVERSIBLE_WORLD_CALL


def test_forbidden_blocked():
    wcc = WorldCallClass.FORBIDDEN_WORLD_CALL
    assert is_blocked(wcc) is True


def test_read_only_not_blocked():
    wcc = WorldCallClass.READ_ONLY_WORLD_CALL
    assert is_blocked(wcc) is False
