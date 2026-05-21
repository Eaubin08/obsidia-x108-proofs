import pytest
from periphery.reverse_os.audience_projection import project_audience
from periphery.reverse_os.format_projection import project_format
from periphery.reverse_os.action_projection_readonly import project_action_readonly


def test_audience_projection_advisory_only():
    r = project_audience("ap1", "technical context", "technical")
    assert r.advisory_only is True
    assert r.can_decide is False


def test_forbidden_token_in_context_detected():
    r = project_audience("ap2", "Please ALLOW this action", "general")
    assert "ALLOW" in r.forbidden_tokens_detected


def test_format_projection_advisory():
    r = project_format("fp1", "executive")
    assert r.recommended_format == "bullet_summary"
    assert r.advisory_only is True
    assert r.can_decide is False


def test_action_projection_readonly():
    r = project_action_readonly("proj1", "check balance", "bank context")
    assert r.real_action_taken is False
    assert r.can_emit_act is False
    assert r.advisory_only is True


def test_action_projection_forbidden_token_withheld():
    r = project_action_readonly("proj2", "DECIDE now", "context")
    assert r.projected_action == "PROJECTION_WITHHELD"
    assert "DECIDE" in r.projection_reason
