"""Safe CSSA historical projection → canonical native intake *draft*, no commit."""
from dataclasses import dataclass
from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
from periphery.cssa_historical_native_intake_draft_v0 import draft_cssa_historical_native_intake_v0
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0


@dataclass(frozen=True)
class ContractAssessmentV0:
    case_id: str = "c-1"
    assessed_at: str = "2026-10-07"
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ("sim:proof",)
    responsible_role: str | None = "manager"
    expected_gate: str = "ALLOW"
    decision_authority: str = "KX108_ONLY"
    external_action: bool = False


def draft(assessment=None, **changes):
    kwargs = dict(
        observed_source_ref="cssa:synthetic:source",
        observed_evidence_refs=("cssa:synthetic:evidence",),
        occurred_at="2026-10-07T00:00:00+00:00",
        due_at="2026-10-20T00:00:00+00:00",
        proposed_owner_ref="CSSA_TEST_MANAGER",
    )
    kwargs.update(changes)
    return draft_cssa_historical_native_intake_v0(
        project_historical_cssa_assessment_v0(assessment or ContractAssessmentV0()),
        **kwargs
    )


def test_review_draft_uses_existing_native_intake_contract():
    result = draft()
    assert result["status"] == "NATIVE_INTAKE_DRAFT_FOR_REVIEW"
    assert verify_native_case_task_intake_plan_v0(result["native_plan"]) == (True, None)
    assert result["native_plan"].case_type == "CONTRACT_REVIEW"
    assert result["native_plan"].source_refs == ("cssa:synthetic:source",)
    assert result["native_plan"].evidence_refs == ("cssa:synthetic:evidence",)
    assert result["native_plan"].allowed_to_act is False
    assert result["canonical_intake_committed"] is False
    assert result["approval_granted"] is False
    assert result["action_candidate"] is None


def test_draft_ids_are_deterministic():
    assert draft()["native_plan"].plan_hash == draft()["native_plan"].plan_hash


def test_blocked_assessment_never_drafts_native_plan():
    result = draft(ContractAssessmentV0(contradictions=("ACTIVE_VERSION_CONFLICT",)))
    assert result["status"] == "BLOCK"
    assert result["native_plan"] is None


def test_missing_external_provenance_holds():
    result = draft(observed_source_ref="")
    assert result["status"] == "HOLD"
    assert "OBSERVED_SOURCE_REFERENCE_MISSING" in result["reasons"]


def test_missing_evidence_holds():
    result = draft(observed_evidence_refs=())
    assert result["status"] == "HOLD"


def test_naive_date_holds():
    result = draft(due_at="2026-10-20")
    assert result["status"] == "HOLD"
    assert "DUE_AT_TIMEZONE_REQUIRED" in result["reasons"]


def test_no_owner_holds():
    result = draft(proposed_owner_ref=None)
    assert result["status"] == "HOLD"
    assert "RESPONSIBLE_OWNER_NOT_BOUND" in result["reasons"]


def test_historical_expected_allow_never_becomes_approval():
    result = draft()
    assert result["native_plan"].case_type == "CONTRACT_REVIEW"
    assert result["native_plan"].allowed_to_decide is False
    assert result["native_plan"].allowed_to_act is False
    assert result["approval_granted"] is False
