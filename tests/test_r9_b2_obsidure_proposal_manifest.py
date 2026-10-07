from __future__ import annotations

import math
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


BASE = "a" * 64
PATCH = "b" * 64
TEST_HASH = "c" * 64


def _proposal(**overrides):
    data = {
        "objective": "bind proposal provenance",
        "proposal_kind": "TOOLING",
        "base_commit_sha": BASE,
        "target_scope": ("scripts/obsidure_proposal_manifest_v1.py",),
        "files_touched": ("scripts/obsidure_proposal_manifest_v1.py",),
        "candidate_patch_ref": B1.BuilderPatchRef("candidate.patch", PATCH),
        "tests_proposed": ("pytest tests/test_r9_b2_obsidure_proposal_manifest.py",),
        "proof_obligations": ("static safety scan",),
        "provider_ref": "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
        "builder_ref": "OBSIDURE",
        "created_from": "unit-test",
    }
    data.update(overrides)
    return B1.build_builder_proposal(**data)


def _patch_artifact(sha=PATCH):
    return B2.ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref="candidate.patch",
        content_sha256=sha,
        size_bytes=123,
        artifact_format="REAL_UNIFIED_DIFF_V1",
        schema_ref="REAL_UNIFIED_DIFF_V1",
    )


def _test_artifact(sha=TEST_HASH):
    return B2.ArtifactRef(
        artifact_kind="TEST_RESULT",
        logical_ref="pytest-result.json",
        content_sha256=sha,
        artifact_format="JSON",
        schema_ref="PYTEST_RESULT",
    )


def _manifest(proposal=None, evidence=(), artifacts=None):
    proposal = proposal or _proposal()
    artifacts = (_patch_artifact(),) if artifacts is None else artifacts
    return B2.build_proposal_manifest(
        proposal,
        candidate_artifacts=artifacts,
        evidence_records=evidence,
        verification_obligations=proposal.tests_proposed + proposal.proof_obligations,
        repo_identity_ref="repo:obsidia-openjarvis-install-v0",
    )


def test_same_manifest_same_id_and_digest():
    proposal = _proposal()
    a = _manifest(proposal)
    b = _manifest(proposal)
    assert a.manifest_id == b.manifest_id
    assert a.manifest_digest == b.manifest_digest
    assert len(a.manifest_digest) == 64
    assert a.to_dict()["manifest_id_bits"] == 256
    assert a.manifest_id == "obm-" + a.manifest_digest
    assert B2.verify_proposal_manifest(a, proposal) == (True, None)


def test_different_evidence_and_different_proposal_change_manifest_id():
    proposal = _proposal()
    baseline = _manifest(proposal)
    evidence = (
        B2.evidence_from_test_result_artifact(
            proposal=proposal,
            artifact_ref=_test_artifact(),
            producer_ref="pytest",
            scope=("scripts/obsidure_proposal_manifest_v1.py",),
            result="PASS",
            verified=True,
        ),
    )
    with_evidence = _manifest(proposal, evidence=evidence)
    different_proposal = _proposal(base_commit_sha="d" * 64)
    assert baseline.manifest_id != with_evidence.manifest_id
    assert baseline.manifest_id != _manifest(different_proposal).manifest_id


def test_proposal_substitution_and_digest_swap_rejected():
    proposal = _proposal()
    other = _proposal(base_commit_sha="d" * 64)
    manifest = _manifest(proposal).to_dict()
    assert B2.verify_proposal_manifest(manifest, other)[1] == "PROPOSAL_ID_MISMATCH"
    tampered = dict(manifest)
    tampered["proposal_digest"] = other.proposal_digest
    assert B2.verify_proposal_manifest(tampered, proposal)[1] == "PROPOSAL_DIGEST_MISMATCH"


def test_base_scope_and_patch_mismatch_rejected():
    proposal = _proposal()
    manifest = _manifest(proposal).to_dict()
    bad_base = dict(manifest)
    bad_base["base_commit_sha"] = "d" * 64
    assert B2.verify_proposal_manifest(bad_base, proposal)[1] == "BASE_COMMIT_MISMATCH"
    bad_scope = dict(manifest)
    bad_scope["target_scope"] = ["scripts/other.py"]
    assert B2.verify_proposal_manifest(bad_scope, proposal)[1] == "TARGET_SCOPE_MISMATCH"
    with pytest.raises(B2.ProposalManifestError, match="PATCH_HASH_MISMATCH"):
        _manifest(proposal, artifacts=(_patch_artifact("e" * 64),))


def test_artifact_content_change_detected_and_filename_only_rejected():
    proposal = _proposal()
    baseline = _manifest(proposal)
    changed = _manifest(proposal, artifacts=(_patch_artifact(PATCH), _test_artifact("e" * 64)))
    assert baseline.manifest_id != changed.manifest_id
    with pytest.raises(B2.ProposalManifestError, match="content_sha256_REQUIRED"):
        B2.ArtifactRef("TEST_RESULT", "pytest-result.json", "")


def test_provider_tests_passed_stays_declared_and_verified_requires_typed_artifact():
    proposal = _proposal()
    declared = B2.evidence_from_provider_declaration(
        proposal=proposal,
        producer_ref="provider",
        claims={"tests_passed": True, "safe": True, "verified": True},
    )
    assert declared.verification_status == "DECLARED"
    assert declared.artifact_ref is None
    with pytest.raises(B2.ProposalManifestError, match="BOUND_ARTIFACT_REQUIRED_FOR_EVIDENCE"):
        B2.EvidenceRecord(
            evidence_kind="TEST_RESULT_EVIDENCE",
            subject_ref=proposal.proposal_id,
            producer_ref="pytest",
            verification_status="VERIFIED",
        )
    observed = B2.evidence_from_test_result_artifact(
        proposal=proposal,
        artifact_ref=_test_artifact(),
        producer_ref="pytest",
        verified=True,
    )
    assert observed.verification_status == "VERIFIED"


