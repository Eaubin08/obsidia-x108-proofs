from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "run_nonrecursive_pytest.py"
)
WORKFLOW_PATH = (
    ROOT
    / ".github"
    / "workflows"
    / "x108-periphery-ci.yml"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "run_nonrecursive_pytest",
        RUNNER_PATH,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[
        spec.name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


def test_selective_detector_excludes_only_reachable_nested_tests() -> None:
    runner = _load_runner()
    nodeids = set(
        runner.discover_deselected_nodeids()
    )

    assert nodeids

    assert (
        "tests/test_p66_srl_readonly_memory_layer.py"
        "::test_p56e_regression"
        in nodeids
    )

    assert (
        "tests/test_p66_srl_readonly_memory_layer.py"
        "::test_p66_json_exists"
        not in nodeids
    )

    assert not any(
        nodeid.startswith(
            "tests/test_sigma_v18_9.py::"
        )
        for nodeid in nodeids
    )


def test_selective_detector_keeps_sigma_main_guard_outside_pytest() -> None:
    runner = _load_runner()

    analysis = runner.analyze_test_file(
        ROOT
        / "tests"
        / "test_sigma_v18_9.py"
    )

    assert analysis.deselected_tests == ()


def test_workflow_uses_selective_runner_without_file_ignores() -> None:
    workflow = WORKFLOW_PATH.read_text(
        encoding="utf-8-sig",
    )

    assert (
        "python scripts/run_nonrecursive_pytest.py "
        "-- tests/ -q --tb=short"
        in workflow
    )

    assert "--ignore=tests/test_p66" not in workflow
    assert "--ignore=tests/test_sigma_v18_9.py" not in workflow
