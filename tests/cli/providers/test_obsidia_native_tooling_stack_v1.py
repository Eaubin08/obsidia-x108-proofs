from __future__ import annotations

import ast
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


from scripts.providers.brody_native_tooling_context_v1 import (
    BRODY_NATIVE_CONTEXT_ID,
    BrodyNativeContextError,
    build_brody_native_tooling_context,
)

from scripts.providers.obsidure_native_tooling_backend_v1 import (
    BACKEND_ID,
    MODEL_ID,
    ObsidureNativeToolingBackend,
    ObsidureNativeToolingError,
)

from scripts.providers.obsidia_native_tooling_stack_v1 import (
    STACK_ID,
    ObsidiaNativeToolingStack,
)

from scripts.providers.tooling_generation_adapter_v1 import (
    generate_tooling_source,
)

from scripts.providers.tooling_generation_contract_v1 import (
    ToolingGenerationRequest,
)

from scripts import (
    obsidure_tooling_candidate_v1 as C2,
)


OLD = (
    '"""Demo module."""\n'
    '\n'
    'VALUE = "old"\n'
)


COMMENT = (
    "R8-C3b3 native internal generation proof."
)


def _objective(
    comment=COMMENT,
):

    return (
        "Produce one bounded internal native tooling edit.\n"
        "NATIVE_EDIT_JSON="
        + json.dumps(
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": comment,
            },
            separators=(",", ":"),
        )
    )


