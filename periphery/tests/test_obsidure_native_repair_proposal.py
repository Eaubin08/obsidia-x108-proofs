from pathlib import Path

import ast

from periphery.agents.obsidure_native_plan import (
    NativePlan,
    NativePlanStep,
)

from periphery.agents.obsidure_native_repair_proposal import (
    build_native_repair_proposal,
)

from periphery.agents.obsidure_repair_contract import (
    RepairRequest,
    validate_repair_proposal,
)


def request():
    return RepairRequest(
        objective="native implementation",
        tests_hint=[],
    )


def test_native_plan_builds_create_repair_proposal(
    tmp_path: Path,
):

    target = "periphery/generated_native.py"

    plan = NativePlan(
        request_id="rr_native_create",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="create native module",
        steps=[
            NativePlanStep(
                step_id="s1",
                primitive="CREATE_FILE",
                target_path=target,
                rationale="create",
                parameters={
                    "source": (
                        '"""native."""\n'
                    )
                },
                execution_ready=True,
            ),
            NativePlanStep(
                step_id="s2",
                primitive="ADD_FUNCTION",
                target_path=target,
                rationale="function",
                parameters={
                    "source": (
                        "def probe():\n"
                        "    return 1\n"
                    )
                },
                depends_on=("s1",),
                execution_ready=True,
            ),
        ],
    )

    result = build_native_repair_proposal(
        plan,
        request=request(),
        repo_root=tmp_path,
        confidence="HIGH",
    )

    assert (
        result.status
        == "REPAIR_PROPOSAL_READY"
    )

    assert result.proposal is not None

    assert len(
        result.proposal.candidate_files
    ) == 1

    candidate = (
        result.proposal.candidate_files[0]
    )

    assert candidate.path == target
    assert candidate.change_kind == "CREATE"

    assert "def probe" in (
        candidate.full_content
    )

    ast.parse(
        candidate.full_content
    )

    # Critical invariant:
    # native execution produced a candidate,
    # never a repository write.
    assert not (
        tmp_path / target
    ).exists()

    assert (
        validate_repair_proposal(
            result.proposal
        )
        == []
    )


def test_native_plan_builds_modify_proposal(
    tmp_path: Path,
):

    target = "periphery/existing_native.py"

    absolute = (
        tmp_path / target
    )

    absolute.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = (
        "class Result:\n"
        "    pass\n"
    )

    absolute.write_text(
        original,
        encoding="utf-8",
    )

    plan = NativePlan(
        request_id="rr_native_modify",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="add confidence field",
        steps=[
            NativePlanStep(
                step_id="s1",
                primitive="ADD_FIELD",
                target_path=target,
                rationale="field",
                parameters={
                    "class_name": "Result",
                    "source": (
                        "confidence: float = 0.0"
                    ),
                },
                execution_ready=True,
            ),
        ],
    )

    result = build_native_repair_proposal(
        plan,
        request=request(),
        repo_root=tmp_path,
    )

    assert (
        result.status
        == "REPAIR_PROPOSAL_READY"
    )

    candidate = (
        result.proposal.candidate_files[0]
    )

    assert (
        candidate.change_kind
        == "MODIFY"
    )

    assert candidate.base_sha256

    assert (
        "confidence: float = 0.0"
        in candidate.full_content
    )

    # Original repository source unchanged.
    assert (
        absolute.read_text(
            encoding="utf-8"
        )
        == original
    )


def test_verify_step_becomes_repair_validation_boundary(
    tmp_path: Path,
):

    target = "periphery/generated_verify.py"

    plan = NativePlan(
        request_id="rr_verify",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="create then verify",
        steps=[
            NativePlanStep(
                step_id="s1",
                primitive="CREATE_FILE",
                target_path=target,
                rationale="create",
                parameters={
                    "source": (
                        "VALUE = 1\n"
                    )
                },
                execution_ready=True,
            ),

            NativePlanStep(
                step_id="verify",
                primitive="VERIFY_TESTS",
                target_path="<acceptance>",
                rationale="verify",
                parameters={
                    "criteria": [
                        "candidate compiles"
                    ]
                },
                depends_on=("s1",),
                execution_ready=True,
            ),
        ],
    )

    result = build_native_repair_proposal(
        plan,
        request=request(),
        repo_root=tmp_path,
    )

    assert (
        result.execution["status"]
        == "AWAITING_VERIFICATION"
    )

    assert (
        result.status
        == "REPAIR_PROPOSAL_READY"
    )

    assert result.proposal is not None


def test_invalid_dependency_does_not_produce_proposal(
    tmp_path: Path,
):

    target = "periphery/bad.py"

    plan = NativePlan(
        request_id="rr_bad",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="bad",
        steps=[
            NativePlanStep(
                step_id="s2",
                primitive="ADD_FUNCTION",
                target_path=target,
                rationale="bad dependency",
                parameters={
                    "source": (
                        "def f():\n"
                        "    return 1\n"
                    )
                },
                depends_on=(
                    "missing",
                ),
                execution_ready=True,
            )
        ],
    )

    result = build_native_repair_proposal(
        plan,
        request=request(),
        repo_root=tmp_path,
    )

    assert (
        result.status
        == "NATIVE_EXECUTION_BLOCKED"
    )

    assert result.proposal is None