def test_evidence_subject_swap_rejected_and_changes_identity():
    proposal = _proposal()
    other = _proposal(base_commit_sha="d" * 64)
    evidence = B2.evidence_from_test_result_artifact(
        proposal=proposal,
        artifact_ref=_test_artifact(),
        producer_ref="pytest",
    )
    swapped = B2.EvidenceRecord(
        evidence_kind=evidence.evidence_kind,
        subject_ref=other.proposal_id,
        producer_ref=evidence.producer_ref,
        verification_status=evidence.verification_status,
        artifact_ref=evidence.artifact_ref,
    )
    assert evidence.evidence_id != swapped.evidence_id
    with pytest.raises(B2.ProposalManifestError, match="EVIDENCE_SUBJECT_MISMATCH"):
        _manifest(proposal, evidence=(swapped,))


def test_immutability_and_defensive_copies():
    proposal = _proposal()
    evidence_list = [B2.evidence_from_provider_declaration(proposal=proposal, producer_ref="p", claims={"x": "y"})]
    manifest = _manifest(proposal, evidence=evidence_list)
    evidence_list.append(B2.evidence_from_provider_declaration(proposal=proposal, producer_ref="p2", claims={"x": "z"}))
    assert len(manifest.evidence_records) == 1
    with pytest.raises(FrozenInstanceError):
        manifest.repo_identity_ref = "other"
    with pytest.raises(AttributeError):
        manifest.evidence_records.append("x")
    with pytest.raises(TypeError):
        manifest.evidence_records[0].provenance["x"] = "z"


def test_strict_json_rejection_and_size_bounds():
    with pytest.raises(B1.BuilderProposalError, match="NON_FINITE_NUMBER"):
        B1.canonical_json({"x": math.inf})
    with pytest.raises(B1.BuilderProposalError, match="BYTES_FORBIDDEN"):
        B1.canonical_json({"x": b"raw"})
    with pytest.raises(B1.BuilderProposalError, match="SET_FORBIDDEN"):
        B1.canonical_json({"x": {"a"}})
    with pytest.raises(B1.BuilderProposalError, match="NON_STRING_KEY"):
        B1.canonical_json({1: "x"})
    recursive = {}
    recursive["self"] = recursive
    with pytest.raises(B1.BuilderProposalError, match="RECURSIVE_STRUCTURE"):
        B1.canonical_json(recursive)
    proposal = _proposal()
    too_many = tuple(
        B2.evidence_from_provider_declaration(proposal=proposal, producer_ref=f"p{i}", claims={"i": i})
        for i in range(65)
    )
    with pytest.raises(B2.ProposalManifestError, match="evidence_records_TOO_LONG"):
        _manifest(proposal, evidence=too_many)


def test_candidate_manifest_adapter_binds_patch_and_classifies_declarations():
    proposal = _proposal()
    manifest = B2.from_candidate_manifest(
        {
            "producer": "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
            "producer_authority": "NONE",
            "decision_authority": "KX_ONLY_DECLARATIVE",
            "base_sha": BASE,
            "candidate_patch": "candidate.patch",
            "candidate_patch_sha256": PATCH,
            "candidate_patch_mode": "REAL_UNIFIED_DIFF_V1",
            "candidate_files": list(proposal.files_touched),
            "auto_apply": False,
            "auto_commit": False,
            "auto_push": False,
            "auto_merge": False,
            "world_action": False,
        },
        proposal,
        repo_identity_ref="repo",
    )
    payload = manifest.to_dict()
    assert payload["candidate_artifacts"][0]["artifact_kind"] == "CANDIDATE_PATCH"
    assert payload["evidence_records"][0]["verification_status"] == "DECLARED"
    assert payload["r8_action_evidence_id"] is None
    assert B2.verify_proposal_manifest(manifest, proposal) == (True, None)


def test_manifest_authority_and_execution_are_frozen():
    proposal = _proposal()
    with pytest.raises(B2.ProposalManifestError, match="MANIFEST_AUTHORITY_MUST_BE_NONE"):
        B2.ObsidureProposalManifestV1(proposal=proposal, authority="ALLOW")
    with pytest.raises(B2.ProposalManifestError, match="MANIFEST_EXECUTION_ALLOWED_MUST_BE_FALSE"):
        B2.ObsidureProposalManifestV1(proposal=proposal, execution_allowed=True)
    with pytest.raises(B2.ProposalManifestError, match="EVIDENCE_AUTHORITY_MUST_BE_NONE"):
        B2.EvidenceRecord(
            evidence_kind="PROVIDER_DECLARATION",
            subject_ref=proposal.proposal_id,
            producer_ref="p",
            verification_status="DECLARED",
            authority="ALLOW",
        )


def test_static_safety_surface():
    text = (SCRIPTS / "obsidure_proposal_manifest_v1.py").read_text(encoding="utf-8")
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
    assert B2.AUTHORITY_NONE == "NONE"
    assert B2.EXECUTION_ALLOWED is False
    assert B2.MANIFEST_ID_BITS == 256