def _prompt(
    objective=None,
    target=(
        "scripts/providers/demo.py"
    ),
    source=OLD,
):

    payload = {
        "contract": (
            "TOOLING_CODE_GENERATION_PROMPT_V1"
        ),
        "objective": (
            objective
            or _objective()
        ),
        "target_path": target,
        "base_sha": "b" * 40,
        "target_before_sha256": (
            hashlib.sha256(
                source.encode(
                    "utf-8"
                )
            ).hexdigest()
        ),
        "current_source": source,
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _request():

    prompt = _prompt()

    return ToolingGenerationRequest(
        generation_id="native-test",
        objective=_objective(),
        objective_sha256=(
            hashlib.sha256(
                _objective().encode(
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
                OLD.encode(
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
        current_source=OLD,
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

    repo = tmp_path / "repo"

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
        "native@obsidia.invalid",
    )

    _run(
        repo,
        "git",
        "config",
        "user.name",
        "Obsidia Native",
    )

    _run(
        repo,
        "git",
        "config",
        "core.autocrlf",
        "false",
    )

    target = (
        repo
        / "scripts"
        / "providers"
        / "demo.py"
    )

    target.parent.mkdir(
        parents=True
    )

    target.write_bytes(
        OLD.encode(
            "utf-8"
        )
    )

    _run(
        repo,
        "git",
        "add",
        "scripts/providers/demo.py",
    )

    _run(
        repo,
        "git",
        "commit",
        "-m",
        "base",
    )

    return repo


def test_brody_native_builds_readonly_context():

    prompt = _prompt()

    context = (
        build_brody_native_tooling_context(
            prompt
        )
    )

    assert (
        context.context_id
        == BRODY_NATIVE_CONTEXT_ID
    )

    assert (
        context.intent
        == "NATIVE_TOOLING_EDIT"
    )

    assert (
        context.current_source
        == OLD
    )

    assert (
        context.readonly
        is True
    )

    assert (
        context.can_decide
        is False
    )

    assert (
        context.kernel_mutation
        is False
    )


def test_brody_rejects_invalid_prompt():

    with pytest.raises(
        BrodyNativeContextError,
    ):
        build_brody_native_tooling_context(
            "not-json"
        )


def test_obsidure_native_generates_complete_source():

    backend = (
        ObsidureNativeToolingBackend()
    )

    result = backend.generate_text(
        _prompt()
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
        "# "
        + COMMENT
        in result.output_text
    )

    assert (
        'VALUE = "old"'
        in result.output_text
    )

    ast.parse(
        result.output_text
    )


def test_obsidure_preserves_full_source():

    result = (
        ObsidureNativeToolingBackend()
        .generate_text(
            _prompt()
        )
    )

    expected = (
        '"""Demo module."""\n'
        '# '
        + COMMENT
        + '\n'
        '\n'
        'VALUE = "old"\n'
    )

    assert (
        result.output_text
        == expected
    )


@pytest.mark.parametrize(
    "target",
    [
        "server.kernel.sealed.cjs",
        "proofs/demo.py",
        "periphery/demo.py",
        "../scripts/providers/demo.py",
        "scripts/gates/demo.py",
    ],
)
def test_obsidure_native_scope_fails_closed(
    target,
):

    backend = (
        ObsidureNativeToolingBackend()
    )

    with pytest.raises(
        ObsidureNativeToolingError,
    ):
        backend.generate_text(
            _prompt(
                target=target
            )
        )


def test_unsupported_operation_fails_closed():

    objective = (
        "Native edit.\n"
        "NATIVE_EDIT_JSON="
        + json.dumps(
            {
                "op": "replace_everything",
                "comment": "x",
            }
        )
    )

    with pytest.raises(
        ObsidureNativeToolingError,
        match="NATIVE_OPERATION_UNSUPPORTED",
    ):
        (
            ObsidureNativeToolingBackend()
            .generate_text(
                _prompt(
                    objective=objective
                )
            )
        )


def test_duplicate_edit_fails_closed():

    source = (
        '"""Demo."""\n'
        "# "
        + COMMENT
        + "\n"
        "VALUE = 1\n"
    )

    with pytest.raises(
        ObsidureNativeToolingError,
        match="NATIVE_EDIT_ALREADY_APPLIED",
    ):
        (
            ObsidureNativeToolingBackend()
            .generate_text(
                _prompt(
                    source=source
                )
            )
        )


def test_native_stack_keeps_obsidia_as_producer():

    stack = (
        ObsidiaNativeToolingStack()
    )

    result = stack.generate(
        _request()
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


def test_native_stack_to_c3a_external_artifact(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )

    stack = (
        ObsidiaNativeToolingStack()
    )

    objective = _objective()

    generation = (
        generate_tooling_source(
            repo_root=repo,
            objective=objective,
            target_path=(
                "scripts/providers/demo.py"
            ),
            artifact_root=(
                tmp_path
                / "generation"
            ),
            provider=stack,
            generation_id=(
                "native-c3a"
            ),
        )
    )

    artifact = Path(
        generation[
            "source_artifact_path"
        ]
    )

    generated = (
        artifact.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "# "
        + COMMENT
        in generated
    )

    assert (
        generation[
            "provider_id"
        ]
        == "OBSIDIA_TOOLING_GENERATOR_V1"
    )

    assert (
        BACKEND_ID
        in generation[
            "model_id"
        ]
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


def test_native_full_chain_to_plan_proposed(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )

    objective = _objective()

    generation = (
        generate_tooling_source(
            repo_root=repo,
            objective=objective,
            target_path=(
                "scripts/providers/demo.py"
            ),
            artifact_root=(
                tmp_path
                / "generation"
            ),
            provider=(
                ObsidiaNativeToolingStack()
            ),
            generation_id=(
                "native-full-chain"
            ),
        )
    )

    candidate = (
        C2.produce_candidate(
            repo,
            objective,
            [
                (
                    "scripts/providers/demo.py",
                    Path(
                        generation[
                            "source_artifact_path"
                        ]
                    ),
                )
            ],
            (
                tmp_path
                / "candidate"
            ),
        )
    )

    worktrees_before = _run(
        repo,
        "git",
        "worktree",
        "list",
        "--porcelain",
    )

    plan = (
        C2.build_phase1_plan(
            repo,
            candidate,
        )
    )

    worktrees_after = _run(
        repo,
        "git",
        "worktree",
        "list",
        "--porcelain",
    )

    assert (
        plan["status"]
        == "PLAN_PROPOSED"
    )

    assert (
        plan[
            "approved_scope_proposal"
        ]
        == [
            "scripts/providers/demo.py"
        ]
    )

    assert (
        plan[
            "candidate_patch_hash"
        ]
        == candidate.patch_sha256
    )

    assert (
        worktrees_before
        == worktrees_after
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


def test_native_modules_have_no_external_provider_imports():

    paths = [
        (
            ROOT
            / "scripts"
            / "providers"
            / "brody_native_tooling_context_v1.py"
        ),
        (
            ROOT
            / "scripts"
            / "providers"
            / "obsidure_native_tooling_backend_v1.py"
        ),
        (
            ROOT
            / "scripts"
            / "providers"
            / "obsidia_native_tooling_stack_v1.py"
        ),
    ]

    banned = {
        "requests",
        "httpx",
        "urllib",
        "anthropic",
        "openai",
        "ollama",
        "subprocess",
    }

    for path in paths:

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        imports = set()

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.Import,
            ):

                for alias in node.names:
                    imports.add(
                        alias.name.split(
                            "."
                        )[0]
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):

                if node.module:
                    imports.add(
                        node.module.split(
                            "."
                        )[0]
                    )

        assert not (
            imports
            & banned
        )


def test_native_modules_do_not_import_historical_agent_obsidure():

    for rel in (
        (
            "scripts/providers/"
            "brody_native_tooling_context_v1.py"
        ),
        (
            "scripts/providers/"
            "obsidure_native_tooling_backend_v1.py"
        ),
        (
            "scripts/providers/"
            "obsidia_native_tooling_stack_v1.py"
        ),
    ):

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
