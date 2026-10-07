from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL
from obsidure_builder_proposal_v1 import BuilderPatchRef, ObsidureBuilderProposalV1
from obsidure_governance_handoff_v1 import build_governance_handoff
from obsidure_governed_patch_prepare_adapter_v1 import (
    REASON_LEGACY_BYPASS_REJECTED,
    REASON_PATCH_DRIFT,
    REASON_SCOPE_WIDENING,
    REASON_STALE_HANDOFF,
    prepare_obsidure_governed_patch_action,
)
from obsidure_proposal_manifest_v1 import (
    ArtifactRef,
    EVIDENCE_STATUS_VERIFIED,
    EvidenceRecord,
    ObsidureProposalManifestV1,
)
from obsidure_proposal_validation_v1 import ProposalValidationResultV1, ValidationPolicy


REPO_REF = "obsidia-openjarvis-install-v0"


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture
def v2_world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / "periphery" / "alpha.txt").write_bytes(b"alpha v1\n")
    (main / "periphery" / "beta.txt").write_bytes(b"beta v1\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "r9b5@test.com")
    _git(main, "config", "user.name", "r9b5")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "r9-b5-branch", base_sha)
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha, "stores": tmp_path / "stores"}


def _patch_alpha() -> str:
    return (
        "--- a/periphery/alpha.txt\n"
        "+++ b/periphery/alpha.txt\n"
        "@@ -1 +1 @@\n"
        "-alpha v1\n"
        "+alpha v2\n"
    )


def _patch_beta() -> str:
    return (
        "--- a/periphery/beta.txt\n"
        "+++ b/periphery/beta.txt\n"
        "@@ -1 +1 @@\n"
        "-beta v1\n"
        "+beta v2\n"
    )


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _chain(base_sha: str, patch: str = "", *, scope=("periphery/alpha.txt",), metadata=None):
    patch = patch or _patch_alpha()
    proposal = ObsidureBuilderProposalV1(
        objective="Prepare governed patch from validated builder handoff",
        proposal_kind="PATCH",
        base_commit_sha=base_sha,
        target_scope=scope,
        files_touched=scope,
        candidate_patch_ref=BuilderPatchRef("candidate.patch", _sha(patch)),
        risk_notes=("governed filesystem prepare only",),
        unknowns=("execution not authorized",),
        provider_ref="OBSIDURE_PROVIDER",
        builder_ref="OBSIDURE",
        created_from="r9-b5-test",
    )
    patch_artifact = ArtifactRef(
        artifact_kind="CANDIDATE_PATCH",
        logical_ref="candidate.patch",
        content_sha256=_sha(patch),
        artifact_format="REAL_UNIFIED_DIFF_V1",
        schema_ref="REAL_UNIFIED_DIFF_V1",
    )
    evidence_artifact = ArtifactRef(
        artifact_kind="TEST_RESULT",
        logical_ref="focused.txt",
        content_sha256="b" * 64,
        artifact_format="TEXT",
    )
    evidence = EvidenceRecord(
        evidence_kind="TEST_RESULT_EVIDENCE",
        subject_ref=proposal.proposal_id,
        producer_ref="pytest",
        verification_status=EVIDENCE_STATUS_VERIFIED,
        artifact_ref=evidence_artifact,
        scope=scope,
        result="PASS",
        provenance={"base_commit_sha": base_sha},
    )
    manifest = ObsidureProposalManifestV1(
        proposal=proposal,
        candidate_artifacts=(patch_artifact, evidence_artifact),
        evidence_records=(evidence,),
        repo_identity_ref=REPO_REF,
    )
    policy = ValidationPolicy()
    validation = ProposalValidationResultV1(
        proposal_id=proposal.proposal_id,
        manifest_id=manifest.manifest_id,
        policy_id=policy.policy_id(proposal.proposal_id),
        policy_version=policy.policy_version,
        structural_status="VALID",
        evidence_status="EVIDENCE_PRESENT",
        obligation_status="OBLIGATIONS_SATISFIED",
        risk_status="RISK_NOT_REQUIRED",
        unknown_status="UNKNOWN_RECORDED",
        evidence_refs=(evidence.evidence_id,),
        validation_verdict="VALID",
    )
    handoff = build_governance_handoff(
        proposal,
        manifest,
        validation,
        source_metadata=dict(metadata or {}),
    )
    return proposal, manifest, validation, handoff


def _prepare(world, proposal, manifest, validation, handoff, patch=None, **overrides):
    return prepare_obsidure_governed_patch_action(
        handoff=handoff,
        proposal=proposal,
        manifest=manifest,
        validation=validation,
        patch_content=patch or _patch_alpha(),
        current_base_sha=overrides.get("current_base_sha", world["base_sha"]),
        current_repo_identity_ref=overrides.get("current_repo_identity_ref", REPO_REF),
        execution_worktree_path=world["exec_wt"],
        main_worktree_path=world["main"],
        branch_name="r9-b5-branch",
        stores_base_dir=world["stores"],
        session_id="r9-b5",
    )


