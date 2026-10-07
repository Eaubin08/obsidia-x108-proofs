from __future__ import annotations

import dataclasses
import inspect
import sys
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidure_builder_proposal_v1 import BuilderPatchRef, ObsidureBuilderProposalV1
from obsidure_governance_handoff_v1 import (
    HANDOFF_ID_BITS,
    HANDOFF_POLICY_SCHEMA_VERSION,
    REQUESTED_ACTION_KIND,
    SCHEMA_VERSION,
    GovernanceHandoffError,
    GovernanceHandoffPolicy,
    build_governance_handoff,
    verify_governance_handoff,
)
from obsidure_proposal_manifest_v1 import (
    ArtifactRef,
    EVIDENCE_STATUS_VERIFIED,
    EvidenceRecord,
    ObsidureProposalManifestV1,
)
from obsidure_proposal_validation_v1 import ProposalValidationResultV1, ValidationPolicy


PATCH_HASH = "a" * 64
TEST_HASH = "b" * 64
BASE_SHA = "0" * 64


def _proposal(*, patch_hash: str = PATCH_HASH, base: str = BASE_SHA) -> ObsidureBuilderProposalV1:
    return ObsidureBuilderProposalV1(
        objective="Bind validated builder proposal to future governed action",
        proposal_kind="PATCH",
        base_commit_sha=base,
        target_scope=("scripts/example.py",),
        files_touched=("scripts/example.py",),
        candidate_patch_ref=BuilderPatchRef("candidate.patch", patch_hash),
        tests_proposed=("pytest tests/test_example.py",),
        proof_obligations=("review canonical handoff",),
        risk_notes=("touches governed filesystem surface",),
        unknowns=("runtime postcondition not yet observed",),
        provider_ref="OBSIDURE_PROVIDER",
        builder_ref="OBSIDURE",
        created_from="r9-b4-test",
    )


def _manifest(proposal: ObsidureBuilderProposalV1) -> ObsidureProposalManifestV1:
    patch_ref = proposal.candidate_patch_ref
    patch_artifact = ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref="candidate.patch",
        content_sha256=patch_ref.sha256,
        artifact_format=patch_ref.patch_format,
        schema_ref=patch_ref.patch_format,
    )
    test_artifact = ArtifactRef(
        artifact_kind="TEST_RESULT",
        logical_ref="pytest-focused.txt",
        content_sha256=TEST_HASH,
        artifact_format="TEXT",
    )
    evidence = EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=proposal.proposal_id,
        producer_ref="pytest",
        verification_status=EVIDENCE_STATUS_VERIFIED,
        artifact_ref=test_artifact,
        scope=("scripts/example.py",),
        result="PASS",
        provenance={"base_commit_sha": proposal.base_commit_sha},
    )
    return ObsidureProposalManifestV1(
        proposal=proposal,
        candidate_artifacts=(patch_artifact, test_artifact),
        evidence_records=(evidence,),
        verification_obligations=("focused pytest",),
        repo_identity_ref="obsidia-openjarvis-install-v0",
    )


def _validation(
    proposal: ObsidureBuilderProposalV1,
    manifest: ObsidureProposalManifestV1,
    *,
    verdict: str = "VALID",
    policy_version: str = "R9_B3_POLICY_V1",
) -> ProposalValidationResultV1:
    policy = ValidationPolicy(policy_version=policy_version)
    return ProposalValidationResultV1(
        proposal_id=proposal.proposal_id,
        manifest_id=manifest.manifest_id,
        policy_id=policy.policy_id(proposal.proposal_id),
        policy_version=policy.policy_version,
        structural_status="VALID",
        evidence_status="EVIDENCE_PRESENT",
        obligation_status="OBLIGATIONS_SATISFIED",
        risk_status="RISK_NOT_REQUIRED",
        unknown_status="UNKNOWN_RECORDED",
        evidence_refs=tuple(record.evidence_id for record in manifest.evidence_records),
        limits=("runtime action deferred",),
        validation_verdict=verdict,
    )


def _triple():
    proposal = _proposal()
    manifest = _manifest(proposal)
    validation = _validation(proposal, manifest)
    return proposal, manifest, validation


def test_validated_proposal_creates_deterministic_handoff_contract():
    proposal, manifest, validation = _triple()
    handoff = build_governance_handoff(proposal, manifest, validation)
    payload = handoff.to_dict()

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["handoff_id"].startswith("obh-")
    assert len(payload["handoff_digest"]) == 64
    assert payload["handoff_id_bits"] == HANDOFF_ID_BITS
    assert payload["requested_action_kind"] == REQUESTED_ACTION_KIND
    assert payload["handoff_policy"]["handoff_policy_schema_version"] == HANDOFF_POLICY_SCHEMA_VERSION
    assert payload["authority"] == "NONE"
    assert payload["execution_allowed"] is False
    assert payload["runtime_called"] is False
    assert payload["governed_action_prepared"] is False
    assert payload["execution_hash_created"] is False
    assert payload["action_evidence_id"] is None

    again = build_governance_handoff(proposal, manifest, validation)
    assert again.to_dict() == payload


@pytest.mark.parametrize("verdict", ["INCOMPLETE", "INVALID", "CONFLICTING", "HELD"])
def test_non_valid_validation_fails_closed(verdict):
    proposal, manifest, _ = _triple()
    validation = _validation(proposal, manifest, verdict=verdict)
    with pytest.raises(GovernanceHandoffError, match="VALIDATION_VERDICT_NOT_VALID"):
        build_governance_handoff(proposal, manifest, validation)


