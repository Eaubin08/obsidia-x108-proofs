from pathlib import Path

import periphery.agents.obsidure_repair_bridge as repair_bridge

from periphery.agents.agent_obsidure import (
    AgentObsidure,
    OSTradResult,
    StabilizationResult,
)

from periphery.agents.obsidure_repair_contract import (
    RepairVerdict,
)


TARGET = (
    "periphery/"
    "native_e2e_semantic_calibration_probe.py"
)


def test_brody_native_proposal_reaches_real_obsidure_sandbox(
    tmp_path: Path,
    monkeypatch,
):

    """
    Full native loop:

        Obsidure failed cycle
        -> RepairRequest
        -> Brody cognition
        -> learned CodeConcept
        -> DesiredState
        -> NativePlan
        -> NativeProgramExecutor
        -> RepairProposal
        -> AgentObsidure.evaluate_repair_proposal(run_tests=True)
        -> real repair sandbox
        -> RepairVerdict

    Critical invariant:
        TARGET is never written into the repository.
    """

    from periphery.agents import agent_obsidure as agent_module

    repo_root = agent_module.REPO_ROOT
    repo_target = repo_root / TARGET

    # This probe must never exist canonically.
    assert not repo_target.exists()

    # Do not persist the RepairRequest during this test.
    # Persistence is not what is under test here.
    monkeypatch.setattr(
        repair_bridge,
        "persist_repair_request",
        lambda request: (
            tmp_path
            / f"{request.request_id}.json"
        ),
    )

    agent = AgentObsidure(
        verbose=False,
    )

    # No previous functional error is necessary:
    # NO_ARTIFACT_PRODUCED is the bounded implementation route.
    agent._last_error_contexts = []

    os_trad = OSTradResult(
        detected_language="en",
        intent="PYTHON_PATCH_PROPOSAL",
        target_paths=[TARGET],
        source="TEST_NATIVE_E2E",
    )

    stabilization = StabilizationResult(
        attempts=1,
        max_attempts=1,
        final_status="MAX_ATTEMPTS_REACHED",
        errors_history=[],
        passed=False,
    )

    captured = {}

    original_evaluate = (
        agent.evaluate_repair_proposal
    )

    def capture_evaluation(
        proposal_source,
        run_tests=True,
    ):
        captured["proposal"] = proposal_source
        captured["run_tests"] = run_tests

        verdict = original_evaluate(
            proposal_source,
            run_tests=run_tests,
        )

        captured["verdict"] = verdict

        return verdict

    monkeypatch.setattr(
        agent,
        "evaluate_repair_proposal",
        capture_evaluation,
    )

    request_dict = (
        agent._maybe_build_repair_request(
            objective=(
                "implement bounded semantic calibration "
                "for unknown terms"
            ),
            os_trad=os_trad,
            patches=[],
            stabilization=stabilization,
        )
    )

    assert request_dict is not None

    # Target propagation:
    # OS_TRAD -> RepairRequest -> EngineeringSpec.
    assert TARGET in (
        request_dict.get(
            "repo_targets",
            [],
        )
    )

    # The automatic route must have reached evaluation.
    assert "proposal" in captured
    assert "verdict" in captured

    proposal = captured["proposal"]

    assert (
        proposal.engine
        == "OBSIDURE_NATIVE_REPAIR_PROPOSAL_V1"
    )

    assert len(
        proposal.candidate_files
    ) == 1

    candidate = (
        proposal.candidate_files[0]
    )

    assert candidate.path == TARGET
    assert candidate.change_kind == "CREATE"

    assert (
        "calibrate_semantics"
        in candidate.full_content
    )

    # This proves AgentObsidure itself invoked the
    # sandbox rail with tests enabled.
    assert captured["run_tests"] is True

    verdict = captured["verdict"]

    assert verdict is not None

    # With no declared functional test the canonical
    # sandbox can legitimately return PARTIAL.
    # PASS is also acceptable if a verification route
    # supplies executable tests.
    assert verdict["status"] in {
        "PASS",
        "PARTIAL",
    }

    assert TARGET in (
        verdict.get(
            "compiled_files",
            [],
        )
    )

    sandbox_dir = Path(
        verdict["sandbox_dir"]
    )

    assert sandbox_dir.is_dir()

    # Candidate exists inside sandbox...
    assert (
        sandbox_dir / TARGET
    ).is_file()

    # ...but NEVER inside repository.
    assert not repo_target.exists()

    # Governance boundaries still intact.
    assert (
        proposal.boundary[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        proposal.boundary[
            "auto_apply"
        ]
        is False
    )

    # Canonical cleanup.
    try:
        sandbox_verdict = RepairVerdict(
            sandbox_dir=str(
                sandbox_dir
            )
        )

        assert (
            repair_bridge.cleanup_repair_sandbox(
                sandbox_verdict
            )
            is True
        )

    finally:
        # Even after sandbox cleanup:
        # absolutely no canonical source appeared.
        assert not repo_target.exists()
