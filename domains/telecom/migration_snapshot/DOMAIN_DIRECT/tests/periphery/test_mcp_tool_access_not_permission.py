import pytest
from periphery.mcp.mcp_permission_matrix import evaluate_tool_access


def test_tool_access_not_same_as_permission():
    r = evaluate_tool_access("write_file", has_permission=False)
    assert r.access_granted is False
    assert r.permission_required is True


def test_high_risk_without_permission_denied():
    r = evaluate_tool_access("execute_command", has_permission=False)
    assert r.access_granted is False
    assert r.risk_level in ("HIGH", "CRITICAL")


def test_low_risk_tool_accessible():
    r = evaluate_tool_access("read_file", has_permission=False)
    assert r.access_granted is True
    assert r.risk_level == "LOW"


def test_high_risk_with_permission_granted():
    r = evaluate_tool_access("call_api", has_permission=True)
    assert r.access_granted is True
    assert r.permission_required is True


def test_dict_has_required_fields():
    r = evaluate_tool_access("database_query", has_permission=False)
    d = r.to_dict()
    assert "tool_name" in d and "access_granted" in d and "permission_required" in d and "risk_level" in d
