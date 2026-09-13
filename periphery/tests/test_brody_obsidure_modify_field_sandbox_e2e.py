from pathlib import Path
import ast
import hashlib

from periphery.agents import (
    obsidure_repair_bridge as repair_bridge,
)
from periphery.agents.obsidure_reasoning_provider import (
    run_reasoning_cycle,
)
from periphery.agents.obsidure_repair_contract import (
    RepairRequest,
)


TARGET = (
    "apps/obsidia_api/"
    "existing_semantic_field_probe.py"
)


def _ast_fingerprint(source: str) -> str:
    return ast.dump(
        ast.parse(source),
        annotate_fields=True,
        include_attributes=False,
    )


def test_existing_wrong_field_is_modified_only_in_sandbox(
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / TARGET
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    request = RepairRequest(
        objective=(
            "implement bounded semantic calibration "
            "for unknown terms"
        ),
        failure_mode="NO_ARTIFACT_PRODUCED",
        repo_targets=[TARGET],
    )

    # --------------------------------------------------
    # 1. Ask the real Brody/Obsidure route what the
    #    correct implementation should structurally be.
    #    Target does not exist yet: proposal only.
    # --------------------------------------------------

    seed_outcome = run_reasoning_cycle(
        request,
        allow_external=False,
        repo_root=tmp_path,
    )

    assert seed_outcome.proposal is not None

    seed_proposal = seed_outcome.proposal

    assert len(seed_proposal.candidate_files) == 1

    seed_candidate = (
        seed_proposal.candidate_files[0]
    )

    assert seed_candidate.path == TARGET
    assert seed_candidate.change_kind == "CREATE"

    seed_source = seed_candidate.full_content

    seed_tree = ast.parse(seed_source)

    # Find one actual learned class field instead of
    # hardcoding its desired annotation/default.
    selected_class = None
    selected_field = None

    for node in seed_tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for child in node.body:
            if (
                isinstance(child, ast.AnnAssign)
                and isinstance(
                    child.target,
                    ast.Name,
                )
            ):
                selected_class = node
                selected_field = child
                break

        if selected_field is not None:
            break

    assert selected_class is not None
    assert selected_field is not None
    assert selected_field.annotation is not None

    class_name = selected_class.name
    field_name = selected_field.target.id

    desired_annotation = ast.unparse(
        selected_field.annotation
    )

    # Deliberately make exactly this field wrong.
    wrong_annotation = (
        "str"
        if desired_annotation != "str"
        else "int"
    )

    selected_field.annotation = ast.Name(
        id=wrong_annotation,
        ctx=ast.Load(),
    )

    ast.fix_missing_locations(seed_tree)

    wrong_source = (
        ast.unparse(seed_tree).rstrip()
        + "\n"
    )

    assert (
        _ast_fingerprint(wrong_source)
        != _ast_fingerprint(seed_source)
    )

    target.write_text(
        wrong_source,
        encoding="utf-8",
    )

    before = target.read_bytes()

    # --------------------------------------------------
    # 2. Same human objective, but now the target exists
    #    with one structurally wrong class field.
    # --------------------------------------------------

    outcome = run_reasoning_cycle(
        request,
        allow_external=False,
        repo_root=tmp_path,
    )

    assert outcome.proposal is not None

    proposal = outcome.proposal

    # Human approval remains mandatory.
    assert (
        proposal.boundary["decision_authority"]
        == "KX108_ONLY"
    )
    assert proposal.boundary["auto_apply"] is False
    assert proposal.boundary["auto_commit"] is False
    assert proposal.boundary["auto_push"] is False
    assert (
        proposal.boundary["sandbox_mode"]
        == "HUMAN_APPROVED_WRITE"
    )

    assert (
        proposal.engine
        == "OBSIDURE_NATIVE_REPAIR_PROPOSAL_V1"
    )

    assert len(proposal.candidate_files) == 1

    candidate = proposal.candidate_files[0]

    assert candidate.path == TARGET
    assert candidate.change_kind == "MODIFY"

    assert (
        candidate.base_sha256
        == hashlib.sha256(before).hexdigest()
    )

    # Candidate restores the exact desired AST,
    # not merely syntactically valid Python.
    assert (
        _ast_fingerprint(
            candidate.full_content
        )
        == _ast_fingerprint(
            seed_source
        )
    )

    handoff = next(
        item
        for item in outcome.diagnosis.findings
        if (
            isinstance(item, dict)
            and item.get("type")
            == "OBSIDURE_NATIVE_HANDOFF"
        )
    )

    native_plan = handoff["result"]["native_plan"]

    primitives = [
        step["primitive"]
        for step in native_plan["steps"]
    ]

    assert "MODIFY_FIELD" in primitives
    assert "CREATE_FILE" not in primitives

    # This test is specifically about a field edit.
    assert "MODIFY_FUNCTION" not in primitives
    assert primitives.count("MODIFY_FIELD") == 1

    # Real temporary repo still untouched by reasoning.
    assert target.read_bytes() == before

    # --------------------------------------------------
    # 3. Existing real repair sandbox rail.
    # --------------------------------------------------

    monkeypatch.setattr(
        repair_bridge,
        "REPO_ROOT",
        tmp_path,
    )

    verdict = repair_bridge.test_repair_proposal(
        proposal,
        request=request,
        run_tests=True,
    )

    try:
        assert verdict.status in {
            "PASS",
            "PARTIAL",
        }

        assert verdict.errors == []
        assert TARGET in verdict.compiled_files

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

        # Sandbox contains the restored desired AST.
        assert (
            _ast_fingerprint(
                sandbox_source
            )
            == _ast_fingerprint(
                seed_source
            )
        )

        # Verify selected field specifically.
        sandbox_tree = ast.parse(
            sandbox_source
        )

        restored_field = None

        for node in sandbox_tree.body:
            if (
                isinstance(node, ast.ClassDef)
                and node.name == class_name
            ):
                for child in node.body:
                    if (
                        isinstance(
                            child,
                            ast.AnnAssign,
                        )
                        and isinstance(
                            child.target,
                            ast.Name,
                        )
                        and child.target.id
                        == field_name
                    ):
                        restored_field = child
                        break

        assert restored_field is not None

        assert (
            ast.unparse(
                restored_field.annotation
            )
            == desired_annotation
        )

        # Repaired only in sandbox.
        assert target.read_bytes() == before

    finally:
        repair_bridge.cleanup_repair_sandbox(
            verdict
        )

        # No human approval:
        # canonical/temp-repo source stays wrong
        # and byte-for-byte untouched.
        assert target.read_bytes() == before
