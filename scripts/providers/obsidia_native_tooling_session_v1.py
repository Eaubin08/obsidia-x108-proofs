"""
R8-C3b4 — Obsidia Native Tooling Session V1.

Bounded orchestration for multiple exact tooling targets.

For each target:

    exact repo source
        -> C3a request
        -> Obsidia Native Solve Stack
        -> external generated source artifact

Then:

    all generated artifacts
        -> C2 REAL_UNIFIED_DIFF_V1 candidate
        -> Build Phase1 PLAN_PROPOSED

No Phase2.
No HumanApproval synthesis.
No apply.
No commit.
No push.
No merge.
No WorldAction.
"""

from __future__ import annotations

import json
import re

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from scripts.providers.obsidia_native_solve_stack_v1 import (
    ObsidiaNativeSolveStack,
)

from scripts.providers.tooling_generation_adapter_v1 import (
    generate_tooling_source,
)

from scripts import (
    obsidure_tooling_candidate_v1 as C2,
)


SESSION_ID = (
    "OBSIDIA_NATIVE_TOOLING_SESSION_V1"
)


class ObsidiaNativeSessionError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True
)
class NativeToolingTarget:

    target_path: str
    objective: str


def _validate_session_id(
    session_id: str,
) -> str:

    value = str(
        session_id
        or ""
    ).strip()


    if not re.fullmatch(
        r"[A-Za-z0-9_.-]{1,80}",
        value,
    ):

        raise ObsidiaNativeSessionError(
            "SESSION_ID_INVALID"
        )


    return value


def run_native_multi_target_phase1(
    *,
    repo_root: Path,
    targets: Sequence[
        NativeToolingTarget
    ],
    artifact_root: Path,
    session_id: str,
) -> dict[str, Any]:

    repo = Path(
        repo_root
    ).resolve()

    root = Path(
        artifact_root
    ).resolve()

    sid = _validate_session_id(
        session_id
    )


    if root.is_relative_to(
        repo
    ):

        raise ObsidiaNativeSessionError(
            "SESSION_ARTIFACT_ROOT_INSIDE_REPO"
        )


    items = list(
        targets
    )


    if (
        not items
        or len(items) > 8
    ):

        raise ObsidiaNativeSessionError(
            "SESSION_TARGET_COUNT_INVALID"
        )


    paths = [
        item.target_path
        for item in items
    ]


    if len(
        set(paths)
    ) != len(
        paths
    ):

        raise ObsidiaNativeSessionError(
            "SESSION_DUPLICATE_TARGET"
        )


    generations: list[
        dict[str, Any]
    ] = []

    candidate_inputs = []


    for index, item in enumerate(
        items,
        start=1,
    ):

        if not isinstance(
            item.objective,
            str,
        ) or not item.objective.strip():

            raise ObsidiaNativeSessionError(
                "SESSION_OBJECTIVE_REQUIRED"
            )


        stack = (
            ObsidiaNativeSolveStack()
        )


        generation = (
            generate_tooling_source(
                repo_root=repo,
                objective=(
                    item.objective
                ),
                target_path=(
                    item.target_path
                ),
                artifact_root=(
                    root
                    / "generation"
                    / str(index)
                ),
                provider=stack,
                generation_id=(
                    sid
                    + "-"
                    + str(index)
                ),
            )
        )


        artifact = Path(
            generation[
                "source_artifact_path"
            ]
        ).resolve()


        if artifact.is_relative_to(
            repo
        ):

            raise ObsidiaNativeSessionError(
                "SESSION_GENERATED_ARTIFACT_INSIDE_REPO"
            )


        candidate_inputs.append(
            (
                item.target_path,
                artifact,
            )
        )


        generations.append(
            {
                "target_path": (
                    item.target_path
                ),
                "provider_id": (
                    generation[
                        "provider_id"
                    ]
                ),
                "model_id": (
                    generation[
                        "model_id"
                    ]
                ),
                "source_sha256": (
                    generation[
                        "source_sha256"
                    ]
                ),
                "source_artifact_path": (
                    str(
                        artifact
                    )
                ),
                "solve_attempts": list(
                    (
                        stack.last_metadata
                        or {}
                    ).get(
                        "solve_attempts",
                        []
                    )
                ),
            }
        )


    candidate_objective = (
        "OBSIDIA_NATIVE_MULTI_TARGET_V1\n"
        + json.dumps(
            {
                "session_id": sid,
                "targets": [
                    {
                        "target_path": (
                            item.target_path
                        ),
                        "objective": (
                            item.objective
                        ),
                    }
                    for item in items
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


    candidate = (
        C2.produce_candidate(
            repo,
            candidate_objective,
            candidate_inputs,
            root
            / "candidate",
        )
    )


    plan = (
        C2.build_phase1_plan(
            repo,
            candidate,
        )
    )


    return {
        "session_id": sid,
        "session_contract": (
            SESSION_ID
        ),
        "status": (
            plan.get(
                "status"
            )
        ),
        "targets": paths,
        "generations": generations,
        "candidate_patch_hash": (
            candidate.patch_sha256
        ),
        "candidate_files": list(
            candidate.files
        ),
        "plan": plan,
        "producer_authority": (
            "NONE"
        ),
        "backend_authority": (
            "NONE"
        ),
        "decision_authority": (
            "KX108_ONLY"
        ),
        "phase2_executed": False,
        "human_approval_synthesized": False,
        "repo_mutation": False,
        "world_action": False,
    }


def self_check() -> dict[str, Any]:

    return {
        "session_contract": (
            SESSION_ID
        ),
        "max_targets": 8,
        "phase1_only": True,
        "human_approval_synthesized": False,
        "auto_apply": False,
        "auto_commit": False,
        "push": False,
        "merge": False,
        "world_action": False,
        "decision_authority": (
            "KX108_ONLY"
        ),
    }
