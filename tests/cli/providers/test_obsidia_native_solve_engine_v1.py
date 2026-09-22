from __future__ import annotations

import hashlib
import json
import subprocess
import sys

from pathlib import Path

import pytest


ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from scripts.providers.brody_native_tooling_analysis_v1 import (
    ANALYSIS_ID,
    analyze_brody_native_tooling_prompt,
)

from scripts.providers.obsidure_native_solve_engine_v1 import (
    BACKEND_ID,
    MODEL_ID,
    ObsidureNativeSolveEngine,
    ObsidureNativeSolveError,
)

from scripts.providers.obsidia_native_solve_stack_v1 import (
    STACK_ID,
    ObsidiaNativeSolveStack,
)

from scripts.providers.obsidia_native_tooling_session_v1 import (
    NativeToolingTarget,
    run_native_multi_target_phase1,
)


SOURCE = (
    '"""Demo."""\n'
    '\n'
    'import json\n'
    'from pathlib import Path\n'
    '\n'
    'MODE = "v1"\n'
    'LIMIT = 3\n'
    '\n'
    'class Demo:\n'
    '    pass\n'
    '\n'
    'def run():\n'
    '    return MODE\n'
)


def _solve_objective(
    strategies,
):

    return (
        "Solve bounded tooling objective.\n"
        "NATIVE_SOLVE_JSON="
        + json.dumps(
            {
                "strategies": (
                    strategies
                )
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def _prompt(
    objective,
    *,
    target=(
        "scripts/providers/demo.py"
    ),
    source=SOURCE,
):

    return json.dumps(
        {
            "contract": (
                "TOOLING_CODE_GENERATION_PROMPT_V1"
            ),
            "objective": objective,
            "target_path": target,
            "base_sha": "b" * 40,
            "target_before_sha256": (
                hashlib.sha256(
                    source.encode(
                        "utf-8"
                    )
                ).hexdigest()
            ),
            "current_source": (
                source
            ),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _run(
    cwd: Path,
    *args: str,
) -> str:

    cp = subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    if cp.returncode != 0:

        raise AssertionError(
            f"command failed: {args}\n"
            f"stdout={cp.stdout}\n"
            f"stderr={cp.stderr}"
        )

    return cp.stdout.strip()


def _make_repo(
    tmp_path: Path,
) -> Path:

    repo = (
        tmp_path
        / "repo"
    )

    repo.mkdir()


    _run(
        repo,
        "git",
        "init",
    )

    _run(
        repo,
        "git",
        "config",
        "user.email",
        "solve@obsidia.invalid",
    )

    _run(
        repo,
        "git",
        "config",
        "user.name",
        "Obsidia Solve",
    )

    _run(
        repo,
        "git",
        "config",
        "core.autocrlf",
        "false",
    )


    for name in (
        "one.py",
        "two.py",
    ):

        path = (
            repo
            / "scripts"
            / "providers"
            / name
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            SOURCE.encode(
                "utf-8"
            )
        )


    _run(
        repo,
        "git",
        "add",
        ".",
    )

    _run(
        repo,
        "git",
        "commit",
        "-m",
        "base",
    )

    return repo


def test_brody_analysis_extracts_structure():

    objective = _solve_objective(
        [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "analysis proof"
                ),
            }
        ]
    )


    analysis = (
        analyze_brody_native_tooling_prompt(
            _prompt(
                objective
            )
        )
    )


    assert (
        analysis.analysis_id
        == ANALYSIS_ID
    )

    assert (
        analysis.module_docstring_present
        is True
    )

    assert (
        analysis.import_roots
        == (
            "json",
            "pathlib",
        )
    )

    assert (
        analysis.top_level_constants
        == (
            "MODE",
            "LIMIT",
        )
    )

    assert (
        analysis.class_names
        == (
            "Demo",
        )
    )

    assert (
        analysis.function_names
        == (
            "run",
        )
    )

    assert (
        analysis.target_is_tooling
        is True
    )

    assert (
        analysis.readonly
        is True
    )


def test_strategy_fallback_records_failure_then_pass():

    objective = _solve_objective(
        [
            {
                "op": (
                    "replace_exact_text_once"
                ),
                "old": (
                    "__missing_text__"
                ),
                "new": "x",
            },
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "fallback proof"
                ),
            },
        ]
    )


    engine = (
        ObsidureNativeSolveEngine()
    )


    result = engine.generate_text(
        _prompt(
            objective
        )
    )


    assert (
        result.backend_id
        == BACKEND_ID
    )

    assert (
        result.model_id
        == MODEL_ID
    )

    assert (
        "# fallback proof"
        in result.output_text
    )


    attempts = (
        result.metadata[
            "attempts"
        ]
    )


    assert len(
        attempts
    ) == 2

    assert (
        attempts[0][
            "status"
        ]
        == "FAIL"
    )

    assert (
        attempts[0][
            "error"
        ]
        == "EXACT_OLD_NOT_FOUND"
    )

    assert (
        attempts[1][
            "status"
        ]
        == "PASS"
    )


def test_replace_exact_text_once():

    objective = _solve_objective(
        [
            {
                "op": (
                    "replace_exact_text_once"
                ),
                "old": (
                    'MODE = "v1"'
                ),
                "new": (
                    'MODE = "v2"'
                ),
            }
        ]
    )


    result = (
        ObsidureNativeSolveEngine()
        .generate_text(
            _prompt(
                objective
            )
        )
    )


    assert (
        'MODE = "v2"'
        in result.output_text
    )

    assert (
        'MODE = "v1"'
        not in result.output_text
    )


def test_set_top_level_constant():

    objective = _solve_objective(
        [
            {
                "op": (
                    "set_top_level_constant"
                ),
                "name": "LIMIT",
                "value": 9,
            }
        ]
    )


    result = (
        ObsidureNativeSolveEngine()
        .generate_text(
            _prompt(
                objective
            )
        )
    )


    assert (
        "LIMIT = 9"
        in result.output_text
    )


def test_unknown_constant_fails_closed():

    objective = _solve_objective(
        [
            {
                "op": (
                    "set_top_level_constant"
                ),
                "name": (
                    "DOES_NOT_EXIST"
                ),
                "value": 1,
            }
        ]
    )


    with pytest.raises(
        ObsidureNativeSolveError,
        match=(
            "NATIVE_SOLVE_EXHAUSTED:"
            "CONSTANT_NOT_FOUND"
        ),
    ):

        (
            ObsidureNativeSolveEngine()
            .generate_text(
                _prompt(
                    objective
                )
            )
        )


def test_target_scope_fails_closed():

    objective = _solve_objective(
        [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": "x",
            }
        ]
    )


    with pytest.raises(
        ObsidureNativeSolveError,
    ):

        (
            ObsidureNativeSolveEngine()
            .generate_text(
                _prompt(
                    objective,
                    target=(
                        "server.kernel.py"
                    ),
                )
            )
        )


