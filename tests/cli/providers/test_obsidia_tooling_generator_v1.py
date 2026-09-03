from __future__ import annotations

import ast
import subprocess
import sys

from pathlib import Path

import pytest


ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

SCRIPTS = (
    ROOT
    / "scripts"
)

if str(
    SCRIPTS
) not in sys.path:

    sys.path.insert(
        0,
        str(SCRIPTS),
    )


from scripts.providers.obsidia_tooling_generator_v1 import (
    PRODUCER_ID,
    ObsidiaToolingGenerator,
    ObsidiaToolingGeneratorError,
    ToolingBackendResult,
    self_check,
)

from scripts.providers.tooling_generation_adapter_v1 import (
    generate_tooling_source,
)

from scripts.providers.tooling_generation_contract_v1 import (
    ToolingGenerationRequest,
)


import obsidure_tooling_candidate_v1 as C2


OLD = 'VALUE = "old"\n'
NEW_A = 'VALUE = "engine-a"\n'
NEW_B = 'VALUE = "engine-b"\n'


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


def _request():

    return ToolingGenerationRequest(
        generation_id="obsidia-generator-test",
        objective="change exact file",
        objective_sha256="o" * 64,
        target_path=(
            "scripts/obsidia_demo.py"
        ),
        base_sha="b" * 40,
        target_before_sha256="s" * 64,
        prompt='{"canonical":"prompt"}',
        prompt_sha256="p" * 64,
        current_source=OLD,
    )


class EngineA:

    backend_id = "ENGINE_A"

    def __init__(
        self,
    ):
        self.prompts = []

    def generate_text(
        self,
        prompt,
    ):

        self.prompts.append(
            prompt
        )

        return ToolingBackendResult(
            backend_id=self.backend_id,
            model_id="model-a-v1",
            output_text=NEW_A,
            metadata={
                "tokens": 123,
            },
        )


class EngineB:

    backend_id = "ENGINE_B"

    def generate_text(
        self,
        prompt,
    ):

        return ToolingBackendResult(
            backend_id=self.backend_id,
            model_id="model-b-v9",
            output_text=NEW_B,
        )


def _make_repo(
    tmp_path: Path,
):

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
        "obsidia-generator@example.invalid",
    )

    _run(
        repo,
        "git",
        "config",
        "user.name",
        "Obsidia Generator",
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
        / "obsidia_demo.py"
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
        "scripts/obsidia_demo.py",
    )

    _run(
        repo,
        "git",
        "commit",
        "-m",
        "base",
    )

    return repo


def test_obsidia_is_visible_generation_producer():

    generator = (
        ObsidiaToolingGenerator(
            backend=EngineA()
        )
    )

    result = generator.generate(
        _request()
    )

    assert (
        result.provider_id
        == PRODUCER_ID
    )

    assert (
        result.model_id
        == "ENGINE_A/model-a-v1"
    )

    assert (
        result.output_text
        == NEW_A
    )


def test_backend_receives_only_canonical_prompt():

    backend = EngineA()

    generator = (
        ObsidiaToolingGenerator(
            backend=backend
        )
    )

    request = _request()

    generator.generate(
        request
    )

    assert (
        backend.prompts
        == [
            request.prompt
        ]
    )


def test_backend_is_interchangeable():

    a = (
        ObsidiaToolingGenerator(
            backend=EngineA()
        )
    )

    b = (
        ObsidiaToolingGenerator(
            backend=EngineB()
        )
    )

    ra = a.generate(
        _request()
    )

    rb = b.generate(
        _request()
    )

    assert (
        ra.provider_id
        == rb.provider_id
        == PRODUCER_ID
    )

    assert (
        ra.model_id
        != rb.model_id
    )

    assert (
        ra.output_text
        == NEW_A
    )

    assert (
        rb.output_text
        == NEW_B
    )


