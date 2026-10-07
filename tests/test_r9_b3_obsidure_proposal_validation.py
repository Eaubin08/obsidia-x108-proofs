from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidure_builder_proposal_v1 as B1
import obsidure_proposal_manifest_v1 as B2
import obsidure_proposal_validation_v1 as B3


BASE = "a" * 64
PATCH = "b" * 64
TEST_HASH = "c" * 64
LEAN_HASH = "d" * 64


def _proposal(**overrides):
    data = {
        "objective": "validate proposal evidence",
        "proposal_kind": "TOOLING",
        "base_commit_sha": BASE,
        "target_scope": ("scripts/obsidure_proposal_validation_v1.py",),
        "files_touched": ("scripts/obsidure_proposal_validation_v1.py",),
        "candidate_patch_ref": B1.BuilderPatchRef("candidate.patch", PATCH),
        "tests_proposed": ("pytest tests/test_r9_b3_obsidure_proposal_validation.py",),
        "proof_obligations": ("lean proof required",),
        "risk_notes": ("review generated validation gate",),
        "provider_ref": "OBSIDURE",
        "builder_ref": "OBSIDURE",
        "created_from": "unit-test",
    }
    data.update(overrides)
    return B1.build_builder_proposal(**data)


def _patch_artifact():
    return B2.ArtifactRef("CANDIDATE_PATCH", "candidate.patch", PATCH, artifact_format="REAL_UNIFIED_DIFF_V1")


def _test_artifact(sha=TEST_HASH):
    return B2.ArtifactRef("TEST_RESULT", "pytest-result.json", sha, artifact_format="JSON")


def _lean_artifact(sha=LEAN_HASH):
    return B2.ArtifactRef("LEAN_ARTIFACT", "proof.lean.json", sha, artifact_format="JSON")


def _test_evidence(proposal, *, result="PASS", status="VERIFIED", base=BASE):
    return B2.EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=proposal.proposal_id,
        artifact_ref=_test_artifact(),
        producer_ref="pytest",
        verification_status=status,
        scope=proposal.files_touched,
        result=result,
        provenance={"base_commit_sha": base},
    )


def _lean_evidence(proposal, *, subject=None):
    return B2.EvidenceRecord(
        evidence_kind="LEAN_EVIDENCE",
        subject_ref=subject or proposal.proposal_id,
        artifact_ref=_lean_artifact(),
        producer_ref="lake",
        verification_status="VERIFIED",
        scope=proposal.files_touched,
        result="PASS",
        provenance={"base_commit_sha": BASE},
    )


def _manifest(proposal, evidence=()):
    return B2.build_proposal_manifest(
        proposal,
        candidate_artifacts=(_patch_artifact(),),
        evidence_records=tuple(evidence),
        verification_obligations=proposal.tests_proposed + proposal.proof_obligations,
        repo_identity_ref="repo",
    )


def _policy(proposal, *, allow_observed=False, optional=False, version="R9_B3_POLICY_V1"):
    return B3.ValidationPolicy(
        policy_version=version,
        obligations=(
            B3.ValidationObligation(
                "UNIT_TEST",
                proposal.tests_proposed[0],
                scope=proposal.files_touched,
                required=not optional,
                expected_evidence_kind="TEST_RESULT_EVIDENCE",
                allow_observed=allow_observed,
            ),
            B3.ValidationObligation(
                "LEAN_PROOF",
                proposal.proof_obligations[0],
                scope=proposal.files_touched,
                required=True,
                expected_evidence_kind="LEAN_EVIDENCE",
            ),
        ),
    )


def test_valid_fully_satisfied_proposal_is_deterministic():
    proposal = _proposal()
    manifest = _manifest(proposal, (_test_evidence(proposal), _lean_evidence(proposal)))
    policy = _policy(proposal)
    a = B3.validate_obsidure_proposal(proposal, manifest, validation_policy=policy)
    b = B3.validate_obsidure_proposal(proposal, manifest, validation_policy=policy)
    assert a.validation_verdict == "VALID"
    assert a.validation_id == b.validation_id
    assert len(a.validation_digest) == 64
    assert a.to_dict()["validation_id_bits"] == 256
    assert a.to_dict()["validation_id_differs_from_action_evidence_id"] is True


def test_missing_required_obligation_is_incomplete():
    proposal = _proposal()
    result = B3.validate_obsidure_proposal(proposal, _manifest(proposal), validation_policy=_policy(proposal))
    assert result.validation_verdict == "INCOMPLETE"
    assert result.missing_obligations


def test_declared_only_evidence_cannot_satisfy_required_test():
    proposal = _proposal()
    declared = B2.evidence_from_provider_declaration(
        proposal=proposal,
        producer_ref="provider",
        claims={"tests_passed": True},
    )
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (declared, _lean_evidence(proposal))),
        validation_policy=_policy(proposal),
    )
    assert result.validation_verdict == "INCOMPLETE"
    assert any("DECLARED_EVIDENCE_INSUFFICIENT" in item for item in result.limits)


