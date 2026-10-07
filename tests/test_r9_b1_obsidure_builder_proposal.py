from __future__ import annotations

import dataclasses
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


BASE = "a" * 64
PATCH = "b" * 64


def _proposal(**overrides):
    data = {
        "objective": "add bounded builder contract",
        "proposal_kind": "PATCH",
        "base_commit_sha": BASE,
        "target_scope": ("scripts/example.py",),
        "files_touched": ("scripts/example.py",),
        "candidate_patch_ref": B1.BuilderPatchRef("candidate.patch", PATCH),
        "tests_proposed": ("pytest tests/test_example.py",),
        "proof_obligations": ("static check required",),
        "risk_notes": ("review generated diff",),
        "unknowns": ("runtime not executed",),
        "provider_ref": "provider-output",
        "builder_ref": "obsidure",
        "created_from": "unit-test",
        "declared_evidence": {"tests_passed": True, "verified": True},
    }
    data.update(overrides)
    return B1.build_builder_proposal(**data)


def test_deterministic_full_width_identity_and_serialization():
    a = _proposal()
    b = _proposal()
    assert a.proposal_id == b.proposal_id
    assert a.proposal_digest == b.proposal_digest
    assert len(a.proposal_digest) == 64
    assert a.to_dict()["proposal_id_bits"] == 256
    assert a.proposal_id == "obp-" + a.proposal_digest
    assert B1.canonical_json(a.to_dict()) == B1.canonical_json(b.to_dict())
    assert B1.verify_builder_proposal(a) == (True, None)


def test_identity_changes_with_patch_and_base_commit():
    baseline = _proposal()
    changed_patch = _proposal(candidate_patch_ref=B1.BuilderPatchRef("candidate.patch", "c" * 64))
    changed_base = _proposal(base_commit_sha="d" * 64)
    assert baseline.proposal_id != changed_patch.proposal_id
    assert baseline.proposal_id != changed_base.proposal_id


def test_immutable_and_defensive_copy():
    source_tests = ["pytest tests/test_example.py"]
    proposal = _proposal(tests_proposed=source_tests)
    source_tests.append("pytest tests/other.py")
    assert proposal.tests_proposed == ("pytest tests/test_example.py",)
    with pytest.raises(FrozenInstanceError):
        proposal.objective = "mutate"
    with pytest.raises(AttributeError):
        proposal.tests_proposed.append("x")
    with pytest.raises(TypeError):
        proposal.metadata["x"] = "y"


def test_unknown_kind_and_authority_injection_rejected():
    with pytest.raises(B1.BuilderProposalError, match="PROPOSAL_KIND_UNSUPPORTED"):
        _proposal(proposal_kind="FREEFORM")
    with pytest.raises(B1.BuilderProposalError, match="AUTHORITY_MUST_BE_NONE"):
        _proposal(authority="ALLOW")
    with pytest.raises(B1.BuilderProposalError, match="EXECUTION_ALLOWED_MUST_BE_FALSE"):
        _proposal(execution_allowed=True)
    with pytest.raises(B1.BuilderProposalError, match="FORBIDDEN_AUTHORITY_VALUE"):
        _proposal(provider_ref="EXECUTE")


def test_canonical_json_rejects_nan_bytes_sets_non_string_keys_and_recursive():
    with pytest.raises(B1.BuilderProposalError, match="NON_FINITE_NUMBER"):
        B1.canonical_json({"x": math.nan})
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


def test_patch_hash_mismatch_and_scope_are_rejected():
    with pytest.raises(B1.BuilderProposalError, match="candidate_patch_hash_NOT_SHA256"):
        B1.BuilderPatchRef("candidate.patch", "not-a-sha")
    with pytest.raises(B1.BuilderProposalError, match="FILES_OUTSIDE_TARGET_SCOPE"):
        _proposal(target_scope=("scripts/a.py",), files_touched=("scripts/b.py",))
    with pytest.raises(B1.BuilderProposalError, match="target_scope_TRAVERSAL"):
        _proposal(target_scope=("../escape.py",), files_touched=("../escape.py",))