def test_backend_provenance_is_preserved():

    generator = (
        ObsidiaToolingGenerator(
            backend=EngineA()
        )
    )

    generator.generate(
        _request()
    )

    metadata = (
        generator.last_metadata
    )

    assert metadata is not None

    assert (
        metadata[
            "producer_id"
        ]
        == PRODUCER_ID
    )

    assert (
        metadata[
            "backend_id"
        ]
        == "ENGINE_A"
    )

    assert (
        metadata[
            "backend_model_id"
        ]
        == "model-a-v1"
    )

    assert (
        metadata[
            "backend_metadata"
        ][
            "tokens"
        ]
        == 123
    )

    assert (
        metadata[
            "producer_authority"
        ]
        == "NONE"
    )

    assert (
        metadata[
            "backend_authority"
        ]
        == "NONE"
    )

    assert (
        metadata[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )


def test_backend_failure_fails_closed():

    class Broken:

        backend_id = "BROKEN"

        def generate_text(
            self,
            prompt,
        ):
            raise ValueError(
                "boom"
            )

    generator = (
        ObsidiaToolingGenerator(
            backend=Broken()
        )
    )

    with pytest.raises(
        ObsidiaToolingGeneratorError,
        match=(
            "BACKEND_GENERATION_FAILED:"
            "ValueError"
        ),
    ):
        generator.generate(
            _request()
        )


def test_backend_identity_mismatch_fails_closed():

    class Liar:

        backend_id = "DECLARED"

        def generate_text(
            self,
            prompt,
        ):

            return ToolingBackendResult(
                backend_id="OTHER",
                model_id="model",
                output_text=NEW_A,
            )

    generator = (
        ObsidiaToolingGenerator(
            backend=Liar()
        )
    )

    with pytest.raises(
        ObsidiaToolingGeneratorError,
        match="BACKEND_ID_MISMATCH",
    ):
        generator.generate(
            _request()
        )


def test_obsidia_generator_to_c3a_external_artifact(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )

    generator = (
        ObsidiaToolingGenerator(
            backend=EngineA()
        )
    )

    head_before = _run(
        repo,
        "git",
        "rev-parse",
        "HEAD",
    )

    generation = (
        generate_tooling_source(
            repo_root=repo,
            objective=(
                "Obsidia proposes "
                "exact source."
            ),
            target_path=(
                "scripts/obsidia_demo.py"
            ),
            artifact_root=(
                tmp_path
                / "generation"
            ),
            provider=generator,
            generation_id=(
                "obsidia-c3a"
            ),
        )
    )

    artifact = Path(
        generation[
            "source_artifact_path"
        ]
    )

    assert (
        artifact.read_bytes()
        == NEW_A.encode(
            "utf-8"
        )
    )

    assert (
        generation[
            "provider_id"
        ]
        == PRODUCER_ID
    )

    assert (
        generation[
            "model_id"
        ]
        == "ENGINE_A/model-a-v1"
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


def test_obsidia_generator_to_c2_to_build_phase1(
    tmp_path,
):

    repo = _make_repo(
        tmp_path
    )

    objective = (
        "Obsidia generate one "
        "bounded tooling candidate."
    )

    generator = (
        ObsidiaToolingGenerator(
            backend=EngineA()
        )
    )

    generation = (
        generate_tooling_source(
            repo_root=repo,
            objective=objective,
            target_path=(
                "scripts/obsidia_demo.py"
            ),
            artifact_root=(
                tmp_path
                / "generation"
            ),
            provider=generator,
            generation_id=(
                "obsidia-build"
            ),
        )
    )

    candidate = (
        C2.produce_candidate(
            repo,
            objective,
            [
                (
                    "scripts/obsidia_demo.py",
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

    before_worktrees = _run(
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

    after_worktrees = _run(
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
            "scripts/obsidia_demo.py"
        ]
    )

    assert (
        plan[
            "candidate_patch_hash"
        ]
        == candidate.patch_sha256
    )

    assert (
        before_worktrees
        == after_worktrees
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


def test_self_check_zero_authority():

    truth = self_check()

    assert (
        truth[
            "producer_id"
        ]
        == PRODUCER_ID
    )

    assert (
        truth[
            "producer_authority"
        ]
        == "NONE"
    )

    assert (
        truth[
            "backend_authority"
        ]
        == "NONE"
    )

    assert (
        truth[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    for key in (
        "repo_mutation",
        "memory_write",
        "kernel_mutation",
        "emits_act",
        "auto_apply",
        "auto_commit",
        "push",
        "merge",
        "kx108_invoked",
        "world_action",
    ):

        assert (
            truth[key]
            is False
        )


def test_generator_ast_has_no_mutation_tool_imports():

    path = (
        ROOT
        / "scripts"
        / "providers"
        / "obsidia_tooling_generator_v1.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    imported = set()

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                imported.add(
                    alias.name.split(
                        "."
                    )[0]
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:

                imported.add(
                    node.module.split(
                        "."
                    )[0]
                )

    assert (
        "subprocess"
        not in imported
    )

    assert (
        "pathlib"
        not in imported
    )

    assert (
        "urllib"
        not in imported
    )

    assert (
        "requests"
        not in imported
    )

    assert (
        "anthropic"
        not in imported
    )

    assert (
        "openai"
        not in imported
    )
