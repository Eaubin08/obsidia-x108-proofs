"""
J9-B5 ? candidate -> governed human checkpoint.

Composition-only seam.

    Obsidure candidate.patch
        -> J9-B4 immutable Git source
        -> canonical isolated worktree
        -> obsidia_test_contract
        -> J3 readonly proposal
        -> Relay J6 PREPARE
        -> exact EAH + HOLD

This module owns NO execution authority.

It does NOT:
- create HumanApproval;
- call KX108;
- execute J5;
- mutate the target;
- commit/push/merge/rebase;
- auto-authorize;
- interpret natural-language approval.

decision_authority = KX108_ONLY.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
from typing import Any

try:
    from scripts import (
        obsidia_cognitive_governed_runtime_handoff_v0 as _J3,
    )
    from scripts import (
        obsidia_isolated_work_unit_v0 as _WU,
    )
    from scripts import (
        obsidia_jarvis_candidate_materializer_v0 as _MAT,
    )
    from scripts import (
        obsidia_jarvis_governed_mutation_v0 as _J5,
    )
    from scripts import (
        obsidia_relay_v0 as _RELAY,
    )
    from scripts import (
        obsidia_test_contract as _TC,
    )
except ImportError:
    import obsidia_cognitive_governed_runtime_handoff_v0 as _J3
    import obsidia_isolated_work_unit_v0 as _WU
    import obsidia_jarvis_candidate_materializer_v0 as _MAT
    import obsidia_jarvis_governed_mutation_v0 as _J5
    import obsidia_relay_v0 as _RELAY
    import obsidia_test_contract as _TC


SCHEMA_VERSION = (
    "OBSIDIA_JARVIS_GOVERNED_PREPARE_BUILDER_V0"
)

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

AUTO_EXECUTE = False
AUTO_AUTHORIZE = False
AUTO_COMMIT = False
AUTO_PUSH = False
AUTO_MERGE = False


class GovernedPrepareBuilderError(
    RuntimeError
):
    pass


def _sha(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _git(
    repo_root: Path,
    *args: str,
) -> str:
    proc = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    if proc.returncode != 0:
        raise GovernedPrepareBuilderError(
            "GIT_COMMAND_FAILED:"
            + " ".join(args[:2])
            + ":"
            + proc.stderr.strip()
        )

    return proc.stdout.strip()


def _require_clean(
    repo_root: Path,
) -> None:
    status = _git(
        repo_root,
        "status",
        "--porcelain",
    )

    if status:
        raise GovernedPrepareBuilderError(
            "MAIN_WORKTREE_MUST_BE_CLEAN"
        )


def _outside_repo(
    repo_root: Path,
    path: Path,
) -> bool:
    try:
        path.resolve().relative_to(
            repo_root.resolve()
        )

        return False
    except ValueError:
        return True


def _runtime_dirs(
    root: Path,
) -> dict[str, Path]:
    names = (
        "ledger",
        "selector",
        "execution",
        "pre_execution_context",
    )

    out = {
        name: root / name
        for name in names
    }

    for path in out.values():
        path.mkdir(
            parents=True,
            exist_ok=True,
        )

    return out


def _build_test_contract(
    *,
    target_path: str,
    expected_target_sha256: str,
    candidate_id: str,
    batch_id: str,
) -> dict[str, Any]:
    """
    Generic J9 contract:
    - final target bytes must equal immutable candidate bytes;
    - exact Git diff scope must remain the one target.

    Domain-specific tests can be added later by higher layers,
    but these two checks are always required.
    """
    checks = [
        _TC.build_check(
            "j9-target-sha256",
            _TC.CHECK_TYPE_TARGET_SHA256,
            target_path=target_path,
            expected_target_sha256=(
                expected_target_sha256
            ),
        ),
        _TC.build_check(
            "j9-diff-scope",
            _TC.CHECK_TYPE_DIFF_SCOPE,
            expected_diff_paths=[
                target_path
            ],
        ),
    ]

    return _TC.build_test_contract(
        (
            "j9b5-contract-"
            + candidate_id
        ),
        (
            "j9b5-candidate-"
            + candidate_id
        ),
        batch_id,
        target_path,
        checks,
    )


def prepare_governed_candidate(
    *,
    repo_root: str | Path,
    candidate_patch_path: str | Path,
    requested_outcome: str,
    relay_store_dir: str | Path,
    runtime_root: str | Path,
    operation_key: str,
) -> dict[str, Any]:
    """
    PREPARE ONLY.

    Successful return means:
      Relay J6 == MISSION_HOLD
      exact EAH revealed
      no target mutation
      no KX108
      no HumanApproval
      isolated worktree remains alive for J7/J5.
    """
    repo = Path(
        repo_root
    ).resolve()

    patch = Path(
        candidate_patch_path
    ).expanduser().resolve()

    relay_store = Path(
        relay_store_dir
    ).resolve()

    runtime = Path(
        runtime_root
    ).resolve()

    objective = str(
        requested_outcome or ""
    ).strip()

    op_key = str(
        operation_key or ""
    ).strip()

    if not repo.is_dir():
        raise GovernedPrepareBuilderError(
            "REPO_ROOT_NOT_FOUND"
        )

    if not patch.is_file():
        raise GovernedPrepareBuilderError(
            "CANDIDATE_PATCH_NOT_FOUND"
        )

    if not objective:
        raise GovernedPrepareBuilderError(
            "REQUESTED_OUTCOME_REQUIRED"
        )

    if not op_key:
        raise GovernedPrepareBuilderError(
            "OPERATION_KEY_REQUIRED"
        )

    if not _outside_repo(
        repo,
        runtime,
    ):
        raise GovernedPrepareBuilderError(
            "RUNTIME_ROOT_MUST_BE_OUTSIDE_REPO"
        )

    _require_clean(
        repo
    )

    base_sha = _git(
        repo,
        "rev-parse",
        "HEAD",
    )

    materialized = (
        _MAT.materialize_candidate_patch(
            repo_root=repo,
            candidate_patch_path=patch,
            base_sha=base_sha,
        )
    )

    identity_seed = "|".join(
        [
            op_key,
            base_sha,
            materialized.candidate_patch_sha256,
            materialized.target_path,
        ]
    )

    short = _sha(
        identity_seed
    )[:16]

    work_unit_id = (
        "j9b5-wu-"
        + short
    )

    branch_name = (
        "jarvis/j9b5-"
        + short
    )

    worktree_path = (
        runtime
        / (
            "worktree-"
            + short
        )
    )

    stores_root = (
        runtime
        / (
            "stores-"
            + short
        )
    )

    dirs = _runtime_dirs(
        stores_root
    )

    created = (
        _WU.create_isolated_work_unit(
            repo_root=repo,
            base_sha=base_sha,
            branch_name=branch_name,
            worktree_path=worktree_path,
            work_unit_id=work_unit_id,
            main_worktree_path=repo,
        )
    )

    if (
        created.get("status")
        != _WU.WORK_UNIT_CREATED
    ):
        raise GovernedPrepareBuilderError(
            "WORK_UNIT_CREATE_FAILED:"
            + str(
                created.get(
                    "reason"
                )
            )
        )

    work_unit = created[
        "work_unit"
    ]

    candidate_id = (
        materialized
        .candidate_patch_sha256[:16]
    )

    batch_id = (
        "j9b5-batch-"
        + short
    )

    contract = (
        _build_test_contract(
            target_path=(
                materialized.target_path
            ),
            expected_target_sha256=(
                materialized
                .source_content_sha256
            ),
            candidate_id=candidate_id,
            batch_id=batch_id,
        )
    )

    proposal = (
        _J3.prepare_cognitive_governed_handoff(
            mission_id=(
                "j9b5-mission-"
                + short
            ),
            provider_id=(
                "obsidure-candidate-materializer"
            ),
            capability=(
                _J5.CAPABILITY_ID
            ),
            payload={
                "source_git_commit":
                    materialized
                    .source_git_commit,
                "source_historical_path":
                    materialized
                    .source_historical_path,
                "target_path":
                    materialized.target_path,
                "test_contract":
                    contract,
                "objective":
                    objective,
            },
            domain=(
                "JARVIS_OPENJARVIS"
            ),
            action_id=(
                "j9b5-action-"
                + short
            ),
            intent=objective,
            action_type=(
                _J5.ACTION_TYPE
            ),
            c1_provenance={
                "source":
                    "J9_B5_OBSIDURE_CANDIDATE",
                "candidate_patch_sha256":
                    materialized
                    .candidate_patch_sha256,
                "source_git_commit":
                    materialized
                    .source_git_commit,
                "work_unit_id":
                    work_unit_id,
                "authority":
                    "NONE",
            },
            irreversible=False,
        )
    )

    request = {
        "proposal":
            proposal,
        "execution_worktree_path":
            str(
                Path(
                    work_unit.worktree_path
                ).resolve()
            ),
        "main_worktree_path":
            str(repo),
        "branch_name":
            work_unit.branch_name,
        "base_sha":
            base_sha,
        "ledger_dir":
            str(
                dirs["ledger"]
            ),
        "selector_dir":
            str(
                dirs["selector"]
            ),
        "execution_dir":
            str(
                dirs["execution"]
            ),
        "pre_execution_context_dir":
            str(
                dirs[
                    "pre_execution_context"
                ]
            ),
        "repository_identity":
            str(
                Path(
                    work_unit.worktree_path
                ).resolve()
            ),
    }

    try:
        relay = (
            _RELAY.relay_submit_mission(
                requested_outcome=(
                    objective
                ),
                mission_kind=(
                    _RELAY
                    .KIND_GOVERNED_UPDATE
                ),
                target=(
                    materialized
                    .target_path
                ),
                store_dir=(
                    relay_store
                ),
                governed_update_request=(
                    request
                ),
            )
        )
    except Exception as exc:
        cleanup = (
            _WU.dispose_isolated_work_unit(
                work_unit=work_unit,
                require_branch_disposition_done=(
                    False
                ),
            )
        )

        raise GovernedPrepareBuilderError(
            "RELAY_PREPARE_EXCEPTION:"
            + type(exc).__name__
            + ":cleanup="
            + str(
                cleanup.get(
                    "status"
                )
            )
        ) from exc

    valid_hold = (
        relay.get("mission_state")
        == _RELAY.MISSION_HOLD
        and relay.get("hold_reason")
        == (
            "HUMAN_EAH_"
            "AUTHORIZATION_REQUIRED"
        )
        and relay.get(
            "governed_prepare_only"
        )
        is True
        and relay.get(
            "governed_auto_execute"
        )
        is False
        and relay.get(
            "target_mutated"
        )
        is False
        and relay.get(
            "kx108_invocations"
        )
        == 0
        and relay.get(
            "human_approval_created"
        )
        is False
        and relay.get(
            "human_authorization_consumed"
        )
        is False
    )

    eah = relay.get(
        "execution_authority_hash"
    )

    valid_eah = (
        isinstance(eah, str)
        and len(eah) == 64
        and all(
            c
            in (
                "0123456789"
                "abcdefABCDEF"
            )
            for c in eah
        )
    )

    if not (
        valid_hold
        and valid_eah
    ):
        cleanup = (
            _WU.dispose_isolated_work_unit(
                work_unit=work_unit,
                require_branch_disposition_done=(
                    False
                ),
            )
        )

        return {
            "status":
                "J9_B5_PREPARE_REJECTED",
            "reason":
                "RELAY_DID_NOT_REACH_VALID_HOLD",
            "relay_result":
                relay,
            "cleanup":
                cleanup,
            "authority":
                AUTHORITY,
            "decision_authority":
                DECISION_AUTHORITY,
        }

    return {
        "status":
            "J9_B5_PREPARED_AWAITING_HUMAN_EAH",
        "relay_result":
            relay,
        "work_unit":
            work_unit,
        "work_unit_id":
            work_unit_id,
        "execution_worktree_path":
            str(
                Path(
                    work_unit.worktree_path
                ).resolve()
            ),
        "branch_name":
            work_unit.branch_name,
        "base_sha":
            base_sha,
        "target_path":
            materialized.target_path,
        "source_git_commit":
            materialized.source_git_commit,
        "source_historical_path":
            materialized.source_historical_path,
        "source_content_sha256":
            materialized.source_content_sha256,
        "candidate_patch_sha256":
            materialized.candidate_patch_sha256,
        "test_contract":
            contract,
        "proposal":
            proposal,
        "governed_update_request":
            request,
        "authority":
            AUTHORITY,
        "decision_authority":
            DECISION_AUTHORITY,
        "target_mutated":
            False,
        "kx108_invocations":
            0,
        "human_approval_created":
            False,
        "human_authorization_consumed":
            False,
        "auto_execute":
            False,
        "auto_authorize":
            False,
    }
