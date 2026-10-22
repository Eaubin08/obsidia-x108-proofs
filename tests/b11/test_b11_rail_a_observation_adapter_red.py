"""M42 B11 Compétence & Calibration — RED test harness for Rail A Verified Observation Adapter.

Source of truth:
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_VERIFIED_OBSERVATION_SPEC_V1.md

Runtime target (absent at RED):
  ``app.cognition.b11.rail_a_observation_adapter``
    - ``RailAVerifiedObservation``
    - ``RailABundleVerificationResult``
    - ``load_and_verify_rail_a_observation``
    - ``load_and_verify_rail_a_observations_batch``

Design & Quality Guarantees:
1. All fixtures are built in isolated ``tmp_path`` directories using the real canonical
   producers and verifiers from ``scripts/`` (never writing to ``%LOCALAPPDATA%\\Obsidia``).
2. Canonical fixture construction is strictly separated from hostile mutations.
3. Each test first asserts the discriminating properties of the canonical/mutated artifacts
   against the existing ``verify_*`` primitives BEFORE invoking the lazy adapter import,
   ensuring that fixture preconditions are genuinely validated even while the runtime module
   is absent at RED.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_batch_execution as E  # noqa: E402
import obsidia_execution_closure as CLO  # noqa: E402
import obsidia_kx108_decision_store as DS  # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PREADP  # noqa: E402
import obsidia_pre_execution_context as PEC  # noqa: E402
import obsidia_sealed_evidence_v0 as SEV  # noqa: E402
import obsidia_test_contract as TC  # noqa: E402
from app.cognition.b11.contracts import (  # noqa: E402
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.cognition.b11.evaluator import evaluate_contextual_competence  # noqa: E402


def _rt_adapter():
    """Lazy loader for the B11 Rail A verified observation adapter module."""
    import importlib

    return importlib.import_module("app.cognition.b11.rail_a_observation_adapter")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ============================================================================
# Canonical Fixture Builder (Purely using real producers from scripts/)
# ============================================================================


def _build_canonical_rail_a_bundle(
    tmp_path: Path,
    *,
    suffix: str = "a",
    target_relpath: str = "periphery/xdomain/rail_a_target_v0.py",
    pre_bytes: bytes = b"# initial state\nVALUE = 0\n",
    post_bytes: bytes = b"# remediated state\nVALUE = 108\n",
    failing_test_contract: bool = False,
    batch_execution_id: str | None = None,
    child_execution_id: str | None = None,
) -> dict[str, Any]:
    """Produces a complete 6-artifact Rail A C2/D1 bundle in isolated ``tmp_path`` stores
    using the real repository producers and verifies every single artifact with its
    canonical verifier.
    """
    base_dir = tmp_path / f"rail_a_{suffix}"
    repo_dir = base_dir / "repo"
    stores = {
        "execution_dir": base_dir / "execution",
        "pre_execution_context_dir": base_dir / "pre_execution_contexts",
        "kx108_decision_dir": base_dir / "kx108_decisions",
        "sealed_receipt_dir": base_dir / "sealed_receipts",
        "sealed_rollback_evidence_dir": base_dir / "sealed_rollback_evidence",
        "test_contract_results_dir": base_dir / "test_contract_results",
        "execution_closures_dir": base_dir / "execution_closures",
    }
    for d in stores.values():
        d.mkdir(parents=True, exist_ok=True)

    target_abs = repo_dir / target_relpath
    target_abs.parent.mkdir(parents=True, exist_ok=True)
    target_abs.write_bytes(pre_bytes)

    src_relpath = f"_PATCH_PROPOSALS/prop-{suffix}/sandbox/{target_relpath}"
    src_abs = repo_dir / src_relpath
    src_abs.parent.mkdir(parents=True, exist_ok=True)
    src_abs.write_bytes(post_bytes)

    sha_pre = _sha256_hex(pre_bytes)
    sha_post = _sha256_hex(post_bytes)
    be_id = batch_execution_id or f"be-raila-{suffix}"
    ce_id = child_execution_id or f"ce-raila-{suffix}"
    cand_id = f"cand-raila-{suffix}"

    child = {
        "child_execution_id": ce_id,
        "candidate_entry_id": cand_id,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "target_pre_hash": sha_pre[:16],
        "source_content_sha256": sha_post,
        "source_hash": sha_post[:16],
        "source_kind": "GIT_BLOB",
        "source_path": src_relpath,
        "source_git_commit_sha": "b" * 40,
        "source_git_blob_sha": "c" * 40,
        "source_git_historical_path": target_relpath,
        "operation_type": "UPDATE_TARGET_FROM_SOURCE",
        "operation_reason": f"governed remediation {suffix}",
        "execution_status": E.PLANNED,
    }

    # 1. Canonical TestContract
    expected_sha_in_check = "f" * 64 if failing_test_contract else sha_post
    chk = TC.build_check(
        check_id=f"post_sha256_{suffix}",
        check_type=TC.CHECK_TYPE_TARGET_SHA256,
        target_path=target_relpath,
        expected_target_sha256=expected_sha_in_check,
        required=True,
    )
    contract = TC.build_test_contract(
        contract_id=f"contract-{suffix}",
        candidate_entry_id=cand_id,
        batch_id=None,
        target_path=target_relpath,
        checks=[chk],
    )
    test_contract_hash = TC.compute_test_contract_hash(contract)

    # 2. Canonical PreExecutionContext V2
    manifest = {
        "repository_identity": str(repo_dir),
        "execution_worktree_path": str(repo_dir),
        "branch_name": f"exec/rail-a-{suffix}",
        "base_sha": "a" * 40,
        "source_kind": "GIT_BLOB",
        "source_repository_identity": str(repo_dir),
        "source_commit": "b" * 40,
        "source_blob_sha": "c" * 40,
        "source_path": src_relpath,
        "source_sha256": sha_post,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "operation": "REPLACE",
        "approved_scope": [target_relpath],
        "protected_scope_status": "CLEAN",
        "test_contract_hash": test_contract_hash,
        "schema_version": 2,
    }
    pec_rec: dict[str, Any] = {
        "context_schema_version": 2,
        "created_at": "2026-10-22T10:00:00+00:00",
        "repository_identity": str(repo_dir),
        "repository_root": str(repo_dir),
        "execution_worktree_path": str(repo_dir),
        "branch_name": f"exec/rail-a-{suffix}",
        "base_sha": "a" * 40,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "source_kind": "GIT_BLOB",
        "source_repository_identity": str(repo_dir),
        "source_commit": "b" * 40,
        "source_blob_sha": "c" * 40,
        "source_path": src_relpath,
        "source_sha256": sha_post,
        "operation": "REPLACE",
        "approved_scope": [target_relpath],
        "worktree_isolated": True,
        "branch_isolated": True,
        "protected_scope_status": "CLEAN",
        "manifest": manifest,
        "manifest_sha256": PEC.compute_manifest_sha256(manifest),
        "legacy_manifest_hash_short": None,
        "decision_authority": "KX108_ONLY",
    }
    pec_seed = [
        f
        for f in PEC._CONTEXT_BOUND_FIELDS_V2
        if f not in ("context_schema_version", "context_id", "created_at")
    ]
    pec_rec["context_id"] = (
        "pec-"
        + hashlib.sha256(
            json.dumps({k: pec_rec.get(k) for k in pec_seed}, sort_keys=True).encode("utf-8")
        ).hexdigest()[:32]
    )
    pec_rec["context_record_hash"] = PEC.compute_context_record_hash(pec_rec)
    pec_store_res = PEC.store_pre_execution_context_record(
        pec_rec, stores["pre_execution_context_dir"]
    )
    assert pec_store_res["status"] in (PEC.STATUS_STORED, PEC.STATUS_IDEMPOTENT_EXISTING_IDENTICAL)
    assert PEC.verify_pre_execution_context_record(pec_rec) == (True, None)

    # 3. Canonical ExecutionEnvelope & HumanApproval
    envelope = {
        "batch_execution_id": be_id,
        "batch_id": None,
        "batch_hash": None,
        "batch_hash_version": 1,
        "candidate_scope_hash": None,
        "execution_order": [cand_id],
        "dependency_edges": [],
        "children": [child],
        "decision_authority": "KX108_ONLY",
        "integrity_verified": True,
        "pre_execution_context_id": pec_rec["context_id"],
        "pre_execution_context_record_hash": pec_rec["context_record_hash"],
        "test_contract": contract,
        "test_contract_hash": test_contract_hash,
    }
    envelope["execution_authority_hash"] = E.compute_execution_authority_hash(envelope)
    env_path = stores["execution_dir"] / "executions" / be_id / "execution.json"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    approval_id = f"appr-raila-{suffix}"
    approval_rec = {
        "approval_id": approval_id,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-10-22T10:01:00+00:00",
        "batch_execution_id": be_id,
        "batch_id": None,
        "batch_hash": None,
        "candidate_scope_hash": None,
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approved_by": "HUMAN",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": "KX108_ONLY",
    }
    approval_rec["approval_record_hash"] = E.compute_approval_record_hash(approval_rec)
    appr_store = E.store_approval_artifact(approval_rec, execution_dir=stores["execution_dir"])
    assert appr_store["status"] in ("STORED", "IDEMPOTENT_ALREADY_EXISTS")

    # 4. Canonical KX108_PRE decision via real adapter + real pipeline
    pre_tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        be_id,
        ce_id,
        approval_id,
        execution_dir=stores["execution_dir"],
        pre_execution_context_dir=stores["pre_execution_context_dir"],
        repo_root=repo_dir,
    )
    assert pre_tr["status"] == PREADP.STATUS_READY, pre_tr
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        pre_tr["pre_tooling_build_state_kwargs"],
        pre_tr["pre_binding_context"],
        store_dir=stores["kx108_decision_dir"],
    )
    assert pre_out["verify_ok"] is True
    assert pre_out["x108_gate"] == "ALLOW"
    kxpre_rec = pre_out["record"]
    kxpre_id = kxpre_rec["decision_record_id"]
    kxpre_hash = kxpre_rec["decision_record_hash"]

    # 5. Canonical SealedRollbackEvidence (pre-write bytes = pre_bytes)
    sre_rec, sre_err = SEV.build_sealed_rollback_evidence(
        batch_execution_id=be_id,
        child=child,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        kx108_pre_decision_record_id=kxpre_id,
        kx108_pre_decision_record_hash=kxpre_hash,
        preimage_bytes=pre_bytes,
    )
    assert sre_err is None and sre_rec is not None
    sre_store = SEV.store_sealed_rollback_evidence(sre_rec, stores["sealed_rollback_evidence_dir"])
    assert sre_store["status"] in (SEV.STATUS_STORED, SEV.STATUS_IDEMPOTENT)
    assert SEV.verify_sealed_rollback_evidence(sre_rec) == (True, None)

    # 6. Physical apply of post_bytes & Canonical SealedApplyReceipt
    target_abs.write_bytes(post_bytes)
    sar_rec, sar_err = SEV.build_sealed_apply_receipt(
        batch_execution_id=be_id,
        child=child,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        kx108_pre_decision_record_id=kxpre_id,
        kx108_pre_decision_record_hash=kxpre_hash,
        sealed_rollback_evidence_id=sre_rec["sealed_rollback_evidence_id"],
        sealed_rollback_evidence_hash=sre_rec["sealed_rollback_evidence_hash"],
        target_pre_sha256=sha_pre,
        target_post_sha256=sha_post,
        bytes_written=len(post_bytes),
    )
    assert sar_err is None and sar_rec is not None
    sar_store = SEV.store_sealed_apply_receipt(sar_rec, stores["sealed_receipt_dir"])
    assert sar_store["status"] in (SEV.STATUS_STORED, SEV.STATUS_IDEMPOTENT)
    assert SEV.verify_sealed_apply_receipt(sar_rec) == (True, None)

    # 7. Canonical TestContractResult via real runner
    tcr_out = TC.run_and_persist_test_contract(
        contract,
        repo_dir,
        batch_execution_id=be_id,
        child_execution_id=ce_id,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        results_dir=stores["test_contract_results_dir"],
    )
    assert tcr_out["verify_ok"] is True
    tcr_rec = tcr_out["record"]

    # 8. Canonical KX108_POST linked decision via real pipeline
    tests_res = "FAIL" if failing_test_contract else "PASS"
    first_fail = f"post_sha256_{suffix}:FAIL" if failing_test_contract else ""
    post_state_kwargs = {
        "session_id": ce_id,
        "objective": child["operation_reason"],
        "base_sha": "a" * 40,
        "manifest_hash": pec_rec["manifest_sha256"],
        "diff_hash": "",
        "approved_scope": [target_relpath],
        "actual_touched_files": [target_relpath],
        "new_files": [],
        "deleted_files": [],
        "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED",
        "obsidure_status": "NOT_APPLICABLE",
        "worktree_isolated": True,
        "branch_isolated": True,
        "auto_commit_disabled": True,
        "auto_push_disabled": True,
        "auto_merge_disabled": True,
        "tests_results": tests_res,
        "gates_results": tests_res,
        "first_failure": first_fail,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
        "decision_authority": "KX108_ONLY",
    }
    translation_hash = _sha256_hex(
        json.dumps(post_state_kwargs, sort_keys=True).encode("utf-8")
    )
    post_binding_context = {
        "batch_execution_id": be_id,
        "child_execution_id": ce_id,
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approval_id": approval_id,
        "test_contract_hash": test_contract_hash,
        "test_result_id": tcr_rec["result_id"],
        "test_result_record_hash": tcr_rec["result_record_hash"],
        "kx108_input_translation_hash": translation_hash,
    }
    post_out = DS.run_and_persist_kx108_post_execution_decision(
        post_state_kwargs,
        post_binding_context,
        kxpre_id,
        execution_dir=stores["execution_dir"],
        pre_decision_store_dir=stores["kx108_decision_dir"],
        post_decision_store_dir=stores["kx108_decision_dir"],
        sealed_evidence_link={
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": sar_rec["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": sre_rec["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": sre_rec["sealed_rollback_evidence_hash"],
        },
    )
    assert post_out["status"] == "STORED" and post_out["verify_ok"] is True
    kxpost_rec = post_out["record"]

    return {
        "stores": stores,
        "repo_dir": repo_dir,
        "target_relpath": target_relpath,
        "sha_pre": sha_pre,
        "sha_post": sha_post,
        "batch_execution_id": be_id,
        "child_execution_id": ce_id,
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approval_id": approval_id,
        "test_contract_hash": test_contract_hash,
        "post_binding_context": post_binding_context,
        "post_state_kwargs": post_state_kwargs,
        "pec": pec_rec,
        "kxpre": kxpre_rec,
        "sre": sre_rec,
        "sar": sar_rec,
        "tcr": tcr_rec,
        "kxpost": kxpost_rec,
        "kxpost_id": kxpost_rec["decision_record_id"],
    }


def _adapter_store_kwargs(bundle: dict[str, Any]) -> dict[str, Path]:
    s = bundle["stores"]
    return {
        "kx108_decision_dir": s["kx108_decision_dir"],
        "pre_execution_context_dir": s["pre_execution_context_dir"],
        "sealed_receipt_dir": s["sealed_receipt_dir"],
        "sealed_rollback_evidence_dir": s["sealed_rollback_evidence_dir"],
        "test_contract_results_dir": s["test_contract_results_dir"],
    }


# ============================================================================
# RED Scenarios RA-01 to RA-11
# ============================================================================


def test_m42_red_ra_01_valid_complete_bundle_all_required_pass(tmp_path: Path):
    """RA-01: Complete valid Rail A bundle with ALL_REQUIRED_PASS produces an immutable
    RailAVerifiedObservation separating executing_mechanism_ref from mutated_target_path,
    marking pre_governance_integrity_confidence as non-predictive, and keeping B11
    evaluate_contextual_competence in UNKNOWN_COMPETENCE (conf=0.0, rel=None).
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra01", failing_test_contract=False)

    # Precondition assertions on canonical artifacts
    assert bundle["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
    assert bundle["kxpost"]["x108_gate"] == "ALLOW"
    assert bundle["kxpre"]["canonical_envelope"]["confidence"] == 0.95
    assert bundle["kxpre"]["canonical_envelope"]["confidence_scope"] == "integrity"

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is True
    assert res.rejection_code is None
    obs = res.observation
    assert obs is not None
    assert obs.domain == "tooling_build"
    assert obs.task_ref == "UPDATE_TARGET_FROM_SOURCE"
    assert obs.executing_mechanism_ref == "rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"
    assert obs.mutated_target_path == bundle["target_relpath"]
    assert obs.executing_mechanism_ref != obs.mutated_target_path
    assert obs.test_aggregate_status == "ALL_REQUIRED_PASS"
    assert obs.kx108_pre_gate == "ALLOW"
    assert obs.kx108_post_gate == "ALLOW"
    assert obs.verified_execution_outcome == "VERIFIED_TEST_CONTRACT_PASS"
    assert obs.pre_governance_integrity_confidence == 0.95
    assert obs.is_predictive_outcome_probability is False
    assert obs.provenance_store_verified is True
    assert len(obs.anchor_refs) == 6

    # Doctrinal boundary: no positive competence promotion without approved thresholds/N_min
    profile: ContextualCompetenceProfile = evaluate_contextual_competence(
        evaluation_id="eval-ra-01",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=(obs.executing_mechanism_ref,),
        conditions=obs.conditions,
        evidence_records=(obs,),
    )
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None


def test_m42_red_ra_02_valid_complete_bundle_failing_test_contract(tmp_path: Path):
    """RA-02: A failing test contract bundle produced by the real repository producers
    (tcr.aggregate_status == REQUIRED_TEST_FAILED, kxpost.x108_gate == BLOCK) is
    cryptographically valid and verified as VERIFIED_TEST_CONTRACT_FAILURE.
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra02", failing_test_contract=True)

    # Precondition assertions proving the real producers emit a valid failing bundle
    assert bundle["tcr"]["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED
    assert bundle["kxpost"]["x108_gate"] == "BLOCK"
    assert TC.verify_test_contract_result_artifact(bundle["tcr"]) == (True, None)
    assert DS.verify_kx108_decision_record(bundle["kxpost"]) == (True, None)

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is True
    assert res.rejection_code is None
    obs = res.observation
    assert obs is not None
    assert obs.test_aggregate_status == "REQUIRED_TEST_FAILED"
    assert obs.kx108_post_gate == "BLOCK"
    assert obs.verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"
    assert obs.passed_required_check_count == 0
    assert obs.required_check_count == 1


@pytest.mark.parametrize(
    "missing_artifact",
    ["pec", "kxpre", "sre", "sar", "tcr", "kxpost"],
)
def test_m42_red_ra_03_missing_artifact_fails_closed(tmp_path: Path, missing_artifact: str):
    """RA-03: Omission of any of the 6 required artifacts on disk fails closed with
    verified=False, observation=None, and an explicit ARTIFACT_MISSING rejection code.
    """
    bundle = _build_canonical_rail_a_bundle(
        tmp_path, suffix=f"ra03_{missing_artifact}", failing_test_contract=False
    )
    stores = bundle["stores"]

    artifact_paths = {
        "pec": stores["pre_execution_context_dir"] / f"{bundle['pec']['context_id']}.json",
        "kxpre": stores["kx108_decision_dir"] / f"{bundle['kxpre']['decision_record_id']}.json",
        "sre": stores["sealed_rollback_evidence_dir"]
        / f"{bundle['sre']['sealed_rollback_evidence_id']}.json",
        "sar": stores["sealed_receipt_dir"] / f"{bundle['sar']['sealed_apply_receipt_id']}.json",
        "tcr": stores["test_contract_results_dir"] / f"{bundle['tcr']['result_id']}.json",
        "kxpost": stores["kx108_decision_dir"] / f"{bundle['kxpost']['decision_record_id']}.json",
    }
    target_file = artifact_paths[missing_artifact]
    assert target_file.exists()
    target_file.unlink()
    assert not target_file.exists()

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is False
    assert res.observation is None
    assert res.rejection_code is not None
    assert res.rejection_code.startswith("ARTIFACT_MISSING:")


@pytest.mark.parametrize(
    "tampered_artifact",
    ["pec", "kxpre", "sre", "sar", "tcr", "kxpost"],
)
def test_m42_red_ra_04_tampered_artifact_without_hash_update_rejected(
    tmp_path: Path, tampered_artifact: str
):
    """RA-04: Modifying any bound field in any of the 6 persisted artifacts without
    updating its cryptographic hash chain is rejected with ARTIFACT_VERIFICATION_FAILED.
    """
    bundle = _build_canonical_rail_a_bundle(
        tmp_path, suffix=f"ra04_{tampered_artifact}", failing_test_contract=False
    )
    stores = bundle["stores"]

    if tampered_artifact == "pec":
        p = stores["pre_execution_context_dir"] / f"{bundle['pec']['context_id']}.json"
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["branch_name"] = "tampered/branch"
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert PEC.verify_pre_execution_context_record(rec)[0] is False
    elif tampered_artifact == "kxpre":
        p = stores["kx108_decision_dir"] / f"{bundle['kxpre']['decision_record_id']}.json"
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["reason_code"] = "TAMPERED_REASON"
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert DS.verify_kx108_decision_record(rec)[0] is False
    elif tampered_artifact == "sre":
        p = (
            stores["sealed_rollback_evidence_dir"]
            / f"{bundle['sre']['sealed_rollback_evidence_id']}.json"
        )
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["pre_write_size"] = 999999
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert SEV.verify_sealed_rollback_evidence(rec)[0] is False
    elif tampered_artifact == "sar":
        p = stores["sealed_receipt_dir"] / f"{bundle['sar']['sealed_apply_receipt_id']}.json"
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["bytes_written"] = 999999
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert SEV.verify_sealed_apply_receipt(rec)[0] is False
    elif tampered_artifact == "tcr":
        p = stores["test_contract_results_dir"] / f"{bundle['tcr']['result_id']}.json"
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["aggregate_status"] = "REQUIRED_TEST_FAILED"
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert TC.verify_test_contract_result_artifact(rec)[0] is False
    elif tampered_artifact == "kxpost":
        p = stores["kx108_decision_dir"] / f"{bundle['kxpost']['decision_record_id']}.json"
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["reason_code"] = "TAMPERED_POST_REASON"
        p.write_text(json.dumps(rec), encoding="utf-8")
        assert DS.verify_kx108_decision_record(rec)[0] is False

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is False
    assert res.observation is None
    assert res.rejection_code is not None
    assert res.rejection_code.startswith("ARTIFACT_VERIFICATION_FAILED:")
    assert any(r.startswith("ARTIFACT_VERIFICATION_FAILED:") for r in res.risk_indicators)


def test_m42_red_ra_05_cross_bundle_substitution_rejected_even_when_individually_valid(
    tmp_path: Path,
):
    """RA-05: Two complete bundles A (failing test) and B (passing test) are individually valid.
    If kxpost_A is re-hashed to reference tcr_B (which passes verify_test_contract_result_artifact
    on its own), the adapter detects the cross-link mismatch (execution_authority_hash /
    child_execution_id / test_contract_hash) and rejects with CROSS_LINK_MISMATCH.
    """
    bundle_a = _build_canonical_rail_a_bundle(
        tmp_path,
        suffix="ra05_a",
        target_relpath="periphery/xdomain/target_a.py",
        failing_test_contract=True,
    )
    bundle_b = _build_canonical_rail_a_bundle(
        tmp_path,
        suffix="ra05_b",
        target_relpath="periphery/xdomain/target_b.py",
        failing_test_contract=False,
    )

    # Copy tcr_B into bundle_a's test_contract_results_dir
    tcr_b = bundle_b["tcr"]
    tcr_b_in_a = (
        bundle_a["stores"]["test_contract_results_dir"] / f"{tcr_b['result_id']}.json"
    )
    tcr_b_in_a.write_text(json.dumps(tcr_b, indent=2), encoding="utf-8")

    # Mutate kxpost_A to point to tcr_B and recompute kxpost_A's hash so verify_kx108_decision_record passes!
    kxpost_a_path = (
        bundle_a["stores"]["kx108_decision_dir"] / f"{bundle_a['kxpost_id']}.json"
    )
    kxpost_a_mut = json.loads(kxpost_a_path.read_text(encoding="utf-8"))
    kxpost_a_mut["test_result_id"] = tcr_b["result_id"]
    kxpost_a_mut["test_result_record_hash"] = tcr_b["result_record_hash"]
    kxpost_a_mut["decision_record_hash"] = DS.compute_kx108_decision_record_hash(kxpost_a_mut)
    kxpost_a_path.write_text(json.dumps(kxpost_a_mut, indent=2), encoding="utf-8")

    # Discriminating precondition: both individual verifiers PASS!
    assert DS.verify_kx108_decision_record(kxpost_a_mut) == (True, None)
    assert TC.verify_test_contract_result_artifact(tcr_b) == (True, None)

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle_a["kxpost_id"],
        **_adapter_store_kwargs(bundle_a),
    )

    assert res.verified is False
    assert res.observation is None
    assert res.rejection_code is not None
    assert res.rejection_code.startswith("CROSS_LINK_MISMATCH:")
    assert any(r.startswith("CROSS_LINK_MISMATCH:") for r in res.risk_indicators)


def test_m42_red_ra_06_internal_test_result_inconsistency_rejected_despite_valid_hash(
    tmp_path: Path,
):
    """RA-06: If TestContractResult has aggregate_status='ALL_REQUIRED_PASS' while a
    required check inside checks[] has result='FAIL', and both tcr.result_record_hash
    and kxpost.decision_record_hash are recomputed so individual verifiers pass,
    the adapter must still reject with TEST_RESULT_INTERNAL_INCONSISTENCY.
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra06", failing_test_contract=False)
    stores = bundle["stores"]

    # Mutate tcr: set check result to FAIL while keeping aggregate_status = ALL_REQUIRED_PASS, then re-hash
    tcr_path = stores["test_contract_results_dir"] / f"{bundle['tcr']['result_id']}.json"
    tcr_mut = json.loads(tcr_path.read_text(encoding="utf-8"))
    tcr_mut["checks"][0]["result"] = "FAIL"
    tcr_mut["aggregate_status"] = "ALL_REQUIRED_PASS"
    tcr_mut["result_record_hash"] = TC.compute_test_contract_result_hash(tcr_mut)
    tcr_path.write_text(json.dumps(tcr_mut, indent=2), encoding="utf-8")

    # Update kxpost to bind the new tcr hash and re-hash kxpost
    kxpost_path = stores["kx108_decision_dir"] / f"{bundle['kxpost_id']}.json"
    kxpost_mut = json.loads(kxpost_path.read_text(encoding="utf-8"))
    kxpost_mut["test_result_record_hash"] = tcr_mut["result_record_hash"]
    kxpost_mut["decision_record_hash"] = DS.compute_kx108_decision_record_hash(kxpost_mut)
    kxpost_path.write_text(json.dumps(kxpost_mut, indent=2), encoding="utf-8")

    # Discriminating precondition: verify_test_contract_result_artifact does NOT check internal consistency!
    assert TC.verify_test_contract_result_artifact(tcr_mut) == (True, None)
    assert DS.verify_kx108_decision_record(kxpost_mut) == (True, None)

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is False
    assert res.observation is None
    assert res.rejection_code == "TEST_RESULT_INTERNAL_INCONSISTENCY"
    assert "TEST_RESULT_INTERNAL_INCONSISTENCY" in res.risk_indicators


def test_m42_red_ra_07_rejects_legacy_kxd_and_agent_kxagent_records(tmp_path: Path):
    """RA-07: Legacy 1-phase POST records (kxd-*) and Rail B agent pre-execution records
    (kxagent-*) pass verify_kx108_decision_record but must be rejected by the Rail A C2/D1
    observation adapter with UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD.
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra07", failing_test_contract=False)
    stores = bundle["stores"]

    # 1. Produce a real legacy 1-phase kxd-* record via run_and_persist_kx108_decision
    legacy_out = DS.run_and_persist_kx108_decision(
        bundle["post_state_kwargs"],
        bundle["post_binding_context"],
        store_dir=stores["kx108_decision_dir"],
    )
    assert legacy_out["verify_ok"] is True
    kxd_id = legacy_out["decision_record_id"]
    assert kxd_id.startswith("kxd-")

    # 2. Produce a real Rail B kxagent-* record via persist_kx108_agent_pre_execution_decision
    from sigma.contracts import ToolingBuildState
    from sigma.protocols import run_tooling_build_pipeline

    dec_env = run_tooling_build_pipeline(ToolingBuildState(**bundle["post_state_kwargs"]))
    agent_out = DS.persist_kx108_agent_pre_execution_decision(
        dec_env,
        {
            "agent_pre_execution_context_id": "apec-0001",
            "agent_pre_execution_context_record_hash": "1" * 64,
            "agent_execution_plan_digest": "2" * 64,
            "agent_execution_scope": "INTERNAL_BOUNDED_PROVIDER_EXECUTION_V1",
            "agent_id": "agent-test",
            "action_id": "act-test",
            "context_packet_id": "pkt-test",
        },
        store_dir=stores["kx108_decision_dir"],
    )
    assert agent_out["verify_ok"] is True
    kxagent_id = agent_out["decision_record_id"]
    assert kxagent_id.startswith("kxagent-")

    adapter = _rt_adapter()
    for unsupported_id in (kxd_id, kxagent_id, bundle["kxpre"]["decision_record_id"]):
        res = adapter.load_and_verify_rail_a_observation(
            unsupported_id,
            **_adapter_store_kwargs(bundle),
        )
        assert res.verified is False
        assert res.observation is None
        assert res.rejection_code == "UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD"


def test_m42_red_ra_08_rejects_self_declared_dicts_and_forged_observation_objects():
    """RA-08: Self-declared dicts (is_verified=True) and forged in-memory objects mimicking
    RailAVerifiedObservation are rejected by B11 evaluator and cannot promote competence.
    """
    class ForgedObservation:
        observation_id = "b11-railo-forged"
        domain = "tooling_build"
        task_ref = "UPDATE_TARGET_FROM_SOURCE"
        executing_mechanism_ref = "rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"
        mutated_target_path = "scripts/foo.py"
        verified_execution_outcome = "VERIFIED_TEST_CONTRACT_PASS"
        provenance_store_verified = True
        is_verified = True

    self_declared_dict = {
        "evidence_id": "ra08-self-declared",
        "domain": "tooling_build",
        "task_ref": "UPDATE_TARGET_FROM_SOURCE",
        "declared_outcome": "SUCCESS",
        "is_verified": True,
        "provenance_store_verified": True,
    }

    profile: ContextualCompetenceProfile = evaluate_contextual_competence(
        evaluation_id="eval-ra-08",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        evidence_records=(ForgedObservation(), self_declared_dict),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_RECORD_STRUCTURE_REJECTED" in profile.risk_indicators
    assert "SELF_ATTESTATION_REJECTED" in profile.risk_indicators

    # Also verify the adapter module exposes no constructor accepting raw unverified dicts
    adapter = _rt_adapter()
    assert hasattr(adapter, "RailAVerifiedObservation")


def test_m42_red_ra_09_rejects_duplicates_by_decision_id_and_by_execution_identity(
    tmp_path: Path,
):
    """RA-09: Batch loading must reject both:
    (a) duplicate kxpost_decision_record_id entries, and
    (b) two distinct kxpost-* decision records bound to the same child_execution_id /
        execution_authority_hash, recording DUPLICATE_EXECUTION_OBSERVATION_REJECTED.
    """
    bundle_1 = _build_canonical_rail_a_bundle(
        tmp_path,
        suffix="ra09_1",
        batch_execution_id="be-shared-09",
        child_execution_id="ce-shared-09",
    )

    # Create a second distinct kxpost-* in the SAME store for the SAME child_execution_id
    # (e.g., a second evaluation run with a different translation hash)
    alt_binding = dict(bundle_1["post_binding_context"])
    alt_binding["kx108_input_translation_hash"] = "9" * 64
    post_out_2 = DS.run_and_persist_kx108_post_execution_decision(
        bundle_1["post_state_kwargs"],
        alt_binding,
        bundle_1["kxpre"]["decision_record_id"],
        execution_dir=bundle_1["stores"]["execution_dir"],
        pre_decision_store_dir=bundle_1["stores"]["kx108_decision_dir"],
        post_decision_store_dir=bundle_1["stores"]["kx108_decision_dir"],
        sealed_evidence_link={
            "sealed_apply_receipt_id": bundle_1["sar"]["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": bundle_1["sar"]["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": bundle_1["sre"]["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": bundle_1["sre"]["sealed_rollback_evidence_hash"],
        },
    )
    assert post_out_2["status"] == "STORED" and post_out_2["verify_ok"] is True
    kxpost_id_2 = post_out_2["decision_record_id"]
    assert kxpost_id_2 != bundle_1["kxpost_id"]

    adapter = _rt_adapter()
    observations, unknowns, risk_indicators = adapter.load_and_verify_rail_a_observations_batch(
        [bundle_1["kxpost_id"], bundle_1["kxpost_id"], kxpost_id_2],
        **_adapter_store_kwargs(bundle_1),
    )

    # Only the first observation for child_execution_id='ce-shared-09' may be retained
    assert len(observations) == 1
    assert observations[0].child_execution_id == "ce-shared-09"
    assert "DUPLICATE_EXECUTION_OBSERVATION_REJECTED" in risk_indicators


def test_m42_red_ra_10_closure_hardcoded_functional_pass_never_overrides_test_failure(
    tmp_path: Path,
):
    """RA-10: create_execution_closure_record hardcodes functional_status='PASS' even when
    TestContractResult failed (REQUIRED_TEST_FAILED) and KX108 gate is BLOCK.
    The adapter must rely exclusively on TestContractResult for test outcome and never
    treat clo.functional_status='PASS' as a passing test execution.
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra10", failing_test_contract=True)
    stores = bundle["stores"]

    # Create a real ExecutionClosureRecord via the canonical producer
    clo_out = CLO.create_execution_closure_record(
        kx108_decision_record=bundle["kxpost"],
        binding_context=bundle["post_binding_context"],
        target_path=bundle["target_relpath"],
        target_pre_apply_sha256=bundle["sha_pre"],
        target_post_apply_sha256=bundle["sha_post"],
        final_disposition="ROLLBACK_PENDING_HUMAN_AUTHORIZATION",
        rollback_status="NOT_EXECUTED",
        store_dir=stores["execution_closures_dir"],
    )
    assert clo_out["verify_ok"] is True
    clo_rec = clo_out["record"]

    # Discriminating forensic fact: clo.functional_status is hardcoded to "PASS" while tcr failed!
    assert clo_rec["functional_status"] == "PASS"
    assert bundle["tcr"]["aggregate_status"] == "REQUIRED_TEST_FAILED"

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        closure_id=clo_rec["closure_id"],
        execution_closures_dir=stores["execution_closures_dir"],
        **_adapter_store_kwargs(bundle),
    )

    assert res.verified is True
    obs = res.observation
    assert obs is not None
    assert obs.test_aggregate_status == "REQUIRED_TEST_FAILED"
    assert obs.verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"
    assert obs.verified_execution_outcome != "VERIFIED_TEST_CONTRACT_PASS"