def test_obsidia_remains_visible_producer():

    objective = _solve_objective(
        [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "producer proof"
                ),
            }
        ]
    )


    from scripts.providers.tooling_generation_contract_v1 import (
        ToolingGenerationRequest,
    )


    prompt = _prompt(
        objective
    )


    request = (
        ToolingGenerationRequest(
            generation_id="solve",
            objective=objective,
            objective_sha256=(
                hashlib.sha256(
                    objective.encode(
                        "utf-8"
                    )
                ).hexdigest()
            ),
            target_path=(
                "scripts/providers/demo.py"
            ),
            base_sha="b" * 40,
            target_before_sha256=(
                hashlib.sha256(
                    SOURCE.encode(
                        "utf-8"
                    )
                ).hexdigest()
            ),
            prompt=prompt,
            prompt_sha256=(
                hashlib.sha256(
                    prompt.encode(
                        "utf-8"
                    )
                ).hexdigest()
            ),
            current_source=SOURCE,
        )
    )


    stack = (
        ObsidiaNativeSolveStack()
    )


    result = stack.generate(
        request
    )


    assert (
        result.provider_id
        == "OBSIDIA_TOOLING_GENERATOR_V1"
    )

    assert (
        result.model_id
        == (
            BACKEND_ID
            + "/"
            + MODEL_ID
        )
    )

    assert (
        stack.last_metadata[
            "stack_id"
        ]
        == STACK_ID
    )

    assert (
        stack.last_metadata[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )


def test_multi_target_native_session_to_plan_proposed(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )


    one = _solve_objective(
        [
            {
                "op": (
                    "replace_exact_text_once"
                ),
                "old": "__missing__",
                "new": "x",
            },
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "multi target one"
                ),
            },
        ]
    )


    two = _solve_objective(
        [
            {
                "op": (
                    "set_top_level_constant"
                ),
                "name": "LIMIT",
                "value": 8,
            }
        ]
    )


    head_before = _run(
        repo,
        "git",
        "rev-parse",
        "HEAD",
    )


    worktrees_before = _run(
        repo,
        "git",
        "worktree",
        "list",
        "--porcelain",
    )


    result = (
        run_native_multi_target_phase1(
            repo_root=repo,
            targets=[
                NativeToolingTarget(
                    target_path=(
                        "scripts/providers/one.py"
                    ),
                    objective=one,
                ),
                NativeToolingTarget(
                    target_path=(
                        "scripts/providers/two.py"
                    ),
                    objective=two,
                ),
            ],
            artifact_root=(
                tmp_path
                / "artifacts"
            ),
            session_id=(
                "multi-target-test"
            ),
        )
    )


    assert (
        result["status"]
        == "PLAN_PROPOSED"
    )


    assert (
        result[
            "candidate_files"
        ]
        == [
            "scripts/providers/one.py",
            "scripts/providers/two.py",
        ]
    )


    assert len(
        result[
            "generations"
        ]
    ) == 2


    assert (
        result[
            "generations"
        ][0][
            "solve_attempts"
        ][0][
            "status"
        ]
        == "FAIL"
    )


    assert (
        result[
            "generations"
        ][0][
            "solve_attempts"
        ][1][
            "status"
        ]
        == "PASS"
    )


    assert (
        _run(
            repo,
            "git",
            "rev-parse",
            "HEAD",
        )
        == head_before
    )


    assert (
        _run(
            repo,
            "git",
            "status",
            "--porcelain=v1",
        )
        == ""
    )


    assert (
        _run(
            repo,
            "git",
            "worktree",
            "list",
            "--porcelain",
        )
        == worktrees_before
    )


