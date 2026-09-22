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
    "existing_method_probe.py"
)


def _class_from_source(
    source: str,
) -> ast.ClassDef:
    tree = ast.parse(source)

    return next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "Calibrator"
        )
    )


def _methods(
    source: str,
) -> dict[str, ast.FunctionDef]:
    cls = _class_from_source(source)

    return {
        node.name: node
        for node in cls.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
    }


def _return_value(
    method: ast.FunctionDef,
):
    assert len(method.body) == 1
    assert isinstance(
        method.body[0],
        ast.Return,
    )
    assert isinstance(
        method.body[0].value,
        ast.Constant,
    )

    return method.body[0].value.value


def test_existing_wrong_method_is_modified_only_in_sandbox(
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = (
        "class Calibrator:\n"
        "    marker: int = 7\n\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n\n'
        "    def keep(self) -> str:\n"
        '        return "KEEP"\n'
    )

    target.write_text(
        original,
        encoding="utf-8",
    )

    before = target.read_bytes()

    current = analyze_python_code_state(
        TARGET,
        target.read_text(
            encoding="utf-8",
        ),
    )

    desired = DesiredTargetState(
        path=TARGET,
        classes=[
            {
                "name": "Calibrator",
                "methods": [
                    {
                        "name": "calibrate",
                        "args": [
                            {
                                "name": "self",
                                "annotation": "",
                            },
                            {
                                "name": "value",
                                "annotation": "str",
                            },
                        ],
                        "returns": "str",
                        "body": [
                            {
                                "kind": "RETURN",
                                "expr": {
                                    "kind": "CONSTANT",
                                    "value": "NEW",
                                },
                            },
                        ],
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
        "MODIFY_METHOD",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "MODIFY_METHOD",
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_modify_method_e2e",
        spec_id="spec_modify_method_e2e",
        objective=(
            "modify one bounded existing "
            "class method"
        ),
        deltas=deltas,
    )

    assert [
        step.primitive
        for step in plan.steps
    ] == [
        "MODIFY_METHOD",
    ]

    step = plan.steps[0]

    assert (
        step.parameters["class_name"]
        == "Calibrator"
    )
    assert (
        step.parameters["name"]
        == "calibrate"
    )

    request = RepairRequest(
        objective=(
            "modify one bounded existing "
            "class method"
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

    assert (
        proposal.engine
        == "OBSIDURE_NATIVE_REPAIR_PROPOSAL_V1"
    )

    # Human validation remains mandatory.
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

    candidate_methods = _methods(
        candidate.full_content
    )

    assert set(candidate_methods) == {
        "calibrate",
        "keep",
    }

    assert (
        _return_value(
            candidate_methods[
                "calibrate"
            ]
        )
        == "NEW"
    )

    assert (
        _return_value(
            candidate_methods["keep"]
        )
        == "KEEP"
    )

    candidate_class = _class_from_source(
        candidate.full_content
    )

    marker = next(
        node
        for node in candidate_class.body
        if isinstance(
            node,
            ast.AnnAssign,
        )
    )

    assert isinstance(
        marker.target,
        ast.Name,
    )
    assert marker.target.id == "marker"

    # Proposal generation must not mutate repo.
    assert target.read_bytes() == before

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

        sandbox_methods = _methods(
            sandbox_source
        )

        assert set(sandbox_methods) == {
            "calibrate",
            "keep",
        }

        assert (
            _return_value(
                sandbox_methods[
                    "calibrate"
                ]
            )
            == "NEW"
        )

        assert (
            _return_value(
                sandbox_methods[
                    "keep"
                ]
            )
            == "KEEP"
        )

        sandbox_class = (
            _class_from_source(
                sandbox_source
            )
        )

        marker = next(
            node
            for node
            in sandbox_class.body
            if isinstance(
                node,
                ast.AnnAssign,
            )
        )

        assert isinstance(
            marker.target,
            ast.Name,
        )
        assert marker.target.id == "marker"

        # Only sandbox changed.
        assert (
            target.read_bytes()
            == before
        )

    finally:
        repair_bridge.cleanup_repair_sandbox(
            verdict
        )

        # No human-approved write happened.
        assert (
            target.read_bytes()
            == before
        )