def test_m42_red_ra_11_b11_effects_immutability_and_strict_read_only_stores(
    tmp_path: Path,
):
    """RA-11: The adapter and B11 preserve B11_EFFECTS invariants, return strictly immutable
    objects, and perform zero writes/mutations in the store directories.
    """
    bundle = _build_canonical_rail_a_bundle(tmp_path, suffix="ra11", failing_test_contract=False)
    stores = bundle["stores"]

    # Snapshot all files and their SHA-256 in all store directories before adapter call
    before_snapshot = {
        str(p.relative_to(tmp_path)): _sha256_hex(p.read_bytes())
        for d in stores.values()
        for p in d.rglob("*")
        if p.is_file()
    }

    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["advisory_only"] is True
    assert B11_EFFECTS["b12_selection"] is False

    adapter = _rt_adapter()
    res = adapter.load_and_verify_rail_a_observation(
        bundle["kxpost_id"],
        **_adapter_store_kwargs(bundle),
    )

    after_snapshot = {
        str(p.relative_to(tmp_path)): _sha256_hex(p.read_bytes())
        for d in stores.values()
        for p in d.rglob("*")
        if p.is_file()
    }
    assert after_snapshot == before_snapshot

    assert res.verified is True
    obs = res.observation
    assert obs is not None
    with pytest.raises(AttributeError):
        obs.verified_execution_outcome = "VERIFIED_TEST_CONTRACT_FAILURE"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        res.verified = False  # type: ignore[misc]


