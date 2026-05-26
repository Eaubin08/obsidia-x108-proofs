import pytest
from periphery.github.github_workflow_guard import guard_workflow_action


def test_auto_merge_blocked():
    r = guard_workflow_action("AUTO_MERGE")
    assert r.blocked is True
    assert r.requires_human is True


def test_force_merge_blocked():
    r = guard_workflow_action("FORCE_MERGE")
    assert r.blocked is True
    assert r.requires_human is True


def test_bypass_review_blocked():
    r = guard_workflow_action("BYPASS_REVIEW")
    assert r.blocked is True
    assert r.requires_human is True


def test_create_pr_allowed():
    r = guard_workflow_action("CREATE_PR")
    assert r.blocked is False
    assert r.requires_human is True


def test_merge_requires_human():
    r = guard_workflow_action("MERGE")
    assert r.blocked is True
    assert r.requires_human is True


def test_dict_fields():
    r = guard_workflow_action("PUSH_BRANCH")
    d = r.to_dict()
    assert "action" in d and "blocked" in d and "reason" in d and "requires_human" in d
