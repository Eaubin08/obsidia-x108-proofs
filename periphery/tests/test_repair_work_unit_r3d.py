from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


import obsidia_isolated_work_unit_v0 as _WU  # noqa: E402
import obsidia_repair_execution_adapter_v0 as _RA  # noqa: E402


TARGET = "periphery/agents/r3d_repair_target.py"

BEFORE = b"VALUE = 1\n"
AFTER = b"VALUE = 2\n"


def _git(cwd: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert p.returncode == 0, (
        args,
        p.stdout,
        p.stderr,
    )

    return p.stdout.strip()


def _make_work_unit(tmp_path: Path):
    main = tmp_path / "main"
    main.mkdir()

    _git(main, "init")
    _git(main, "config", "user.email", "r3d@example.invalid")
    _git(main, "config", "user.name", "R3D Test")

    target = main / TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(BEFORE)

    _git(main, "add", ".")
    _git(main, "commit", "-m", "r3d base")

    base_sha = _git(main, "rev-parse", "HEAD")

    created = _WU.create_isolated_work_unit(
        repo_root=main,
        main_worktree_path=main,
        base_sha=base_sha,
        branch_name="r3d-repair-work-unit",
        worktree_path=tmp_path / "execution-worktree",
        work_unit_id="wu-r3d",
    )

    assert created["status"] == _WU.WORK_UNIT_CREATED, created

    work_unit = created["work_unit"]

    assert isinstance(
        work_unit,
        _WU.IsolatedWorkUnit,
    )

    assert (
        Path(work_unit.worktree_path) / TARGET
    ).read_bytes() == BEFORE

    return main, work_unit


def _repair_material(tmp_path: Path):
    base_sha256 = hashlib.sha256(BEFORE).hexdigest()
    source_sha256 = hashlib.sha256(AFTER).hexdigest()

    request = {
        "request_id": "rr_r3d",
        "objective": "update bounded repair target",
        "repo_targets": [TARGET],
    }

    proposal = {
        "proposal_id": "rp_r3d",
        "request_id": "rr_r3d",
        "rationale": "bounded repair",
        "candidate_files": [{
            "path": TARGET,
            "full_content": AFTER.decode("utf-8"),
            "change_kind": "MODIFY",
            "base_sha256": base_sha256,
            "rationale": "replace bounded value",
        }],
        "tests_to_run": [],
        "confidence": "HIGH",
    }

    c278 = {
        "stage": "C278",
        "phase": "PROPOSAL_MEANING",
        "evidence": "CONTINUOUS",
        "request_id": "rr_r3d",
        "proposal_id": "rp_r3d",
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
    }

    sandbox = tmp_path / "repair-sandbox"
    artifact = sandbox / TARGET
    artifact.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    artifact.write_bytes(AFTER)

    verdict = {
        "verdict_id": "rv_r3d",
        "request_id": "rr_r3d",
        "proposal_id": "rp_r3d",
        "status": "PASS",
        "sandbox_dir": str(sandbox),
        "errors": [],
        "tested_artifacts": [{
            "path": TARGET,
            "sha256": source_sha256,
        }],
    }

    return request, proposal, c278, verdict


def test_r3d_repair_verdict_uses_real_work_unit_and_reaches_eah(
    tmp_path: Path,
):
    _main, work_unit = _make_work_unit(tmp_path)

    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    execution_target = (
        Path(work_unit.worktree_path)
        / TARGET
    )

    before = execution_target.read_bytes()

    result = _RA.prepare_repair_verdict_in_work_unit(
        request=request,
        proposal=proposal,
        c278_evidence=c278,
        verdict=verdict,
        work_unit=work_unit,
        ledger_dir=tmp_path / "ledger",
        selector_dir=tmp_path / "selector",
        execution_dir=tmp_path / "execution-store",
        pre_execution_context_dir=tmp_path / "pec",
    )

    assert result["status"] == _RA.STATUS_EXEC_READY, result

    assert result["work_unit_id"] == "wu-r3d"
    assert result["repair_handoff_status"] == "REPAIR_HANDOFF_READY"
    assert result["repair_request_id"] == "rr_r3d"
    assert result["repair_proposal_id"] == "rp_r3d"
    assert result["repair_verdict_id"] == "rv_r3d"

    expected_source_sha = hashlib.sha256(
        AFTER
    ).hexdigest()

    assert (
        result["repair_source_content_sha256"]
        == expected_source_sha
    )

    assert (
        result["source_content_sha256"]
        == expected_source_sha
    )

    assert (
        result["target_pre_sha256"]
        == hashlib.sha256(BEFORE).hexdigest()
    )

    assert result["sha256_triple_assert"] == "PASS"

    eah = result["execution_authority_hash"]

    assert len(eah) == 64
    assert all(
        c in "0123456789abcdef"
        for c in eah
    )

    # PREPARE only.
    assert result["write_capability"] is False
    assert result["target_mutated"] is False
    assert result["human_approval_present"] is False
    assert result["kx108_invoked"] is False

    # Absolutely no target mutation during R3D.
    assert execution_target.read_bytes() == before

    # Worktree remains clean.
    assert (
        _git(
            Path(work_unit.worktree_path),
            "status",
            "--porcelain",
        )
        == ""
    )


def test_r3d_refuses_non_work_unit_handle(tmp_path: Path):
    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    result = _RA.prepare_repair_verdict_in_work_unit(
        request=request,
        proposal=proposal,
        c278_evidence=c278,
        verdict=verdict,
        work_unit={
            "worktree_path": str(tmp_path),
            "branch_name": "forged",
            "base_sha": "0" * 40,
        },
    )

    assert result["status"] == _RA.STATUS_PREP_HOLD
    assert result["reason"] == "WORK_UNIT_HANDLE_REQUIRED"
    assert result["write_capability"] is False
    assert result["target_mutated"] is False
    assert result["kx108_invoked"] is False



def _runtime_snapshot(
    request,
    proposal,
    c278,
    verdict,
    **overrides,
):
    snap = {
        "status": "REPAIR_RUNTIME_EVIDENCE_SNAPSHOT",

        "request": request,
        "proposal": proposal,
        "c278_evidence": c278,
        "verdict": verdict,

        "readonly": True,
        "authority": "NON_SOVEREIGN",
        "decision_authority": "KX108_ONLY",

        "execution_authority": False,
        "work_unit_bound": False,
        "human_approval_present": False,
        "kx108_invoked": False,
        "target_mutated": False,
    }

    snap.update(overrides)
    return snap


def test_r3e2_runtime_snapshot_reaches_r3d_and_eah(
    tmp_path: Path,
):
    _main, work_unit = _make_work_unit(tmp_path)

    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    snapshot = _runtime_snapshot(
        request,
        proposal,
        c278,
        verdict,
    )

    execution_target = (
        Path(work_unit.worktree_path)
        / TARGET
    )

    before = execution_target.read_bytes()

    result = _RA.prepare_repair_runtime_snapshot_in_work_unit(
        snapshot=snapshot,
        work_unit=work_unit,
        ledger_dir=tmp_path / "ledger-r3e2",
        selector_dir=tmp_path / "selector-r3e2",
        execution_dir=tmp_path / "execution-r3e2",
        pre_execution_context_dir=tmp_path / "pec-r3e2",
    )

    assert result["status"] == _RA.STATUS_EXEC_READY, result

    assert result["work_unit_id"] == work_unit.work_unit_id

    assert result["repair_request_id"] == "rr_r3d"
    assert result["repair_proposal_id"] == "rp_r3d"
    assert result["repair_verdict_id"] == "rv_r3d"

    eah = result["execution_authority_hash"]

    assert len(eah) == 64
    assert all(
        c in "0123456789abcdef"
        for c in eah
    )

    # Still PREPARE only.
    assert result["write_capability"] is False
    assert result["target_mutated"] is False
    assert result["human_approval_present"] is False
    assert result["kx108_invoked"] is False

    # No mutation occurred while consuming the runtime snapshot.
    assert execution_target.read_bytes() == before

    assert (
        _git(
            Path(work_unit.worktree_path),
            "status",
            "--porcelain",
        )
        == ""
    )


def test_r3e2_rejects_embedded_execution_context(
    tmp_path: Path,
):
    _main, work_unit = _make_work_unit(tmp_path)

    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    snapshot = _runtime_snapshot(
        request,
        proposal,
        c278,
        verdict,
        execution_worktree_path="FORGED",
    )

    result = _RA.prepare_repair_runtime_snapshot_in_work_unit(
        snapshot=snapshot,
        work_unit=work_unit,
    )

    assert result["status"] == _RA.STATUS_PREP_HOLD

    assert (
        result["reason"]
        == "REPAIR_RUNTIME_SNAPSHOT_CONTAINS_EXECUTION_CONTEXT"
    )

    assert result["target_mutated"] is False
    assert result["kx108_invoked"] is False


def test_r3e2_rejects_incomplete_runtime_snapshot(
    tmp_path: Path,
):
    _main, work_unit = _make_work_unit(tmp_path)

    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    snapshot = _runtime_snapshot(
        request,
        proposal,
        c278,
        verdict,
    )

    snapshot["verdict"] = None

    result = _RA.prepare_repair_runtime_snapshot_in_work_unit(
        snapshot=snapshot,
        work_unit=work_unit,
    )

    assert result["status"] == _RA.STATUS_PREP_HOLD

    assert (
        result["reason"]
        == "REPAIR_RUNTIME_SNAPSHOT_ARTIFACT_MISSING_OR_MALFORMED"
    )

    assert result["artifact"] == "verdict"
    assert result["target_mutated"] is False
    assert result["kx108_invoked"] is False


def test_r3e2_does_not_bypass_r3d_provenance_validation(
    tmp_path: Path,
):
    _main, work_unit = _make_work_unit(tmp_path)

    request, proposal, c278, verdict = _repair_material(
        tmp_path
    )

    forged_c278 = dict(c278)
    forged_c278["request_id"] = "rr_forged"

    snapshot = _runtime_snapshot(
        request,
        proposal,
        forged_c278,
        verdict,
    )

    result = _RA.prepare_repair_runtime_snapshot_in_work_unit(
        snapshot=snapshot,
        work_unit=work_unit,
    )

    assert result["status"] == _RA.STATUS_PREP_HOLD

    # R3E2 did not invent its own repair provenance semantics:
    # rejection comes from the existing R3D/handoff seam.
    assert result["reason"] == "REPAIR_HANDOFF_NOT_READY"

    assert (
        result["handoff_reason"]
        == "C278_REQUEST_ID_MISMATCH"
    )

    assert result["target_mutated"] is False
    assert result["kx108_invoked"] is False