def test_m42_red_ra_12_f01_deduplication_distinguishes_execution_identity_from_shared_authority_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """RA-12 (F-01): Batch deduplication must separate batch authority identity
    (execution_authority_hash) from unitary child execution identity
    ((batch_execution_id, child_execution_id),kxpost_decision_record_id, sar receipt).
    - Repeating the same execution under a different kxpost-* ID is rejected.
    - Two distinct child executions (ce-child-01 vs ce-child-02) sharing a common
      parent execution_authority_hash are NOT rejected on account of the shared
      authority hash.
    """
    bundle_1 = _build_canonical_rail_a_bundle(
        tmp_path,
        suffix="ra12_c1",
        target_relpath="periphery/xdomain/target_c1.py",
        batch_execution_id="be-shared-ra12",
        child_execution_id="ce-child-01",
    )
    bundle_2 = _build_canonical_rail_a_bundle(
        tmp_path,
        suffix="ra12_c2",
        target_relpath="periphery/xdomain/target_c2.py",
        batch_execution_id="be-shared-ra12",
        child_execution_id="ce-child-02",
    )

    # Second distinct kxpost-* record for the SAME execution ("be-shared-ra12", "ce-child-01")
    alt_binding_1 = dict(bundle_1["post_binding_context"])
    alt_binding_1["kx108_input_translation_hash"] = "8" * 64
    post_out_1_dup = DS.run_and_persist_kx108_post_execution_decision(
        bundle_1["post_state_kwargs"],
        alt_binding_1,
        bundle_1["kxpre"]["decision_record_id"],
        execution_dir=bundle_1["stores"]["execution_dir"],
        pre_decision_store_dir=bundle_1["stores"]["kx108_decision_dir"],
        post_decision_store_dir=bundle_1["stores"]["kx108_decision_dir"],
        sealed_evidence_link={
            "sealed_apply_receipt_id": bundle_1["sar"]["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": bundle_1["sar"]["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": bundle_1["sre"]["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": bundle_1["sre"]["sealed_rollback_evidence_hash"],
        },
    )
    assert post_out_1_dup["status"] == "STORED" and post_out_1_dup["verify_ok"] is True
    kxpost_id_1_dup = post_out_1_dup["decision_record_id"]
    assert kxpost_id_1_dup != bundle_1["kxpost_id"]

    adapter = _rt_adapter()
    res_1 = adapter.load_and_verify_rail_a_observation(
        bundle_1["kxpost_id"], **_adapter_store_kwargs(bundle_1)
    )
    res_1_dup = adapter.load_and_verify_rail_a_observation(
        kxpost_id_1_dup, **_adapter_store_kwargs(bundle_1)
    )
    res_2 = adapter.load_and_verify_rail_a_observation(
        bundle_2["kxpost_id"], **_adapter_store_kwargs(bundle_2)
    )
    assert res_1.verified is True and res_1.observation is not None
    assert res_1_dup.verified is True and res_1_dup.observation is not None
    assert res_2.verified is True and res_2.observation is not None

    # Test deduplication boundary: obs_2 has a distinct (batch_execution_id, child_execution_id)
    # and distinct sar/kxpost anchors, but shares the parent batch's execution_authority_hash.
    object.__setattr__(
        res_2.observation,
        "_execution_authority_hash",
        res_1.observation.execution_authority_hash,
    )
    assert res_2.observation.execution_authority_hash == res_1.observation.execution_authority_hash
    assert res_2.observation.child_execution_id != res_1.observation.child_execution_id

    by_id = {
        bundle_1["kxpost_id"]: res_1,
        kxpost_id_1_dup: res_1_dup,
        bundle_2["kxpost_id"]: res_2,
    }
    monkeypatch.setattr(
        adapter,
        "load_and_verify_rail_a_observation",
        lambda rec_id, **kwargs: by_id[rec_id],
    )

    observations, unknowns, risk_indicators = adapter.load_and_verify_rail_a_observations_batch(
        [bundle_1["kxpost_id"], kxpost_id_1_dup, bundle_2["kxpost_id"]],
        **_adapter_store_kwargs(bundle_1),
    )

    #kxpost_id_1_dup (same child_execution_id='ce-child-01') must be rejected as duplicate,
    # while bundle_2 (distinct child_execution_id='ce-child-02' under shared authority hash) must be kept!
    assert "DUPLICATE_EXECUTION_OBSERVATION_REJECTED" in risk_indicators
    assert len(observations) == 2
    assert [o.child_execution_id for o in observations] == ["ce-child-01", "ce-child-02"]


def _build_diff_scope_rail_a_bundle(
    tmp_path: Path,
    *,
    suffix: str,
    expected_diff_paths: list[str],
    failing_test_contract: bool,
) -> dict[str, Any]:
    """Builds a canonical 6-artifact Rail A bundle in an initialized temporary Git repo
    using a real CHECK_TYPE_DIFF_SCOPE check executed by TC.run_and_persist_test_contract.
    """
    import subprocess

    base_dir = tmp_path / f"rail_a_diff_{suffix}"
    repo_dir = base_dir / "repo"
    stores = {
        "execution_dir": base_dir / "execution",
        "pre_execution_context_dir": base_dir / "pre_execution_contexts",
        "kx108_decision_dir": base_dir / "kx108_decisions",
        "sealed_receipt_dir": base_dir / "sealed_receipts",
        "sealed_rollback_evidence_dir": base_dir / "sealed_rollback_evidence",
        "test_contract_results_dir": base_dir / "test_contract_results",
        "execution_closures_dir": base_dir / "execution_closures",
    }
    for d in stores.values():
        d.mkdir(parents=True, exist_ok=True)

    target_relpath = "periphery/xdomain/rail_a_diff_target.py"
    pre_bytes = b"# initial state\nVALUE = 0\n"
    post_bytes = b"# remediated state\nVALUE = 108\n"

    target_abs = repo_dir / target_relpath
    target_abs.parent.mkdir(parents=True, exist_ok=True)
    target_abs.write_bytes(pre_bytes)

    # Initialize real local git repo and commit pre_bytes so `git diff --name-only` is canonical
    subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@obsidia.local"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Obsidia Test"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "add", target_relpath], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo_dir), check=True, capture_output=True)

    src_relpath = f"_PATCH_PROPOSALS/prop-{suffix}/sandbox/{target_relpath}"
    src_abs = repo_dir / src_relpath
    src_abs.parent.mkdir(parents=True, exist_ok=True)
    src_abs.write_bytes(post_bytes)

    sha_pre = _sha256_hex(pre_bytes)
    sha_post = _sha256_hex(post_bytes)
    be_id = f"be-diff-{suffix}"
    ce_id = f"ce-diff-{suffix}"
    cand_id = f"cand-diff-{suffix}"

    child = {
        "child_execution_id": ce_id,
        "candidate_entry_id": cand_id,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "target_pre_hash": sha_pre[:16],
        "source_content_sha256": sha_post,
        "source_hash": sha_post[:16],
        "source_kind": "GIT_BLOB",
        "source_path": src_relpath,
        "source_git_commit_sha": "b" * 40,
        "source_git_blob_sha": "c" * 40,
        "source_git_historical_path": target_relpath,
        "operation_type": "UPDATE_TARGET_FROM_SOURCE",
        "operation_reason": f"governed diff remediation {suffix}",
        "execution_status": E.PLANNED,
    }

    chk = TC.build_check(
        check_id=f"diff_scope_{suffix}",
        check_type=TC.CHECK_TYPE_DIFF_SCOPE,
        expected_diff_paths=expected_diff_paths,
        required=True,
    )
    contract = TC.build_test_contract(
        contract_id=f"contract-diff-{suffix}",
        candidate_entry_id=cand_id,
        batch_id=None,
        target_path=target_relpath,
        checks=[chk],
    )
    test_contract_hash = TC.compute_test_contract_hash(contract)

    manifest = {
        "repository_identity": str(repo_dir),
        "execution_worktree_path": str(repo_dir),
        "branch_name": f"exec/rail-a-diff-{suffix}",
        "base_sha": "a" * 40,
        "source_kind": "GIT_BLOB",
        "source_repository_identity": str(repo_dir),
        "source_commit": "b" * 40,
        "source_blob_sha": "c" * 40,
        "source_path": src_relpath,
        "source_sha256": sha_post,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "operation": "REPLACE",
        "approved_scope": [target_relpath],
        "protected_scope_status": "CLEAN",
        "test_contract_hash": test_contract_hash,
        "schema_version": 2,
    }
    pec_rec: dict[str, Any] = {
        "context_schema_version": 2,
        "created_at": "2026-10-22T10:00:00+00:00",
        "repository_identity": str(repo_dir),
        "repository_root": str(repo_dir),
        "execution_worktree_path": str(repo_dir),
        "branch_name": f"exec/rail-a-diff-{suffix}",
        "base_sha": "a" * 40,
        "target_path": target_relpath,
        "target_pre_sha256": sha_pre,
        "source_kind": "GIT_BLOB",
        "source_repository_identity": str(repo_dir),
        "source_commit": "b" * 40,
        "source_blob_sha": "c" * 40,
        "source_path": src_relpath,
        "source_sha256": sha_post,
        "operation": "REPLACE",
        "approved_scope": [target_relpath],
        "worktree_isolated": True,
        "branch_isolated": True,
        "protected_scope_status": "CLEAN",
        "manifest": manifest,
        "manifest_sha256": PEC.compute_manifest_sha256(manifest),
        "legacy_manifest_hash_short": None,
        "decision_authority": "KX108_ONLY",
    }
    pec_seed = [
        f
        for f in PEC._CONTEXT_BOUND_FIELDS_V2
        if f not in ("context_schema_version", "context_id", "created_at")
    ]
    pec_rec["context_id"] = (
        "pec-"
        + hashlib.sha256(
            json.dumps({k: pec_rec.get(k) for k in pec_seed}, sort_keys=True).encode("utf-8")
        ).hexdigest()[:32]
    )
    pec_rec["context_record_hash"] = PEC.compute_context_record_hash(pec_rec)
    PEC.store_pre_execution_context_record(pec_rec, stores["pre_execution_context_dir"])

    envelope = {
        "batch_execution_id": be_id,
        "batch_id": None,
        "batch_hash": None,
        "batch_hash_version": 1,
        "candidate_scope_hash": None,
        "execution_order": [cand_id],
        "dependency_edges": [],
        "children": [child],
        "decision_authority": "KX108_ONLY",
        "integrity_verified": True,
        "pre_execution_context_id": pec_rec["context_id"],
        "pre_execution_context_record_hash": pec_rec["context_record_hash"],
        "test_contract": contract,
        "test_contract_hash": test_contract_hash,
    }
    envelope["execution_authority_hash"] = E.compute_execution_authority_hash(envelope)
    env_path = stores["execution_dir"] / "executions" / be_id / "execution.json"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    approval_id = f"appr-diff-{suffix}"
    approval_rec = {
        "approval_id": approval_id,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-10-22T10:01:00+00:00",
        "batch_execution_id": be_id,
        "batch_id": None,
        "batch_hash": None,
        "candidate_scope_hash": None,
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approved_by": "HUMAN",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": "KX108_ONLY",
    }
    approval_rec["approval_record_hash"] = E.compute_approval_record_hash(approval_rec)
    E.store_approval_artifact(approval_rec, execution_dir=stores["execution_dir"])

    pre_tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        be_id,
        ce_id,
        approval_id,
        execution_dir=stores["execution_dir"],
        pre_execution_context_dir=stores["pre_execution_context_dir"],
        repo_root=repo_dir,
    )
    assert pre_tr["status"] == PREADP.STATUS_READY
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        pre_tr["pre_tooling_build_state_kwargs"],
        pre_tr["pre_binding_context"],
        store_dir=stores["kx108_decision_dir"],
    )
    kxpre_rec = pre_out["record"]

    sre_rec, _ = SEV.build_sealed_rollback_evidence(
        batch_execution_id=be_id,
        child=child,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        kx108_pre_decision_record_id=kxpre_rec["decision_record_id"],
        kx108_pre_decision_record_hash=kxpre_rec["decision_record_hash"],
        preimage_bytes=pre_bytes,
    )
    assert sre_rec is not None
    SEV.store_sealed_rollback_evidence(sre_rec, stores["sealed_rollback_evidence_dir"])

    target_abs.write_bytes(post_bytes)
    sar_rec, _ = SEV.build_sealed_apply_receipt(
        batch_execution_id=be_id,
        child=child,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        kx108_pre_decision_record_id=kxpre_rec["decision_record_id"],
        kx108_pre_decision_record_hash=kxpre_rec["decision_record_hash"],
        sealed_rollback_evidence_id=sre_rec["sealed_rollback_evidence_id"],
        sealed_rollback_evidence_hash=sre_rec["sealed_rollback_evidence_hash"],
        target_pre_sha256=sha_pre,
        target_post_sha256=sha_post,
        bytes_written=len(post_bytes),
    )
    assert sar_rec is not None
    SEV.store_sealed_apply_receipt(sar_rec, stores["sealed_receipt_dir"])

    tcr_out = TC.run_and_persist_test_contract(
        contract,
        repo_dir,
        batch_execution_id=be_id,
        child_execution_id=ce_id,
        execution_authority_hash=envelope["execution_authority_hash"],
        approval_id=approval_id,
        results_dir=stores["test_contract_results_dir"],
    )
    assert tcr_out["verify_ok"] is True
    tcr_rec = tcr_out["record"]

    tests_res = "FAIL" if failing_test_contract else "PASS"
    first_fail = f"diff_scope_{suffix}:FAIL" if failing_test_contract else ""
    post_state_kwargs = {
        "session_id": ce_id,
        "objective": child["operation_reason"],
        "base_sha": "a" * 40,
        "manifest_hash": pec_rec["manifest_sha256"],
        "diff_hash": "",
        "approved_scope": [target_relpath],
        "actual_touched_files": [target_relpath],
        "new_files": [],
        "deleted_files": [],
        "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED",
        "obsidure_status": "NOT_APPLICABLE",
        "worktree_isolated": True,
        "branch_isolated": True,
        "auto_commit_disabled": True,
        "auto_push_disabled": True,
        "auto_merge_disabled": True,
        "tests_results": tests_res,
        "gates_results": tests_res,
        "first_failure": first_fail,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
        "decision_authority": "KX108_ONLY",
    }
    translation_hash = _sha256_hex(json.dumps(post_state_kwargs, sort_keys=True).encode("utf-8"))
    post_binding_context = {
        "batch_execution_id": be_id,
        "child_execution_id": ce_id,
        "execution_authority_hash": envelope["execution_authority_hash"],
        "approval_id": approval_id,
        "test_contract_hash": test_contract_hash,
        "test_result_id": tcr_rec["result_id"],
        "test_result_record_hash": tcr_rec["result_record_hash"],
        "kx108_input_translation_hash": translation_hash,
    }
    post_out = DS.run_and_persist_kx108_post_execution_decision(
        post_state_kwargs,
        post_binding_context,
        kxpre_rec["decision_record_id"],
        execution_dir=stores["execution_dir"],
        pre_decision_store_dir=stores["kx108_decision_dir"],
        post_decision_store_dir=stores["kx108_decision_dir"],
        sealed_evidence_link={
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": sar_rec["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": sre_rec["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": sre_rec["sealed_rollback_evidence_hash"],
        },
    )
    assert post_out["status"] == "STORED" and post_out["verify_ok"] is True
    kxpost_rec = post_out["record"]

    return {
        "stores": stores,
        "target_relpath": target_relpath,
        "tcr": tcr_rec,
        "kxpost": kxpost_rec,
        "kxpost_id": kxpost_rec["decision_record_id"],
    }