def test_tests_and_proofs_are_obligations_not_authority():
    proposal = _proposal()
    payload = proposal.to_dict()
    assert payload["tests_proposed"] == ["pytest tests/test_example.py"]
    assert "tests_executed" not in payload
    assert payload["tests_are_obligations_not_authority"] is True
    assert payload["proof_claims_are_non_authoritative"] is True
    assert payload["declared_evidence"]["tests_passed"] is True
    assert payload["authority"] == "NONE"
    assert payload["execution_allowed"] is False


def test_candidate_manifest_adapter_binds_patch_base_and_scope():
    manifest = {
        "producer": "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
        "producer_authority": "NONE",
        "decision_authority": "KX108_ONLY",
        "route": "TOOLING_ENGINEERING_V1",
        "base_sha": BASE,
        "candidate_patch_mode": "REAL_UNIFIED_DIFF_V1",
        "candidate_patch": "C:/outside/candidate.patch",
        "candidate_patch_sha256": PATCH,
        "candidate_files": ["scripts/obsidure_builder_proposal_v1.py"],
        "auto_apply": False,
        "auto_commit": False,
        "auto_push": False,
        "auto_merge": False,
        "world_action": False,
    }
    proposal = B1.from_candidate_manifest(manifest, objective="canonicalize builder proposal")
    payload = proposal.to_dict()
    assert payload["proposal_kind"] == "TOOLING"
    assert payload["base_commit_sha"] == BASE
    assert payload["candidate_patch_ref"]["sha256"] == PATCH
    assert payload["candidate_patch_ref"]["patch_format"] == "REAL_UNIFIED_DIFF_V1"
    assert payload["files_touched"] == ["scripts/obsidure_builder_proposal_v1.py"]
    assert B1.verify_builder_proposal(proposal) == (True, None)


@dataclasses.dataclass
class _RepairCandidate:
    path: str
    full_content: str = "x"
    change_kind: str = "MODIFY"


@dataclasses.dataclass
class _RepairProposal:
    request_id: str = "req-1"
    proposal_id: str = "rp-1"
    engine: str = "BRODY"
    rationale: str = "repair target"
    candidate_files: list[_RepairCandidate] = dataclasses.field(default_factory=lambda: [_RepairCandidate("scripts/a.py")])
    tests_to_run: list[str] = dataclasses.field(default_factory=lambda: ["pytest tests/test_a.py"])
    confidence: str = "DECLARED_HIGH"


def test_repair_proposal_adapter_preserves_tests_as_proposed_obligations():
    proposal = B1.from_repair_proposal(_RepairProposal(), base_commit_sha=BASE)
    payload = proposal.to_dict()
    assert payload["proposal_kind"] == "REPAIR"
    assert payload["tests_proposed"] == ["pytest tests/test_a.py"]
    assert payload["files_touched"] == ["scripts/a.py"]
    assert payload["authority"] == "NONE"


@dataclasses.dataclass
class _NativeStep:
    target_path: str


@dataclasses.dataclass
class _NativePlan:
    request_id: str = "req"
    spec_id: str = "spec"
    plan_id: str = "native"
    objective: str = "native plan"
    steps: list[_NativeStep] = dataclasses.field(default_factory=lambda: [_NativeStep("periphery/a.py")])
    acceptance_criteria: list[str] = dataclasses.field(default_factory=lambda: ["unit test required"])
    missing_capabilities: list[str] = dataclasses.field(default_factory=lambda: ["no executor"])
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    canonical_write: bool = False
    world_action: bool = False


def test_native_plan_adapter_keeps_plan_non_executing():
    proposal = B1.from_native_plan(_NativePlan(), base_commit_sha=BASE)
    payload = proposal.to_dict()
    assert payload["proposal_kind"] == "NATIVE_PLAN"
    assert payload["files_touched"] == ["periphery/a.py"]
    assert payload["tests_proposed"] == ["unit test required"]
    assert payload["unknowns"] == ["no executor"]
    assert payload["execution_allowed"] is False


def test_canonical_module_static_safety_surface():
    module_path = SCRIPTS / "obsidure_builder_proposal_v1.py"
    text = module_path.read_text(encoding="utf-8")
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
    )
    for token in forbidden:
        assert token not in text
    assert B1.OBSIDURE_AUTHORITY == "NONE"
    assert B1.PROVIDER_OUTPUT_AUTHORITY == "NONE"
    assert B1.EXECUTION_ALLOWED is False