def test_manifest_validation_and_proposal_must_be_same_bound_objects():
    proposal, manifest, validation = _triple()
    other = _proposal(patch_hash="c" * 64)

    with pytest.raises(GovernanceHandoffError, match="MANIFEST_PROPOSAL_BINDING_FAILED"):
        build_governance_handoff(other, manifest, validation)

    other_manifest = _manifest(other)
    with pytest.raises(GovernanceHandoffError, match="VALIDATION_PROPOSAL_ID_MISMATCH"):
        build_governance_handoff(other, other_manifest, validation)

    manifest_mismatch_validation = ProposalValidationResultV1(
        proposal_id=proposal.proposal_id,
        manifest_id=other_manifest.manifest_id,
        policy_id=validation.policy_id,
        policy_version=validation.policy_version,
        structural_status="VALID",
        evidence_status="EVIDENCE_PRESENT",
        obligation_status="OBLIGATIONS_SATISFIED",
        risk_status="RISK_NOT_REQUIRED",
        unknown_status="UNKNOWN_RECORDED",
        validation_verdict="VALID",
    )
    with pytest.raises(GovernanceHandoffError, match="VALIDATION_MANIFEST_ID_MISMATCH"):
        build_governance_handoff(proposal, manifest, manifest_mismatch_validation)


def test_handoff_verifier_rejects_scope_base_patch_and_validation_tampering():
    proposal, manifest, validation = _triple()
    payload = build_governance_handoff(proposal, manifest, validation).to_dict()

    widened = dict(payload)
    widened["target_scope"] = ["scripts/example.py", "scripts/extra.py"]
    assert verify_governance_handoff(widened, proposal, manifest, validation) == (
        False,
        "TARGET_SCOPE_MISMATCH",
    )

    wrong_base = dict(payload)
    wrong_base["base_commit_sha"] = "11111111"
    assert verify_governance_handoff(wrong_base, proposal, manifest, validation) == (
        False,
        "BASE_COMMIT_SHA_MISMATCH",
    )

    wrong_patch = dict(payload)
    wrong_patch["candidate_patch_ref"] = dict(wrong_patch["candidate_patch_ref"])
    wrong_patch["candidate_patch_ref"]["sha256"] = "d" * 64
    assert verify_governance_handoff(wrong_patch, proposal, manifest, validation) == (
        False,
        "CANDIDATE_PATCH_REF_MISMATCH",
    )

    wrong_validation = dict(payload)
    wrong_validation["validation_verdict"] = "INCOMPLETE"
    assert verify_governance_handoff(wrong_validation, proposal, manifest, validation) == (
        False,
        "VALIDATION_VERDICT_MISMATCH",
    )


def test_unknowns_risks_limits_and_evidence_are_preserved_without_authority():
    proposal, manifest, validation = _triple()
    payload = build_governance_handoff(proposal, manifest, validation).to_dict()

    assert payload["unknowns"] == ["runtime postcondition not yet observed"]
    assert payload["risk_notes"] == ["touches governed filesystem surface"]
    assert payload["limits"] == ["runtime action deferred"]
    assert payload["evidence_refs"] == [manifest.evidence_records[0].evidence_id]
    assert payload["source_metadata_is_authority"] is False


def test_policy_or_validation_policy_change_changes_handoff_identity():
    proposal, manifest, validation = _triple()
    baseline = build_governance_handoff(proposal, manifest, validation)
    policy_changed = build_governance_handoff(
        proposal,
        manifest,
        validation,
        handoff_policy=GovernanceHandoffPolicy(policy_version="R9_B4_POLICY_V1_ALT"),
    )
    validation_changed = build_governance_handoff(
        proposal,
        manifest,
        _validation(proposal, manifest, policy_version="R9_B3_POLICY_V1_ALT"),
    )

    assert policy_changed.handoff_id != baseline.handoff_id
    assert validation_changed.handoff_id != baseline.handoff_id


def test_source_metadata_is_non_authoritative_and_forbidden_words_still_fail_closed():
    proposal, manifest, validation = _triple()
    handoff = build_governance_handoff(
        proposal,
        manifest,
        validation,
        source_metadata={"authorized": True, "apply_now": True, "legacy_pass": True},
    )
    payload = handoff.to_dict()

    assert payload["source_metadata"] == {
        "apply_now": True,
        "authorized": True,
        "legacy_pass": True,
    }
    assert payload["source_metadata_is_authority"] is False
    assert payload["authority"] == "NONE"
    assert payload["execution_allowed"] is False

    with pytest.raises(Exception):
        build_governance_handoff(
            proposal,
            manifest,
            validation,
            source_metadata={"execute": True},
        )


def test_handoff_object_is_frozen():
    proposal, manifest, validation = _triple()
    handoff = build_governance_handoff(proposal, manifest, validation)

    with pytest.raises(dataclasses.FrozenInstanceError):
        handoff.authority = "NONE"


def test_no_runtime_or_filesystem_side_effect_surfaces_in_handoff_module():
    import obsidure_governance_handoff_v1 as module

    src = Path(inspect.getsourcefile(module)).read_text(encoding="utf-8")
    forbidden = (
        "subprocess",
        "requests",
        "urllib",
        "write_text",
        "write_bytes",
        "open(",
        "eval(",
        "exec(",
        "commit(",
        "push(",
        "merge(",
    )
    for token in forbidden:
        assert token not in src