def test_m42_red_ra_13_f03_diff_scope_exact_coherence_and_contradiction_rejection(
    tmp_path: Path,
):
    """RA-13 (F-03): For DIFF_SCOPE_EXACT checks in TestContractResult:
    1. Authentic passing check (actual_diff_paths == expected_diff_paths, result='PASS')
       is accepted as VERIFIED_TEST_CONTRACT_PASS.
    2. Authentic failing check (actual_diff_paths != expected_diff_paths, result='FAIL')
       is accepted as VERIFIED_TEST_CONTRACT_FAILURE (not confused with tampering).
    3. Hostile re-hashed TCR where a DIFF_SCOPE_EXACT check has contradictory
       actual_diff_paths != expected_diff_paths while claiming result='PASS' (or
       actual_diff_paths == expected_diff_paths while claiming result='FAIL') is
       rejected with TEST_RESULT_INTERNAL_INCONSISTENCY even though individual hash
       verifiers pass.
    """
    target_rel = "periphery/xdomain/rail_a_diff_target.py"

    # 1. Authentic PASS bundle with DIFF_SCOPE_EXACT
    bundle_pass = _build_diff_scope_rail_a_bundle(
        tmp_path,
        suffix="pass",
        expected_diff_paths=[target_rel],
        failing_test_contract=False,
    )
    assert bundle_pass["tcr"]["checks"][0]["result"] == "PASS"
    assert bundle_pass["tcr"]["checks"][0]["actual_diff_paths"] == [target_rel]
    assert bundle_pass["tcr"]["checks"][0]["expected_diff_paths"] == [target_rel]

    # 2. Authentic FAIL bundle with DIFF_SCOPE_EXACT
    bundle_fail = _build_diff_scope_rail_a_bundle(
        tmp_path,
        suffix="fail",
        expected_diff_paths=["periphery/xdomain/other_file.py"],
        failing_test_contract=True,
    )
    assert bundle_fail["tcr"]["checks"][0]["result"] == "FAIL"
    assert bundle_fail["tcr"]["checks"][0]["actual_diff_paths"] == [target_rel]
    assert bundle_fail["tcr"]["checks"][0]["expected_diff_paths"] == [
        "periphery/xdomain/other_file.py"
    ]

    # 3. Hostile bundle: re-hash PASS bundle's TCR after injecting contradictory actual_diff_paths
    bundle_hostile = _build_diff_scope_rail_a_bundle(
        tmp_path,
        suffix="hostile",
        expected_diff_paths=[target_rel],
        failing_test_contract=False,
    )
    tcr_path = (
        bundle_hostile["stores"]["test_contract_results_dir"]
        / f"{bundle_hostile['tcr']['result_id']}.json"
    )
    tcr_mut = json.loads(tcr_path.read_text(encoding="utf-8"))
    tcr_mut["checks"][0]["actual_diff_paths"] = [
        target_rel,
        "periphery/xdomain/undeclared_extra_diff.py",
    ]
    tcr_mut["checks"][0]["result"] = "PASS"
    tcr_mut["aggregate_status"] = "ALL_REQUIRED_PASS"
    tcr_mut["result_record_hash"] = TC.compute_test_contract_result_hash(tcr_mut)
    tcr_path.write_text(json.dumps(tcr_mut, indent=2), encoding="utf-8")

    kxpost_path = (
        bundle_hostile["stores"]["kx108_decision_dir"] / f"{bundle_hostile['kxpost_id']}.json"
    )
    kxpost_mut = json.loads(kxpost_path.read_text(encoding="utf-8"))
    kxpost_mut["test_result_record_hash"] = tcr_mut["result_record_hash"]
    kxpost_mut["decision_record_hash"] = DS.compute_kx108_decision_record_hash(kxpost_mut)
    kxpost_path.write_text(json.dumps(kxpost_mut, indent=2), encoding="utf-8")

    # Individual canonical verifiers pass on the re-hashed artifacts
    assert TC.verify_test_contract_result_artifact(tcr_mut) == (True, None)
    assert DS.verify_kx108_decision_record(kxpost_mut) == (True, None)

    adapter = _rt_adapter()

    res_pass = adapter.load_and_verify_rail_a_observation(
        bundle_pass["kxpost_id"], **_adapter_store_kwargs(bundle_pass)
    )
    assert res_pass.verified is True
    assert res_pass.observation is not None
    assert res_pass.observation.verified_execution_outcome == "VERIFIED_TEST_CONTRACT_PASS"

    res_fail = adapter.load_and_verify_rail_a_observation(
        bundle_fail["kxpost_id"], **_adapter_store_kwargs(bundle_fail)
    )
    assert res_fail.verified is True
    assert res_fail.observation is not None
    assert res_fail.observation.verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"

    res_hostile = adapter.load_and_verify_rail_a_observation(
        bundle_hostile["kxpost_id"], **_adapter_store_kwargs(bundle_hostile)
    )
    assert res_hostile.verified is False
    assert res_hostile.observation is None
    assert res_hostile.rejection_code == "TEST_RESULT_INTERNAL_INCONSISTENCY"
    assert "TEST_RESULT_INTERNAL_INCONSISTENCY" in res_hostile.risk_indicators
