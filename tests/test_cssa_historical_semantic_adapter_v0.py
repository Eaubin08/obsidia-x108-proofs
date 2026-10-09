"""Semantic boundary tests using structural replicas of historical CSSA dataclasses.

These are contract tests, NOT a replay of original F3F/F3G implementation.
"""
from dataclasses import dataclass
import pytest
from periphery.cssa_historical_semantic_adapter_v0 import (
    project_historical_cssa_assessment_v0, verify_historical_cssa_semantic_projection_v0,
)


@dataclass(frozen=True)
class ContractAssessmentV0:
    case_id: str = "contract-001"
    assessed_at: str = "2026-10-07"
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ("sim:contract:001",)
    responsible_role: str | None = "ADMIN"
    expected_gate: str = "ALLOW"
    decision_authority: str = "KX108_ONLY"
    external_action: bool = False


@dataclass(frozen=True)
class InstitutionalAssessmentV0(ContractAssessmentV0):
    pass


@dataclass(frozen=True)
class ComplianceAssessmentV0(ContractAssessmentV0):
    pass


@dataclass(frozen=True)
class RootCauseAssessmentV0(ContractAssessmentV0):
    pass


@dataclass(frozen=True)
class BuvetteAssessmentV0(ContractAssessmentV0):
    pass


@dataclass(frozen=True)
class StressAssessmentV0:
    scenario_id: str = "stress-001"
    event_date: str = "2026-10-07"
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ("sim:stress:001",)
    conflicts: tuple[str, ...] = ()
    expected_gate: str = "ALLOW"


@pytest.mark.parametrize("assessment", [
    ContractAssessmentV0(), ComplianceAssessmentV0(),
    InstitutionalAssessmentV0(), RootCauseAssessmentV0(),
    BuvetteAssessmentV0(), StressAssessmentV0(),
])
def test_all_original_signature_families_are_non_sovereign(assessment):
    result = project_historical_cssa_assessment_v0(assessment)
    assert verify_historical_cssa_semantic_projection_v0(result)
    assert result.disposition == "HOLD"
    assert result.source_expected_gate == "ALLOW"
    assert result.canonical_intake_allowed is False
    assert result.action_candidate is None


def test_conflicts_block_even_if_original_fixture_expected_allow():
    result = project_historical_cssa_assessment_v0(
        ContractAssessmentV0(contradictions=("DUPLICATE_ACTIVE_CONTRACT",)))
    assert result.disposition == "BLOCK"


def test_stress_resource_conflict_blocks():
    result = project_historical_cssa_assessment_v0(
        StressAssessmentV0(conflicts=("STADIUM_OVERLOAD",)))
    assert result.disposition == "BLOCK"
    assert "CONTRADICTION:RESOURCE_CONFLICTS_PRESENT" in result.reasons


def test_missing_evidence_holds():
    result = project_historical_cssa_assessment_v0(
        ContractAssessmentV0(evidence_refs=()))
    assert result.disposition == "HOLD"
    assert "EVIDENCE_NOT_PROVIDED" in result.reasons


def test_unknown_type_rejected():
    with pytest.raises(ValueError, match="UNSUPPORTED_ASSESSMENT_TYPE"):
        project_historical_cssa_assessment_v0({"case_id": "one"})


def test_authority_escalation_rejected():
    with pytest.raises(ValueError, match="AUTHORITY_MISMATCH"):
        project_historical_cssa_assessment_v0(
            ContractAssessmentV0(decision_authority="CSSA_ONLY"))


def test_external_action_rejected():
    with pytest.raises(ValueError, match="EXTERNAL_ACTION_FORBIDDEN"):
        project_historical_cssa_assessment_v0(
            ContractAssessmentV0(external_action=True))


def test_unknown_and_risk_hold_for_human_review():
    result = project_historical_cssa_assessment_v0(
        InstitutionalAssessmentV0(
            unknowns=("REAL_INSTITUTIONAL_SCOPE",), risk_flags=("DEADLINE_NEAR",)))
    assert result.disposition == "HOLD"
    assert len(result.reasons) == 2
