from pathlib import Path

from periphery.agents import (
    obsidure_repair_bridge as repair_bridge,
)
from periphery.agents.obsidure_reasoning_provider import (
    run_reasoning_cycle,
)
from periphery.agents.obsidure_repair_contract import (
    RepairRequest,
)


TARGET = "apps/obsidia_api/existing_semantic_probe.py"


def test_existing_wrong_function_is_modified_only_in_sandbox(
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / TARGET
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = (
        "def calibrate_semantics("
        "term: str, known: bool"
        ") -> str:\n"
        '    return "BROKEN"\n'
    )

    target.write_text(
        original,
        encoding="utf-8",
    )

    before = target.read_bytes()

    request = RepairRequest(
        objective=(
            "implement bounded semantic calibration "
            "for unknown terms"
        ),
        failure_mode="NO_ARTIFACT_PRODUCED",
        repo_targets=[TARGET],
    )

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

    import hashlib

    assert (
        candidate.base_sha256
        == hashlib.sha256(before).hexdigest()
    )

    assert "calibrate_semantics" in candidate.full_content
    assert '"BROKEN"' not in candidate.full_content

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

    assert "MODIFY_FUNCTION" in primitives
    assert "CREATE_FILE" not in primitives

    # Original source still untouched.
    assert target.read_bytes() == before

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

        sandbox_source = sandbox_target.read_text(
            encoding="utf-8",
        )

        assert "calibrate_semantics" in sandbox_source
        assert '"BROKEN"' not in sandbox_source

        # Repaired only in sandbox.
        assert target.read_bytes() == before

    finally:
        repair_bridge.cleanup_repair_sandbox(
            verdict
        )

        # Human never approved write:
        # canonical file must remain identical.
        assert target.read_bytes() == before
