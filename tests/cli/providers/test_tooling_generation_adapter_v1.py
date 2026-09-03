from __future__ import annotations

import hashlib
import json
import subprocess

from pathlib import Path

import pytest

from scripts.providers.tooling_generation_adapter_v1 import (
    MAX_SOURCE_BYTES,
    ToolingGenerationError,
    generate_tooling_source,
)

from scripts.providers.tooling_generation_contract_v1 import (
    TOOLING_GENERATION_MODE,
    ToolingGenerationProviderResult,
)


OLD_SOURCE = 'VALUE = "old"\n'
NEW_SOURCE = 'VALUE = "new"\n'


def _run(
    cwd: Path,
    *args: str,
) -> str:
    proc = subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    if proc.returncode != 0:
        raise AssertionError(
            f"command failed: {args}\n"
            f"stdout={proc.stdout}\n"
            f"stderr={proc.stderr}"
        )

    return proc.stdout.strip()


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
        "r8-c3a@example.invalid",
    )

    _run(
        repo,
        "git",
        "config",
        "user.name",
        "R8 C3a",
    )

    _run(
        repo,
        "git",
        "config",
        "core.autocrlf",
        "false",
    )

    target = repo / "scripts" / "demo.py"
    target.parent.mkdir(
        parents=True
    )

    target.write_text(
        OLD_SOURCE,
        encoding="utf-8",
    )

    _run(
        repo,
        "git",
        "add",
        "scripts/demo.py",
    )

    _run(
        repo,
        "git",
        "commit",
        "-m",
        "baseline",
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

    return repo


class FakeProvider:
    def __init__(
        self,
        output: str = NEW_SOURCE,
        provider_id: str = "fake-generation-provider",
        model_id: str = "fake-model-v1",
    ):
        self.output = output
        self.provider_id = provider_id
        self.model_id = model_id
        self.last_request = None

    def generate(
        self,
        request,
    ):
        self.last_request = request

        return ToolingGenerationProviderResult(
            provider_id=self.provider_id,
            model_id=self.model_id,
            output_text=self.output,
        )


def _sha(
    data: bytes,
) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def test_generation_creates_only_external_artifacts(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    artifact_root = (
        tmp_path
        / "external-artifacts"
    )

    provider = FakeProvider()

    head_before = _run(
        repo,
        "git",
        "rev-parse",
        "HEAD",
    )

    result = generate_tooling_source(
        repo_root=repo,
        objective=(
            "Change VALUE from old to new "
            "without any repository mutation."
        ),
        target_path="scripts/demo.py",
        artifact_root=artifact_root,
        provider=provider,
        generation_id="c3a-test-generation",
    )

    head_after = _run(
        repo,
        "git",
        "rev-parse",
        "HEAD",
    )

    status_after = _run(
        repo,
        "git",
        "status",
        "--porcelain=v1",
    )

    assert head_after == head_before
    assert status_after == ""

    assert (
        repo
        / "scripts"
        / "demo.py"
    ).read_text(
        encoding="utf-8"
    ) == OLD_SOURCE

    source_path = Path(
        result[
            "source_artifact_path"
        ]
    )

    receipt_path = Path(
        result[
            "generation_receipt_path"
        ]
    )

    assert source_path.exists()
    assert receipt_path.exists()

    assert (
        source_path.read_text(
            encoding="utf-8"
        )
        == NEW_SOURCE
    )

    assert not source_path.is_relative_to(
        repo
    )

    assert not receipt_path.is_relative_to(
        repo
    )


def test_receipt_binds_exact_hashes_and_provider_identity(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    provider = FakeProvider(
        provider_id="provider-proof-id",
        model_id="model-proof-id",
    )

    result = generate_tooling_source(
        repo_root=repo,
        objective="Exact hash proof",
        target_path="scripts/demo.py",
        artifact_root=tmp_path / "artifacts",
        provider=provider,
        generation_id="hash-proof",
    )

    receipt = json.loads(
        Path(
            result[
                "generation_receipt_path"
            ]
        ).read_text(
            encoding="utf-8"
        )
    )

    generated_bytes = NEW_SOURCE.encode(
        "utf-8"
    )

    assert (
        receipt["mode"]
        == TOOLING_GENERATION_MODE
    )

    assert (
        receipt["provider_id"]
        == "provider-proof-id"
    )

    assert (
        receipt["model_id"]
        == "model-proof-id"
    )

    assert (
        receipt[
            "target_before_sha256"
        ]
        == _sha(
            OLD_SOURCE.encode("utf-8")
        )
    )

    assert (
        receipt["source_sha256"]
        == _sha(generated_bytes)
    )

    assert (
        receipt[
            "raw_response_sha256"
        ]
        == _sha(generated_bytes)
    )

    assert (
        receipt["source_bytes"]
        == len(generated_bytes)
    )

    assert (
        receipt["base_sha"]
        == _run(
            repo,
            "git",
            "rev-parse",
            "HEAD",
        )
    )


def test_prompt_is_canonical_and_hash_bound(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    provider = FakeProvider()

    result = generate_tooling_source(
        repo_root=repo,
        objective="Canonical prompt proof",
        target_path="scripts/demo.py",
        artifact_root=tmp_path / "artifacts",
        provider=provider,
        generation_id="prompt-proof",
    )

    req = provider.last_request

    assert req is not None

    assert (
        hashlib.sha256(
            req.prompt.encode("utf-8")
        ).hexdigest()
        == req.prompt_sha256
        == result["prompt_sha256"]
    )

    payload = json.loads(
        req.prompt
    )

    assert (
        payload["objective"]
        == "Canonical prompt proof"
    )

    assert (
        payload["target_path"]
        == "scripts/demo.py"
    )

    assert (
        payload["current_source"]
        == OLD_SOURCE
    )

    assert (
        payload["boundary"][
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        payload["boundary"][
            "apply"
        ]
        is False
    )

    assert (
        payload["boundary"][
            "world_action"
        ]
        is False
    )


def test_artifact_root_inside_repo_rejected(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    with pytest.raises(
        ToolingGenerationError,
        match=(
            "ARTIFACT_ROOT_INSIDE_REPO_REJECTED"
        ),
    ):
        generate_tooling_source(
            repo_root=repo,
            objective="reject inside repo",
            target_path="scripts/demo.py",
            artifact_root=(
                repo
                / "_GENERATION_ARTIFACTS"
            ),
            provider=FakeProvider(),
        )


@pytest.mark.parametrize(
    "target",
    [
        "../outside.py",
        "/absolute.py",
        r"C:\absolute.py",
        r"scripts\demo.py",
        "missing.py",
    ],
)
def test_invalid_target_rejected(
    tmp_path,
    target,
):
    repo = _make_repo(
        tmp_path
    )

    with pytest.raises(
        ToolingGenerationError,
    ):
        generate_tooling_source(
            repo_root=repo,
            objective="invalid target",
            target_path=target,
            artifact_root=(
                tmp_path
                / "artifacts"
            ),
            provider=FakeProvider(),
        )


@pytest.mark.parametrize(
    "output,reason",
    [
        (
            "",
            "PROVIDER_OUTPUT_EMPTY",
        ),
        (
            "```python\nVALUE = 1\n```\n",
            "PROVIDER_OUTPUT_MARKDOWN_FENCE_REJECTED",
        ),
        (
            "X" * (MAX_SOURCE_BYTES + 1),
            "PROVIDER_OUTPUT_TOO_LARGE",
        ),
    ],
)
def test_invalid_provider_output_rejected(
    tmp_path,
    output,
    reason,
):
    repo = _make_repo(
        tmp_path
    )

    with pytest.raises(
        ToolingGenerationError,
        match=reason,
    ):
        generate_tooling_source(
            repo_root=repo,
            objective="invalid provider output",
            target_path="scripts/demo.py",
            artifact_root=(
                tmp_path
                / "artifacts"
            ),
            provider=FakeProvider(
                output=output
            ),
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


class MutatingProvider:
    def __init__(
        self,
        repo: Path,
    ):
        self.repo = repo

    def generate(
        self,
        request,
    ):
        (
            self.repo
            / "scripts"
            / "demo.py"
        ).write_text(
            'VALUE = "MUTATED"\n',
            encoding="utf-8",
        )

        return ToolingGenerationProviderResult(
            provider_id="malicious-test-provider",
            model_id="malicious-test-model",
            output_text=NEW_SOURCE,
        )


def test_provider_repo_mutation_is_detected(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    with pytest.raises(
        ToolingGenerationError,
        match="REPO_STATUS_MUTATED_DURING_PROVIDER_CALL",
    ):
        generate_tooling_source(
            repo_root=repo,
            objective="mutation must be detected",
            target_path="scripts/demo.py",
            artifact_root=(
                tmp_path
                / "artifacts"
            ),
            provider=MutatingProvider(
                repo
            ),
        )


def test_receipt_has_zero_nonsovereign_authority(
    tmp_path,
):
    repo = _make_repo(
        tmp_path
    )

    result = generate_tooling_source(
        repo_root=repo,
        objective="authority proof",
        target_path="scripts/demo.py",
        artifact_root=tmp_path / "artifacts",
        provider=FakeProvider(),
        generation_id="authority-proof",
    )

    receipt = json.loads(
        Path(
            result[
                "generation_receipt_path"
            ]
        ).read_text(
            encoding="utf-8"
        )
    )

    assert (
        receipt[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        receipt[
            "generation_authority"
        ]
        == "NONE"
    )

    for key in (
        "provider_is_authority",
        "can_decide",
        "execution_authority",
        "memory_write",
        "kernel_mutation",
        "emits_act",
        "auto_apply",
        "auto_commit",
        "push",
        "merge",
        "world_action",
        "kx108_invoked",
        "candidate_patch_created",
    ):
        assert receipt[key] is False


def test_adapter_source_has_no_network_or_mutation_command(
):
    path = (
        Path(__file__)
        .resolve()
        .parents[3]
        / "scripts"
        / "providers"
        / "tooling_generation_adapter_v1.py"
    )

    source = path.read_text(
        encoding="utf-8"
    ).lower()

    for forbidden in (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import urllib",
        "from urllib",
        "import anthropic",
        "from anthropic",
        "import openai",
        "from openai",
        "git apply",
        "git commit",
        "git push",
        "git merge",
        "_call_kx108",
        "guardx108",
    ):
        assert forbidden not in source