def test_wrong_evidence_type_and_wrong_base_are_not_satisfied():
    proposal = _proposal()
    wrong_type = _lean_evidence(proposal)
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (wrong_type,)),
        validation_policy=B3.ValidationPolicy(
            obligations=(B3.ValidationObligation("UNIT_TEST", "pytest", scope=proposal.files_touched),)
        ),
    )
    assert result.validation_verdict == "INCOMPLETE"
    assert any("EVIDENCE_KIND_INCOMPATIBLE" in item for item in result.limits)

    wrong_base = _test_evidence(proposal, base="e" * 64)
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (wrong_base, _lean_evidence(proposal))),
        validation_policy=_policy(proposal),
    )
    assert result.validation_verdict == "INCOMPLETE"
    assert any("EVIDENCE_BASE_COMMIT_MISMATCH" in item for item in result.limits)


def test_wrong_manifest_binding_is_conflicting():
    proposal = _proposal()
    other = _proposal(base_commit_sha="e" * 64)
    manifest = _manifest(other, (_test_evidence(other), _lean_evidence(other)))
    result = B3.validate_obsidure_proposal(proposal, manifest, validation_policy=_policy(proposal))
    assert result.validation_verdict == "CONFLICTING"
    assert result.conflicts


def test_cross_proposal_evidence_and_lean_wrong_subject_rejected_by_manifest():
    proposal = _proposal()
    other = _proposal(base_commit_sha="e" * 64)
    with pytest.raises(B2.ProposalManifestError, match="EVIDENCE_SUBJECT_MISMATCH"):
        _manifest(proposal, (_test_evidence(other),))
    with pytest.raises(B2.ProposalManifestError, match="EVIDENCE_SUBJECT_MISMATCH"):
        _manifest(proposal, (_lean_evidence(proposal, subject=other.proposal_id),))


def test_optional_missing_visible_but_non_blocking_when_required_proof_present():
    proposal = _proposal()
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (_lean_evidence(proposal),)),
        validation_policy=_policy(proposal, optional=True),
    )
    assert result.validation_verdict == "VALID"
    assert any("OPTIONAL_OBLIGATION_UNSATISFIED" in item for item in result.limits)


def test_unknown_required_field_held_by_policy():
    proposal = _proposal(unknowns=("runtime target unresolved",))
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (_test_evidence(proposal), _lean_evidence(proposal))),
        validation_policy=B3.ValidationPolicy(
            obligations=_policy(proposal).obligations,
            require_no_unknowns=True,
        ),
    )
    assert result.validation_verdict == "HELD"
    assert result.unknown_status == "UNKNOWN_HELD"


def test_conflicting_pass_fail_evidence_detected():
    proposal = _proposal()
    fail = B2.EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=proposal.proposal_id,
        artifact_ref=_test_artifact("e" * 64),
        producer_ref="pytest",
        verification_status="VERIFIED",
        scope=proposal.files_touched,
        result="FAIL",
        provenance={"base_commit_sha": BASE},
    )
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (_test_evidence(proposal), fail, _lean_evidence(proposal))),
        validation_policy=_policy(proposal),
    )
    assert result.validation_verdict == "CONFLICTING"
    assert result.conflicts


def test_policy_version_change_changes_validation_id():
    proposal = _proposal()
    manifest = _manifest(proposal, (_test_evidence(proposal), _lean_evidence(proposal)))
    a = B3.validate_obsidure_proposal(proposal, manifest, validation_policy=_policy(proposal))
    b = B3.validate_obsidure_proposal(proposal, manifest, validation_policy=_policy(proposal, version="R9_B3_POLICY_V2"))
    assert a.validation_id != b.validation_id
    assert a.policy_version != b.policy_version


def test_observed_policy_and_no_action_authority():
    proposal = _proposal()
    observed = _test_evidence(proposal, status="OBSERVED")
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (observed, _lean_evidence(proposal))),
        validation_policy=_policy(proposal, allow_observed=True),
    )
    assert result.validation_verdict == "VALID"
    assert result.authority == "NONE"
    assert result.execution_allowed is False


def test_immutability_and_static_safety_surface():
    proposal = _proposal()
    result = B3.validate_obsidure_proposal(
        proposal,
        _manifest(proposal, (_test_evidence(proposal), _lean_evidence(proposal))),
        validation_policy=_policy(proposal),
    )
    with pytest.raises(FrozenInstanceError):
        result.validation_verdict = "INVALID"
    with pytest.raises(AttributeError):
        result.evidence_refs.append("x")
    text = (SCRIPTS / "obsidure_proposal_validation_v1.py").read_text(encoding="utf-8")
    forbidden = (
        "subprocess",
        "requests",
        "urllib",
        ".write_text(",
        ".write_bytes(",
        "open(",
        "apply(",
        "execute(",
        "commit(",
        "push(",
        "merge(",
        "JarJar",
    )
    for token in forbidden:
        assert token not in text
    assert B3.EXECUTION_ALLOWED is False
    assert B3.VALIDATION_ID_BITS == 256