def test_valid_handoff_matching_base_and_patch_prepares_existing_apply_patch(v2_world):
    proposal, manifest, validation, handoff = _chain(v2_world["base_sha"])
    before = (v2_world["exec_wt"] / "periphery" / "alpha.txt").read_text(encoding="utf-8")

    out = _prepare(v2_world, proposal, manifest, validation, handoff)

    assert out["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["operation_type"] == "V2_APPLY_PATCH"
    assert out["handoff_to_governed_prepare"] is True
    assert out["existing_apply_patch_rail_reused"] is True
    assert len(out["execution_authority_hash"]) == 64
    assert out["proposal_id_bound"] == proposal.proposal_id
    assert out["manifest_id_bound"] == manifest.manifest_id
    assert out["validation_id_bound"] == validation.validation_id
    assert out["handoff_id_bound"] == handoff.handoff_id
    assert out["approval_created"] is False
    assert out["binder_runtime_called"] is False
    assert out["kx108_called"] is False
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert (v2_world["exec_wt"] / "periphery" / "alpha.txt").read_text(encoding="utf-8") == before

    desc_path = v2_world["stores"] / "v2exec" / f"{out['v2_exec_id']}.json"
    descriptor = json.loads(desc_path.read_text(encoding="utf-8"))["descriptor"]
    assert descriptor["descriptor_lineage"]["builder_handoff_id"] == handoff.handoff_id


def test_base_commit_drift_rejected_before_prepare(v2_world):
    stale = "f" * 40
    proposal, manifest, validation, handoff = _chain(stale)

    out = _prepare(v2_world, proposal, manifest, validation, handoff)

    assert out["status"] == "PREPARE_REJECTED"
    assert out["reason"] == REASON_STALE_HANDOFF
    assert not (v2_world["stores"] / "v2exec").exists()


def test_patch_content_drift_rejected_before_prepare(v2_world):
    proposal, manifest, validation, handoff = _chain(v2_world["base_sha"])
    drifted = _patch_alpha().replace("alpha v2", "alpha v3")

    out = _prepare(v2_world, proposal, manifest, validation, handoff, patch=drifted)

    assert out["status"] == "PREPARE_REJECTED"
    assert out["reason"] == REASON_PATCH_DRIFT


def test_target_scope_widening_rejected(v2_world):
    proposal, manifest, validation, handoff = _chain(v2_world["base_sha"])
    widened = _patch_alpha() + _patch_beta()

    out = _prepare(v2_world, proposal, manifest, validation, handoff, patch=widened)

    assert out["status"] == "PREPARE_REJECTED"
    assert out["reason"] == REASON_PATCH_DRIFT

    p2, m2, v2, h2 = _chain(
        v2_world["base_sha"],
        widened,
        scope=("periphery/alpha.txt",),
    )
    out2 = _prepare(v2_world, p2, m2, v2, h2, patch=widened)
    assert out2["status"] == "PREPARE_REJECTED"
    assert out2["reason"] == REASON_SCOPE_WIDENING


def test_cross_object_attack_rejected(v2_world):
    proposal, manifest, validation, handoff = _chain(v2_world["base_sha"])
    other_proposal, other_manifest, other_validation, _ = _chain(v2_world["base_sha"], _patch_beta(), scope=("periphery/beta.txt",))

    assert _prepare(v2_world, other_proposal, manifest, validation, handoff)["status"] == "PREPARE_REJECTED"
    assert _prepare(v2_world, proposal, other_manifest, validation, handoff)["status"] == "PREPARE_REJECTED"
    assert _prepare(v2_world, proposal, manifest, other_validation, handoff)["status"] == "PREPARE_REJECTED"


def test_legacy_direct_bypass_rejected(v2_world):
    proposal, manifest, validation, _ = _chain(v2_world["base_sha"])
    out = prepare_obsidure_governed_patch_action(
        handoff={"legacy": "PatchProposal"},
        proposal=proposal,
        manifest=manifest,
        validation=validation,
        patch_content=_patch_alpha(),
        current_base_sha=v2_world["base_sha"],
        current_repo_identity_ref=REPO_REF,
        execution_worktree_path=v2_world["exec_wt"],
        main_worktree_path=v2_world["main"],
        branch_name="r9-b5-branch",
        stores_base_dir=v2_world["stores"],
    )
    assert out["status"] == "PREPARE_REJECTED"
    assert out["reason"] == REASON_LEGACY_BYPASS_REJECTED


def test_injected_authority_fields_have_no_effect(v2_world):
    proposal, manifest, validation, handoff = _chain(
        v2_world["base_sha"],
        metadata={"authorized": True, "approved": True, "binder": "PASS", "apply_now": True},
    )
    out = _prepare(v2_world, proposal, manifest, validation, handoff)

    assert out["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["approval_created"] is False
    assert out["kx108_called"] is False
    assert out["binder_runtime_called"] is False
    assert out["executor_invoked"] is False


def test_adapter_static_safety():
    src = (SCRIPTS / "obsidure_governed_patch_prepare_adapter_v1.py").read_text(encoding="utf-8")
    forbidden = (
        "subprocess",
        "requests",
        "urllib",
        "write_text",
        "write_bytes",
        "open(",
        "JarJar",
        "store_approval_artifact(",
        "run_and_persist_kx108",
        "pc_v2_apply_patch_execute(",
    )
    for token in forbidden:
        assert token not in src