def test_multi_target_rejects_duplicate_target(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )


    objective = _solve_objective(
        [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": "duplicate",
            }
        ]
    )


    from scripts.providers.obsidia_native_tooling_session_v1 import (
        ObsidiaNativeSessionError,
    )


    with pytest.raises(
        ObsidiaNativeSessionError,
        match=(
            "SESSION_DUPLICATE_TARGET"
        ),
    ):

        run_native_multi_target_phase1(
            repo_root=repo,
            targets=[
                NativeToolingTarget(
                    (
                        "scripts/providers/"
                        "one.py"
                    ),
                    objective,
                ),
                NativeToolingTarget(
                    (
                        "scripts/providers/"
                        "one.py"
                    ),
                    objective,
                ),
            ],
            artifact_root=(
                tmp_path
                / "artifacts"
            ),
            session_id="duplicate",
        )


def test_native_solve_modules_have_no_external_engines():

    files = [
        ANALYSIS_ID,
    ]

    del files


    paths = [
        (
            ROOT
            / "scripts"
            / "providers"
            / "brody_native_tooling_analysis_v1.py"
        ),
        (
            ROOT
            / "scripts"
            / "providers"
            / "obsidure_native_solve_engine_v1.py"
        ),
        (
            ROOT
            / "scripts"
            / "providers"
            / "obsidia_native_solve_stack_v1.py"
        ),
    ]


    banned = (
        "anthropic",
        "openai",
        "ollama",
        "requests",
        "httpx",
    )


    for path in paths:

        lower = path.read_text(
            encoding="utf-8"
        ).lower()


        for token in banned:

            assert (
                token
                not in lower
            )


def test_no_historical_agent_obsidure_import():

    paths = [
        (
            "scripts/providers/"
            "brody_native_tooling_analysis_v1.py"
        ),
        (
            "scripts/providers/"
            "obsidure_native_solve_engine_v1.py"
        ),
        (
            "scripts/providers/"
            "obsidia_native_solve_stack_v1.py"
        ),
        (
            "scripts/providers/"
            "obsidia_native_tooling_session_v1.py"
        ),
    ]


    for rel in paths:

        source = (
            ROOT
            / rel
        ).read_text(
            encoding="utf-8"
        )


        assert (
            "periphery.agents.agent_obsidure"
            not in source
        )
