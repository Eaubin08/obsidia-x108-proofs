"""Compare a full X108 pytest log to the pinned known-failure baseline.

Forensic audit only. A zero return code means NO NEW FAILURES,
not that the global CI is green. Does not exclude tests or alter pytest.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "docs/runtime/ENTERPRISE_INTERREPO_GLOBAL_FREEZE_V0.json"
)


def extract_failed_test_ids(log: str) -> list[str]:
    names: set[str] = set()
    for line in log.splitlines():
        if "FAILED tests/" not in line:
            continue
        token = line.split("FAILED ", 1)[1].split(" - ", 1)[0].strip()
        if "::" not in token or not token.startswith("tests/"):
            raise ValueError("MALFORMED_PYTEST_FAILURE")
        names.add(token)
    return sorted(names)


def audit_pytest_log(log: str, baseline: list[str]) -> dict:
    found = extract_failed_test_ids(log)
    summaries = re.findall(
        r"\b(\d+) failed, (\d+) passed, (\d+) skipped, (\d+) deselected\b",
        log,
    )
    if not summaries:
        raise ValueError("GLOBAL_PYTEST_SUMMARY_MISSING")
    failed, passed, skipped, deselected = map(int, summaries[-1])
    if failed != len(found):
        raise ValueError("PYTEST_FAILURE_COUNT_DISAGREEMENT")
    old, new = set(baseline), set(found)
    unexpected = sorted(new - old)
    resolved = sorted(old - new)
    return {
        "schema": "OBSIDIA_GLOBAL_REGRESSION_BASELINE_AUDIT_V0",
        "verdict": "REGRESSION_DETECTED" if unexpected else
                   "NO_NEW_FAILURES_GLOBAL_CI_RED",
        "global_ci_green": failed == 0,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "deselected": deselected,
        "unexpected_failures": unexpected,
        "baseline_resolved": resolved,
        "failure_list": found,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pytest-log", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = audit_pytest_log(
        args.pytest_log.read_text(encoding="utf-8"),
        baseline["known_failed_tests"],
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["unexpected_failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
