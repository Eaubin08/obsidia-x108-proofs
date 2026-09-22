"""
Obsidure Native Repair Proposal V1.

NativePlan
    -> in-memory execution
    -> candidate sources
    -> canonical RepairProposal

No repository write.
No commit.
No push.
No canonical mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from pathlib import Path, PurePosixPath
from typing import Any

from periphery.agents.obsidure_native_plan import (
    NativePlan,
    NativePlanStep,
)

from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)

from periphery.agents.obsidure_repair_contract import (
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
)


BUILDER_ID = "OBSIDURE_NATIVE_REPAIR_PROPOSAL_V1"


@dataclass
class NativeRepairProposalBuildResult:
    status: str

    proposal: RepairProposal | None = None

    execution: dict[str, Any] = field(
        default_factory=dict
    )

    errors: list[str] = field(
        default_factory=list
    )

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    repository_write: bool = False
    auto_apply: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:

        data = asdict(self)

        if self.proposal is not None:
            data["proposal"] = (
                self.proposal.to_dict()
            )

        return data


def _plan_from_dict(
    raw: dict[str, Any],
) -> NativePlan:

    steps: list[NativePlanStep] = []

    for item in (
        raw.get("steps")
        or []
    ):

        if not isinstance(
            item,
            dict,
        ):
            raise ValueError(
                "NATIVE_PLAN_STEP_NOT_OBJECT"
            )

        steps.append(
            NativePlanStep(
                step_id=str(
                    item.get(
                        "step_id",
                        "",
                    )
                    or ""
                ),
                primitive=str(
                    item.get(
                        "primitive",
                        "",
                    )
                    or ""
                ),
                target_path=str(
                    item.get(
                        "target_path",
                        "",
                    )
                    or ""
                ),
                rationale=str(
                    item.get(
                        "rationale",
                        "",
                    )
                    or ""
                ),
                parameters=dict(
                    item.get(
                        "parameters",
                        {},
                    )
                    or {}
                ),
                depends_on=tuple(
                    item.get(
                        "depends_on",
                        (),
                    )
                    or ()
                ),
                execution_ready=bool(
                    item.get(
                        "execution_ready",
                        False,
                    )
                ),
            )
        )

    return NativePlan(
        request_id=str(
            raw.get(
                "request_id",
                "",
            )
            or ""
        ),
        spec_id=str(
            raw.get(
                "spec_id",
                "",
            )
            or ""
        ),
        objective=str(
            raw.get(
                "objective",
                "",
            )
            or ""
        ),
        steps=steps,
        acceptance_criteria=list(
            raw.get(
                "acceptance_criteria",
                [],
            )
            or []
        ),
        missing_capabilities=list(
            raw.get(
                "missing_capabilities",
                [],
            )
            or []
        ),
    )


def _safe_target(
    path: str,
) -> str:

    normalized = str(
        path
        or ""
    ).replace("\\", "/").strip()

    if not normalized:
        raise ValueError(
            "TARGET_PATH_EMPTY"
        )

    pp = PurePosixPath(
        normalized
    )

    if pp.is_absolute():
        raise ValueError(
            f"TARGET_PATH_ABSOLUTE:{normalized}"
        )

    if ".." in pp.parts:
        raise ValueError(
            f"TARGET_PATH_ESCAPE:{normalized}"
        )

    return normalized


def _sha256(
    content: str,
) -> str:

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def _touched_targets(
    plan: NativePlan,
) -> list[str]:

    result: list[str] = []

    for step in plan.steps:

        if step.primitive == "VERIFY_TESTS":
            continue

        if step.target_path == "<acceptance>":
            continue

        target = _safe_target(
            step.target_path
        )

        if target not in result:
            result.append(target)

    return result


def build_native_repair_proposal(
    native_plan: NativePlan | dict[str, Any],
    *,
    request: RepairRequest,
    repo_root: Path | str,
    confidence: str = "MEDIUM",
) -> NativeRepairProposalBuildResult:

    if isinstance(
        native_plan,
        dict,
    ):
        try:
            plan = _plan_from_dict(
                native_plan
            )

        except Exception as exc:

            return NativeRepairProposalBuildResult(
                status="INVALID_NATIVE_PLAN",
                errors=[
                    (
                        "NATIVE_PLAN_PARSE_ERROR:"
                        f"{type(exc).__name__}:"
                        f"{exc}"
                    )
                ],
            )

    else:
        plan = native_plan

    root = Path(
        repo_root
    )

    try:
        targets = _touched_targets(
            plan
        )

    except Exception as exc:

        return NativeRepairProposalBuildResult(
            status="INVALID_NATIVE_PLAN",
            errors=[
                str(exc)
            ],
        )

    original_sources: dict[
        str,
        str,
    ] = {}

    # Hash exact des octets du fichier de r?f?rence.
    # Le texte reste normalis? comme Path.read_text()
    # pour pr?server le comportement historique du moteur,
    # mais REPAIR_BASE_DRIFT compare byte-for-byte.
    original_sha256: dict[
        str,
        str,
    ] = {}

    existed_before: dict[
        str,
        bool,
    ] = {}

    for target in targets:

        absolute = (
            root
            / Path(target)
        )

        exists = absolute.is_file()

        existed_before[
            target
        ] = exists

        if exists:

            try:
                raw_bytes = absolute.read_bytes()

                original_sha256[
                    target
                ] = hashlib.sha256(
                    raw_bytes
                ).hexdigest()

                # Equivalent au universal-newline de
                # Path.read_text(), sans perdre le hash
                # exact des octets d'origine.
                original_sources[
                    target
                ] = (
                    raw_bytes
                    .decode("utf-8")
                    .replace("\r\n", "\n")
                    .replace("\r", "\n")
                )

            except Exception as exc:

                return NativeRepairProposalBuildResult(
                    status=(
                        "CURRENT_SOURCE_UNAVAILABLE"
                    ),
                    errors=[
                        (
                            "CURRENT_SOURCE_READ_FAILED:"
                            f"{target}:"
                            f"{type(exc).__name__}"
                        )
                    ],
                )

    execution = execute_native_plan(
        plan,
        original_sources,
    )

    # VERIFY_TESTS belongs to the existing RepairProposal sandbox rail.
    # Reaching it after successful source generation is therefore acceptable.
    if execution.status not in {
        "PASS",
        "AWAITING_VERIFICATION",
    }:

        return NativeRepairProposalBuildResult(
            status="NATIVE_EXECUTION_BLOCKED",
            execution=execution.to_dict(),
            errors=list(
                execution.errors
            ),
        )

    candidates: list[
        RepairCandidateFile
    ] = []

    for target in targets:

        generated = (
            execution.generated_sources.get(
                target
            )
        )

        if generated is None:
            continue

        original = original_sources.get(
            target,
            "",
        )

        if (
            existed_before[target]
            and generated == original
        ):
            continue

        change_kind = (
            "MODIFY"
            if existed_before[target]
            else "CREATE"
        )

        candidates.append(
            RepairCandidateFile(
                path=target,
                full_content=generated,
                change_kind=change_kind,
                base_sha256=(
                    original_sha256.get(
                        target,
                        "",
                    )
                    if existed_before[target]
                    else ""
                ),
                rationale=(
                    "Generated by bounded native "
                    "Obsidure semantic execution."
                ),
            )
        )

    if not candidates:

        return NativeRepairProposalBuildResult(
            status="NO_CHANGE_REQUIRED",
            execution=execution.to_dict(),
        )

    proposal = RepairProposal(
        request_id=request.request_id,
        engine=BUILDER_ID,
        rationale=(
            "Native Brody/Obsidure implementation candidate. "
            "Produced from structured DesiredState, semantic IR "
            "and bounded AST operations. "
            "No repository mutation performed."
        ),
        candidate_files=candidates,
        tests_to_run=list(
            request.tests_hint
            or []
        ),
        confidence=str(
            confidence
            or "MEDIUM"
        ),
    )

    return NativeRepairProposalBuildResult(
        status="REPAIR_PROPOSAL_READY",
        proposal=proposal,
        execution=execution.to_dict(),
    )


def self_check() -> dict[str, Any]:

    return {
        "builder_id": BUILDER_ID,
        "role": (
            "NATIVE_PLAN_TO_CANONICAL_REPAIR_PROPOSAL"
        ),
        "repository_write": False,
        "auto_apply": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "external_engine_called": False,
    }
