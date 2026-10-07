import json
from pathlib import Path

import pytest

from scripts.verify_enterprise_regression_baseline_v0 import audit_pytest_log

MANIFEST_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/runtime/ENTERPRISE_INTERREPO_GLOBAL_FREEZE_V0.json"
)


def test_freeze_manifest_is_pinned_and_non_sovereign():
    value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert value["schema"] == "OBSIDIA_ENTERPRISE_INTERREPO_GLOBAL_FREEZE_V0"
    assert value["source"]["head_sha"] == "3f3ecac29e33c52988faf4f021bc11c4580b0edc"
    assert value["monde"]["head_sha"] == "d1b78d4de11ca2da4d31f88799ebb75fd3aa1698"
    assert value["decision_authority"] == "KX108_ONLY"
    assert value["no_main_merge"] is True
    assert value["kernel_mutation"] is False
    assert value["global_ci_green"] is False
    assert value["release_readiness"] != "READY_FOR_PRODUCTION"
    assert value["source"]["full_ci"]["regressions_compared_to_earlier_head"] == 0
    assert len(value["known_failed_tests"]) == 11
    assert len(set(value["known_failed_tests"])) == 11


def _log(names):
    failures = "".join(
        "FAILED " + name + " - AssertionError: expected baseline\n"
        for name in names
    )
    return failures + (
        f"{len(names)} failed, 12653 passed, 46 skipped, "
        "207 deselected, 43 warnings in 345.74s\n"
    )


def test_known_failure_baseline_not_mislabeled_globally_green():
    baseline = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["known_failed_tests"]
    output = audit_pytest_log(_log(baseline), baseline)
    assert output["verdict"] == "NO_NEW_FAILURES_GLOBAL_CI_RED"
    assert output["failed"] == 11
    assert output["global_ci_green"] is False
    assert output["unexpected_failures"] == []
    assert output["baseline_resolved"] == []


def test_global_regression_audit_fails_for_unexpected_test():
    baseline = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["known_failed_tests"]
    changed = baseline + ["tests/integration/test_monde_native_read_model_v0.py::test_new_regression"]
    output = audit_pytest_log(_log(changed), baseline)
    assert output["verdict"] == "REGRESSION_DETECTED"
    assert output["unexpected_failures"] == [changed[-1]]


def test_missing_or_mismatched_pytest_summary_is_refused():
    with pytest.raises(ValueError, match="GLOBAL_PYTEST_SUMMARY_MISSING"):
        audit_pytest_log("FAILED tests/x.py::test_a - failure", [])
    with pytest.raises(ValueError, match="PYTEST_FAILURE_COUNT_DISAGREEMENT"):
        audit_pytest_log("2 failed, 10 passed, 1 skipped, 0 deselected", [])
