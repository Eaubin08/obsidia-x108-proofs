from pathlib import Path
import ast
import hashlib

from apps.obsidia_api.brody_code_state import (
    analyze_python_code_state,
)
from apps.obsidia_api.brody_desired_state_planner import (
    DesiredTargetState,
    plan_desired_state,
)
from periphery.agents import (
    obsidure_repair_bridge as repair_bridge,
)
from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)
from periphery.agents.obsidure_native_repair_proposal import (
    build_native_repair_proposal,
)
from periphery.agents.obsidure_native_semantic_compiler import (
    compile_semantic_operations,
)
from periphery.agents.obsidure_repair_contract import (
    RepairRequest,
)


TARGET = (
    "apps/obsidia_api/"
    "multistep_sandbox_probe.py"
)


def _assert_desired_source(source: str) -> None:
    tree = ast.parse(source)

    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
    ]

    assert len(imports) == 1

    imp = imports[0]

    assert imp.module == "math"
    assert [
        alias.name
        for alias in imp.names
    ] == ["sqrt"]

    fn = next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "normalize"
        )
    )

    assert len(fn.body) == 1
    assert isinstance(
        fn.body[0],
        ast.Return,
    )

    call = fn.body[0].value

    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "sqrt"

    assert len(call.args) == 1
    assert isinstance(call.args[0], ast.Name)
    assert call.args[0].id == "value"


def test_add_import_then_modify_function_reaches_real_sandbox(
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Deliberately use CRLF so base_sha256 proves
    # byte-exact drift protection independently
    # from the executor's normalized text rail.
    original = (
        "def normalize(value: float) -> float:\r\n"
        "    return value\r\n"
    ).encode("utf-8")

    target.write_bytes(original)

    before = target.read_bytes()

    current = analyze_python_code_state(
        TARGET,
        target.read_text(
            encoding="utf-8",
        ),
    )

    desired = DesiredTargetState(
        path=TARGET,
        imports=[
            {
                "module": "math",
                "names": ["sqrt"],
            },
        ],
        functions=[
            {
                "name": "normalize",
                "args": [
                    {
                        "name": "value",
                        "annotation": "float",
                    },
                ],
                "returns": "float",
                "body": [
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "CALL",
                            "func": "sqrt",
                            "args": [
                                {
                                    "kind": "NAME",
                                    "id": "value",
                                },
                            ],
                        },
                    },
                ],
            },
        ],
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert [
        operation.kind
        for operation in operations
    ] == [
        "IMPORT_FROM",
        "MODIFY_FUNCTION",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "ADD_IMPORT",
        "MODIFY_FUNCTION",
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_multistep_sandbox",
        spec_id="spec_multistep_sandbox",
        objective=(
            "compose import insertion and "
            "function modification"
        ),
        deltas=deltas,
    )

    assert [
        step.primitive
        for step in plan.steps
    ] == [
        "ADD_IMPORT",
        "MODIFY_FUNCTION",
    ]

    assert (
        plan.steps[1].depends_on
        == (
            plan.steps[0].step_id,
        )
    )

    request = RepairRequest(
        objective=(
            "compose import insertion and "
            "function modification"
        ),
        failure_mode="INCORRECT_IMPLEMENTATION",
        repo_targets=[TARGET],
    )

    build = build_native_repair_proposal(
        plan,
        request=request,
        repo_root=tmp_path,
        confidence="HIGH",
    )

    assert (
        build.status
        == "REPAIR_PROPOSAL_READY"
    )
    assert build.errors == []
    assert build.proposal is not None

    proposal = build.proposal

    assert len(
        proposal.candidate_files
    ) == 1

    candidate = (
        proposal.candidate_files[0]
    )

    assert candidate.path == TARGET
    assert (
        candidate.change_kind
        == "MODIFY"
    )

    assert (
        candidate.base_sha256
        == hashlib.sha256(
            before
        ).hexdigest()
    )

    # Both operations must be present in the
    # single final candidate source.
    _assert_desired_source(
        candidate.full_content
    )

    # Proposal building is memory-only.
    assert target.read_bytes() == before

    assert (
        proposal.boundary[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )
    assert (
        proposal.boundary["auto_apply"]
        is False
    )
    assert (
        proposal.boundary[
            "canonical_write"
        ]
        is False
    )
    assert (
        proposal.boundary["auto_commit"]
        is False
    )
    assert (
        proposal.boundary["auto_push"]
        is False
    )
    assert (
        proposal.boundary["sandbox_mode"]
        == "HUMAN_APPROVED_WRITE"
    )

    monkeypatch.setattr(
        repair_bridge,
        "REPO_ROOT",
        tmp_path,
    )

    verdict = (
        repair_bridge
        .test_repair_proposal(
            proposal,
            request=request,
            run_tests=True,
        )
    )

    try:
        assert verdict.status in {
            "PASS",
            "PARTIAL",
        }

        assert verdict.errors == []

        assert TARGET in (
            verdict.compiled_files
        )

        sandbox_target = (
            Path(verdict.sandbox_dir)
            / TARGET
        )

        assert sandbox_target.is_file()

        sandbox_source = (
            sandbox_target.read_text(
                encoding="utf-8",
            )
        )

        # Real sandbox contains the composed result,
        # not only one of the two operations.
        _assert_desired_source(
            sandbox_source
        )

        # Canonical/original file never changed.
        assert (
            target.read_bytes()
            == before
        )

    finally:
        repair_bridge.cleanup_repair_sandbox(
            verdict
        )

        assert (
            target.read_bytes()
            == before
        )
