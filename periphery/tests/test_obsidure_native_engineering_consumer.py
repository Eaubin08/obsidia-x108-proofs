from pathlib import Path

from apps.obsidia_api.brody_repair_reasoning import BrodyReasoningProvider
from periphery.agents.obsidure_native_engineering_consumer import (
    consume_brody_engineering_spec,
)
from periphery.agents.obsidure_reasoning_provider import (
    DiagnosisStatus,
    RepairDiagnosis,
    run_reasoning_cycle,
)
from periphery.agents.obsidure_repair_contract import RepairRequest


def test_consumer_reports_current_native_capability_gap():
    diagnosis = RepairDiagnosis(
        provider="BRODY",
        request_id="rr_test",
        status=DiagnosisStatus.NEEDS_NATIVE_ENGINE,
        defect_class="IMPLEMENTATION_REQUEST",
        findings=[{
            "type": "BRODY_ENGINEERING_SPEC",
            "spec": {
                "spec_id": "BRODY_ENGINEERING_SPEC_V1",
                "objective": "implement bounded semantic calibration",
                "targets": [{
                    "path": "apps/obsidia_api/example.py",
                    "target_state": "EXISTING",
                    "source_present": True,
                }],
            },
        }],
    )

    result = consume_brody_engineering_spec(diagnosis)

    assert result.status == "NATIVE_PLAN_READY_CAPABILITIES_MISSING"
    assert result.proposal is None
    assert result.external_engine_called is False
    assert (
        "SEMANTIC_EDIT_DECOMPOSITION_MISSING:apps/obsidia_api/example.py"
        in result.missing_capabilities
    )
    assert (
        "SEMANTIC_EDIT_DECOMPOSITION_MISSING:apps/obsidia_api/example.py"
        in result.missing_capabilities
    )


def test_reasoning_cycle_hands_brody_spec_to_native_obsidure(tmp_path: Path):
    target = tmp_path / "apps" / "obsidia_api" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")

    request = RepairRequest(
        objective="implement bounded semantic calibration",
        failure_mode="NO_ARTIFACT_PRODUCED",
        repo_targets=["apps/obsidia_api/example.py"],
        tests_hint=["semantic calibration test"],
    )

    outcome = run_reasoning_cycle(
        request,
        providers=[BrodyReasoningProvider()],
        allow_external=False,
        repo_root=tmp_path,
    )

    assert outcome.proposal is not None
    assert outcome.proposal.engine == "OBSIDURE_NATIVE_REPAIR_PROPOSAL_V1"
    assert len(outcome.proposal.candidate_files) == 1

    candidate = outcome.proposal.candidate_files[0]

    assert candidate.path == "apps/obsidia_api/example.py"
    assert candidate.change_kind == "MODIFY"
    assert "calibrate_semantics" in candidate.full_content

    # Native generation must still be proposal-only.
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"
    assert outcome.diagnosis is not None
    assert outcome.diagnosis.status == DiagnosisStatus.NEEDS_NATIVE_ENGINE
    # Native capability is now available through:
    # Brody code concept -> DesiredState -> NativePlan.
    assert outcome.diagnosis.defect_class == "IMPLEMENTATION_REQUEST"
    assert outcome.providers_tried == ["BRODY"]
    assert outcome.external_fallback_offered is False

    handoffs = [
        item for item in outcome.diagnosis.findings
        if item.get("type") == "OBSIDURE_NATIVE_HANDOFF"
    ]

    assert len(handoffs) == 1
    assert handoffs[0]["result"]["status"] == "NATIVE_PLAN_READY"
    assert handoffs[0]["result"]["missing_capabilities"] == []
    assert handoffs[0]["result"]["native_plan"] is not None
    assert handoffs[0]["result"]["external_engine_called"] is False
