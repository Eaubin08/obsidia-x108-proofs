from __future__ import annotations

import os
import subprocess
import sys
import time

from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SCRIPTS = (
    ROOT
    / "scripts"
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import bounded_execution_policy_v1 as P


def test_full_suite_has_large_finite_budget():

    budget = (
        P.budget_for_test_command(
            (
                "python -m pytest "
                "tests/ -q --tb=no"
            )
        )
    )

    assert (
        budget.label
        == "PYTEST_FULL_SUITE"
    )

    assert (
        budget.hard_seconds
        == 7200
    )

    assert (
        budget.idle_seconds
        == 600
    )

    assert (
        budget.hard_seconds
        > budget.idle_seconds
    )


def test_focused_suite_has_distinct_budget():

    budget = (
        P.budget_for_test_command(
            (
                "python -m pytest "
                "tests/test_example.py -q"
            )
        )
    )

    assert (
        budget.label
        == "PYTEST_FOCUSED"
    )

    assert (
        budget.hard_seconds
        == 1800
    )

    assert (
        budget.idle_seconds
        == 300
    )


def test_budget_can_be_explicitly_overridden(
    monkeypatch,
):

    monkeypatch.setenv(
        (
            "OBSIDIA_FULL_TEST_"
            "HARD_SECONDS"
        ),
        "999",
    )

    monkeypatch.setenv(
        (
            "OBSIDIA_FULL_TEST_"
            "IDLE_SECONDS"
        ),
        "111",
    )


    budget = (
        P.budget_for_test_command(
            (
                "python -m pytest "
                "tests/ -q"
            )
        )
    )


    assert (
        budget.hard_seconds
        == 999
    )

    assert (
        budget.idle_seconds
        == 111
    )


def test_fast_command_passes():

    result = (
        P.run_bounded_command(
            [
                sys.executable,
                "-u",
                "-c",
                (
                    "print('ok', "
                    "flush=True)"
                ),
            ],
            cwd=ROOT,
            budget=P.ExecutionBudget(
                label="TEST",
                hard_seconds=5,
                idle_seconds=2,
                poll_seconds=0.05,
            ),
        )
    )


    assert result.returncode == 0

    assert (
        result.bounded_status
        == P.STATUS_PASS
    )

    assert "ok" in result.stdout

    assert (
        result.progress_events
        >= 1
    )


def test_hard_limit_is_explicit():

    started = time.monotonic()


    result = (
        P.run_bounded_command(
            [
                sys.executable,
                "-u",
                "-c",
                (
                    "import time; "
                    "time.sleep(5)"
                ),
            ],
            cwd=ROOT,
            budget=P.ExecutionBudget(
                label="HARD_TEST",
                hard_seconds=0.8,
                idle_seconds=10,
                poll_seconds=0.05,
            ),
        )
    )


    elapsed = (
        time.monotonic()
        - started
    )


    assert (
        result.returncode
        == P.EXIT_TIMEOUT_HARD_LIMIT
    )

    assert (
        result.bounded_status
        == P.STATUS_TIMEOUT_HARD_LIMIT
    )

    assert (
        "TIMEOUT_HARD_LIMIT"
        in result.stderr
    )

    assert elapsed < 4


def test_no_progress_timeout_is_explicit():

    result = (
        P.run_bounded_command(
            [
                sys.executable,
                "-u",
                "-c",
                (
                    "import time; "
                    "print('start', flush=True); "
                    "time.sleep(5)"
                ),
            ],
            cwd=ROOT,
            budget=P.ExecutionBudget(
                label="IDLE_TEST",
                hard_seconds=5,
                idle_seconds=0.8,
                poll_seconds=0.05,
            ),
        )
    )


    assert (
        result.returncode
        == P.EXIT_TIMEOUT_NO_PROGRESS
    )

    assert (
        result.bounded_status
        == P.STATUS_TIMEOUT_NO_PROGRESS
    )

    assert (
        "TIMEOUT_NO_PROGRESS"
        in result.stderr
    )

    assert (
        result.progress_events
        >= 1
    )


def test_continuing_progress_prevents_idle_timeout():

    script = (
        "import time\n"
        "for i in range(5):\n"
        "    print(i, flush=True)\n"
        "    time.sleep(0.2)\n"
    )


    result = (
        P.run_bounded_command(
            [
                sys.executable,
                "-u",
                "-c",
                script,
            ],
            cwd=ROOT,
            budget=P.ExecutionBudget(
                label="PROGRESS_TEST",
                hard_seconds=4,
                idle_seconds=0.6,
                poll_seconds=0.05,
            ),
        )
    )


    assert result.returncode == 0

    assert (
        result.bounded_status
        == P.STATUS_PASS
    )

    assert (
        result.progress_events
        >= 5
    )


def test_build_uses_bounded_policy():

    source = (
        ROOT
        / "scripts"
        / "obsidia_build.py"
    ).read_text(
        encoding="utf-8"
    )


    assert (
        "run_bounded_command"
        in source
    )

    assert (
        "budget_for_test_command"
        in source
    )

    assert (
        (
            "cwd=worktree_path, "
            "timeout=120"
        )
        not in source
    )

    assert (
        "TEST_TIMEOUT_NO_PROGRESS"
        in source
    )

    assert (
        "TEST_TIMEOUT_HARD_LIMIT"
        in source
    )


def test_policy_is_non_sovereign():

    state = P.self_check()


    assert (
        state[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        state[
            "repo_mutation"
        ]
        is False
    )

    assert (
        state[
            "memory_write"
        ]
        is False
    )

    assert (
        state[
            "kernel_mutation"
        ]
        is False
    )

    assert (
        state[
            "emits_act"
        ]
        is False
    )

    assert (
        state[
            "world_action"
        ]
        is False
    )
