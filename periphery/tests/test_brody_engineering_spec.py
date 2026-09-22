from pathlib import Path

from apps.obsidia_api.brody_engineering_spec import build_brody_engineering_spec
from apps.obsidia_api.brody_repair_reasoning import BrodyReasoningProvider
from periphery.agents.obsidure_repair_contract import RepairRequest
from periphery.agents.obsidure_reasoning_provider import DiagnosisStatus


def test_engineering_spec_existing_and_create_targets(tmp_path: Path):
    existing = tmp_path / "apps" / "obsidia_api" / "existing.py"
    existing.parent.mkdir(parents=True)
    existing.write_text("VALUE = 1\n", encoding="utf-8")

    request = RepairRequest(
        objective=(
            "impl?mente le changement "
            "decision_authority=KX108_ONLY emits_act=false "
            "kernel_mutation=false memory_write=false"
        ),
        failure_mode="NO_ARTIFACT_PRODUCED",
        repo_targets=[
            "apps/obsidia_api/existing.py",
            "periphery/harness/new_module.py",
        ],
        tests_hint=["known term resolves", "unknown term holds"],
    )

    spec = build_brody_engineering_spec(request, tmp_path)

    assert spec.targets[0].target_state == "EXISTING"
    assert spec.targets[0].source_present is True
    assert spec.targets[1].target_state == "CREATE"
    assert spec.targets[1].source_present is False
    assert spec.explicit_invariants["decision_authority"] == "KX108_ONLY"
    assert spec.explicit_invariants["emits_act"].lower() == "false"
    assert spec.acceptance_criteria == [
        "known term resolves",
        "unknown term holds",
    ]
    assert spec.confidence == "HIGH"
    assert spec.can_generate_source is False
    assert spec.can_decide is False


def test_brody_routes_bounded_implementation_to_native_engine(tmp_path: Path):
    target = tmp_path / "apps" / "obsidia_api" / "existing.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")

    request = RepairRequest(
        objective="impl?mente une modification born?e",
        failure_mode="NO_ARTIFACT_PRODUCED",
        repo_targets=["apps/obsidia_api/existing.py"],
    )

    diagnosis = BrodyReasoningProvider().diagnose(
        request,
        repo_root=tmp_path,
    )

    assert diagnosis.status == DiagnosisStatus.NEEDS_NATIVE_ENGINE
    assert diagnosis.defect_class == "IMPLEMENTATION_REQUEST"
    assert diagnosis.findings
    assert diagnosis.findings[0]["type"] == "BRODY_ENGINEERING_SPEC"
    assert diagnosis.findings[0]["spec"]["can_generate_source"] is False
