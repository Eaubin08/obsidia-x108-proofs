"""
R8-C1 — Obsidure proposal -> candidate.patch -> Build Phase 1.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(
    __file__
).resolve().parents[1]

SCRIPTS = (
    ROOT
    / "scripts"
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import obsidure_candidate_export_v1 as C


def git(
    repo: Path,
    *args: str,
) -> str:

    proc = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    return proc.stdout.strip()


def make_repo(
    tmp_path: Path,
) -> Path:

    repo = (
        tmp_path
        / "repo"
    )

    repo.mkdir()

    git(
        repo,
        "init",
    )

    # Force explicit Windows-style checkout semantics even when
    # this test runs on a non-Windows host.
    git(
        repo,
        "config",
        "core.autocrlf",
        "true",
    )

    target = (
        repo
        / "periphery"
        / "demo.py"
    )

    target.parent.mkdir(
        parents=True
    )

    # Physical worktree = CRLF.
    # Git index/blob = canonical LF because core.autocrlf=true.
    target.write_bytes(
        b'VALUE = "old"\r\n'
    )

    git(
        repo,
        "add",
        ".",
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Obsidia Test",
            "-c",
            "user.email=obsidia@test.local",
            "commit",
            "-m",
            "base",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    return repo


def make_proposal(
    tmp_path: Path,
    *,
    target: str = "periphery/demo.py",
    content: str = 'VALUE = "new"\n',
    human_approved: bool = False,
):

    proposal_dir = (
        tmp_path
        / "proposal"
    )

    proposal_dir.mkdir(
        exist_ok=True
    )

    sandbox = (
        tmp_path
        / "sandbox.py"
    )

    sandbox.write_text(
        content,
        encoding="utf-8",
    )

    proposal = {
        "proposal_id": "proposal-r8c1",
        "objective": (
            "change demo value"
        ),
        "human_approved": (
            human_approved
        ),
        "status": (
            "PROPOSED"
        ),
        "patches": [
            {
                "path": target,
                "sandbox_path": (
                    str(
                        sandbox
                    )
                ),
            }
        ],
    }

    proposal_json = (
        proposal_dir
        / "proposal.json"
    )

    proposal_json.write_text(
        json.dumps(
            proposal
        ),
        encoding="utf-8",
    )

    return proposal_json


def test_export_real_candidate_exact_hash(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path
    )

    output = (
        tmp_path
        / "outside"
    )

    artifact = (
        C.export_proposal_candidate(
            repo,
            proposal,
            output,
        )
    )

    raw = (
        artifact
        .patch_path
        .read_bytes()
    )

    assert (
        hashlib.sha256(
            raw
        ).hexdigest()
        == artifact.patch_sha256
    )

    assert artifact.files == (
        "periphery/demo.py",
    )

    text = raw.decode(
        "utf-8"
    )

    assert (
        '-VALUE = "old"'
        in text
    )

    assert (
        '+VALUE = "new"'
        in text
    )


def test_build_phase1_is_explicit_scope(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path
    )

    artifact = (
        C.export_proposal_candidate(
            repo,
            proposal,
            tmp_path
            / "outside",
        )
    )

    before = git(
        repo,
        "worktree",
        "list",
        "--porcelain",
    )

    plan = C.build_phase1_plan(
        repo,
        "R8-C1 bridge proof",
        artifact,
    )

    after = git(
        repo,
        "worktree",
        "list",
        "--porcelain",
    )

    assert (
        plan["status"]
        == "PLAN_PROPOSED"
    )

    assert (
        plan["scope_mode"]
        == "EXPLICIT_CHILD_TARGET"
    )

    assert (
        plan[
            "approved_scope_proposal"
        ]
        == [
            "periphery/demo.py"
        ]
    )

    assert (
        plan[
            "candidate_patch_mode"
        ]
        == "REAL_UNIFIED_DIFF_V1"
    )

    assert (
        plan[
            "candidate_patch_hash"
        ]
        == artifact.patch_sha256
    )

    assert before == after


def test_candidate_content_changes_plan_identity(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal1 = make_proposal(
        tmp_path,
        content='VALUE = "new-a"\n',
    )

    a = C.export_proposal_candidate(
        repo,
        proposal1,
        tmp_path
        / "outside-a",
    )

    plan_a = C.build_phase1_plan(
        repo,
        "same objective",
        a,
    )

    proposal2_dir = (
        tmp_path
        / "proposal2"
    )

    proposal2_dir.mkdir()

    sandbox2 = (
        tmp_path
        / "sandbox2.py"
    )

    sandbox2.write_text(
        'VALUE = "new-b"\n',
        encoding="utf-8",
    )

    proposal2 = (
        proposal2_dir
        / "proposal.json"
    )

    proposal2.write_text(
        json.dumps(
            {
                "proposal_id": (
                    "proposal-r8c1-b"
                ),
                "objective": (
                    "same objective"
                ),
                "human_approved": (
                    False
                ),
                "status": (
                    "PROPOSED"
                ),
                "patches": [
                    {
                        "path": (
                            "periphery/demo.py"
                        ),
                        "sandbox_path": (
                            str(
                                sandbox2
                            )
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    b = C.export_proposal_candidate(
        repo,
        proposal2,
        tmp_path
        / "outside-b",
    )

    plan_b = C.build_phase1_plan(
        repo,
        "same objective",
        b,
    )

    assert (
        a.patch_sha256
        != b.patch_sha256
    )

    assert (
        plan_a["session_id"]
        != plan_b["session_id"]
    )

    assert (
        plan_a[
            "next_human_action"
        ]
        != plan_b[
            "next_human_action"
        ]
    )


def test_scripts_target_rejected_in_r8c1(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path,
        target=(
            "scripts/obsidia_build.py"
        ),
    )

    with pytest.raises(
        C.CandidateExportError,
        match="R8C1_PERIPHERY_ONLY",
    ):
        C.export_proposal_candidate(
            repo,
            proposal,
            tmp_path
            / "outside",
        )


def test_new_file_rejected_modification_only(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path,
        target=(
            "periphery/new_file.py"
        ),
    )

    with pytest.raises(
        C.CandidateExportError,
        match="R8C1_MODIFICATION_ONLY",
    ):
        C.export_proposal_candidate(
            repo,
            proposal,
            tmp_path
            / "outside",
        )


def test_applied_proposal_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path,
        human_approved=True,
    )

    with pytest.raises(
        C.CandidateExportError,
        match=(
            "ALREADY_HUMAN_APPROVED"
        ),
    ):
        C.export_proposal_candidate(
            repo,
            proposal,
            tmp_path
            / "outside",
        )


def test_artifact_inside_repo_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    proposal = make_proposal(
        tmp_path
    )

    with pytest.raises(
        C.CandidateExportError,
        match=(
            "MUST_BE_OUTSIDE_REPO"
        ),
    ):
        C.export_proposal_candidate(
            repo,
            proposal,
            repo
            / "candidate_artifacts",
        )


def test_self_check_non_sovereign():

    truth = C.self_check()

    assert (
        truth[
            "producer_authority"
        ]
        == "NONE"
    )

    assert (
        truth[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        truth["auto_apply"]
        is False
    )

    assert (
        truth["auto_commit"]
        is False
    )

    assert (
        truth["auto_push"]
        is False
    )

    assert (
        truth["auto_merge"]
        is False
    )

    assert (
        truth["world_action"]
        is False
    )

    assert (
        truth["allowed_surface"]
        == "periphery/*"
    )

    assert (
        truth["r8c_status"]
        == (
            "C1_ADAPTER_ONLY_NOT_TOOLING_ENGINEERING"
        )
    )
