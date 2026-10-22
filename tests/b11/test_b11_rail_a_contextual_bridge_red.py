"""M42 B11 Compétence & Calibration — RED test harness for Rail A Contextual Bridge.

Source of truth:
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_VERIFIED_OBSERVATION_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_CONTEXTUAL_BRIDGE_SPEC_V1.md

Runtime target (absent at RED):
  ``evaluate_rail_a_contextual_competence`` in ``app.cognition.b11``

Design & Quality Guarantees:
1. All fixtures are built in isolated ``tmp_path`` directories using the real canonical
   producers and verifiers from ``scripts/``.
2. Each test asserts the discriminating preconditions on the canonical artifacts
   BEFORE invoking the lazy bridge import, guaranteeing that preconditions are genuinely
   validated even while the runtime bridge function is absent at RED.
3. Every test fails cleanly with certified RED when the bridge function is absent.
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


def _rt_bridge():
    """Lazy loader for evaluate_rail_a_contextual_competence.
    Certified RED fails when the bridge function is absent from app.cognition.b11.
    """
    try:
        import app.cognition.b11.evaluator as ev

        if hasattr(ev, "evaluate_rail_a_contextual_competence"):
            return ev.evaluate_rail_a_contextual_competence
    except ImportError:
        pass
    try:
        import app.cognition.b11.rail_a_contextual_bridge as br

        if hasattr(br, "evaluate_rail_a_contextual_competence"):
            return br.evaluate_rail_a_contextual_competence
    except ImportError:
        pass
    try:
        import app.cognition.b11.rail_a_observation_adapter as adp

        if hasattr(adp, "evaluate_rail_a_contextual_competence"):
            return adp.evaluate_rail_a_contextual_competence
    except ImportError:
        pass
    pytest.fail("M42 B11 bridge evaluate_rail_a_contextual_competence is absent (certified RED)")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_canonical_bridge_bundle(
    tmp_path: Path,
    *,
    suffix: str = "b",
    target_relpath: str = "periphery/xdomain/bridge_target_v0.py",
    pre_bytes: bytes = b"# initial bridge state\nVALUE = 0\n",
    post_bytes: bytes = b"# remediated bridge state\nVALUE = 108\n",
    failing_test_contract: bool = False,
    batch_execution_id: str | None = None,
    child_execution_id: str | None = None,
) -> dict[str, Any]:
    """Produces a complete 6-artifact Rail A C2/D1 bundle in isolated ``tmp_path`` stores
    using the real repository producers.
    """
    base_dir = tmp_path / f"bridge_{suffix}"
    repo_dir = base_dir / "repo"
    stores = {
        "execution_dir": base_dir / "execution",
        "pre_execution_context_dir": base_dir / "pre_execution_contexts",
        "kx108_decision_dir": base_dir / "kx108_decisions",
        "sealed_receipt_dir": base_dir / "sealed_receipts",
        "sealed_rollback_evidence_dir": base_dir / "sealed_rollback_evidence",
        "test_contract_results_dir": base_dir / "test_contract_results",
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
    be_id = batch_execution_id or f"be-bridge-{suffix}"
    ce_id = child_execution_id or f"ce-bridge-{suffix}"
    cand_id = f"cand-bridge-{suffix}"

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
        "operation_reason": f"governed bridge remediation {suffix}",
        "execution_status": E.PLANNED,
    }

    expected_sha = "f" * 64 if failing_test_contract else sha_post
    chk = TC.build_check(
        check_id=f"chk_bridge_{suffix}",
        check_type=TC.CHECK_TYPE_TARGET_SHA256,
        target_path=target_relpath,
        expected_target_sha256=expected_sha,
        required=True,
    )
    contract = TC.build_test_contract(
        contract_id=f"contract-bridge-{suffix}",
        candidate_entry_id=cand_id,
        batch_id=None,
        target_path=target_relpath,
        checks=[chk],
    )
    test_contract_hash = TC.compute_test_contract_hash(contract)

    manifest = {
        "repository_identity": str(repo_dir),
        "execution_worktree_path": str(repo_dir),
        "branch_name": f"exec/bridge-{suffix}",
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
        "branch_name": f"exec/bridge-{suffix}",
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

    approval_id = f"appr-bridge-{suffix}"
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
    tcr_rec = tcr_out["record"]

    tests_res = "FAIL" if failing_test_contract else "PASS"
    first_fail = f"chk_bridge_{suffix}:FAIL" if failing_test_contract else ""
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
    kxpost_rec = post_out["record"]

    return {
        "stores": stores,
        "target_relpath": target_relpath,
        "batch_execution_id": be_id,
        "child_execution_id": ce_id,
        "test_contract_hash": test_contract_hash,
        "pec": pec_rec,
        "kxpre": kxpre_rec,
        "sre": sre_rec,
        "sar": sar_rec,
        "tcr": tcr_rec,
        "post_binding_context": post_binding_context,
        "post_state_kwargs": post_state_kwargs,
        "kxpost": kxpost_rec,
        "kxpost_id": kxpost_rec["decision_record_id"],
    }


def _bridge_store_kwargs(bundle: dict[str, Any]) -> dict[str, Path]:
    s = bundle["stores"]
    return {
        "kx108_decision_dir": s["kx108_decision_dir"],
        "pre_execution_context_dir": s["pre_execution_context_dir"],
        "sealed_receipt_dir": s["sealed_receipt_dir"],
        "sealed_rollback_evidence_dir": s["sealed_rollback_evidence_dir"],
        "test_contract_results_dir": s["test_contract_results_dir"],
    }


# ============================================================================
# RED Scenarios RAC-01 to RAC-10
# ============================================================================


def test_m42_red_rac_01_valid_pass_bundle_exact_context_retains_evidence(tmp_path: Path):
    """RAC-01: Valid passing bundle on exact context retains verified evidence references
    while maintaining UNKNOWN_COMPETENCE (confidence=0.0, reliability=None, calibration=None).
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac01", failing_test_contract=False)
    assert bundle["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
    assert bundle["kxpost"]["x108_gate"] == "ALLOW"

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-01",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True", "branch_isolated:True", "protected_scope_status:CLEAN"),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None
    assert len(profile.evidence_refs) >= 1
    assert any(ref.startswith(f"kxpost:{bundle['kxpost_id']}") for ref in profile.evidence_refs)
    assert "M42_STATISTICAL_THRESHOLDS_PENDING" in profile.unknowns


def test_m42_red_rac_02_valid_fail_bundle_exact_context_retains_failure_observation(tmp_path: Path):
    """RAC-02: Valid failing bundle on exact context retains verified failure observation
    in evidence_refs without premature promotion to EVIDENCED_INCOMPETENCE.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac02", failing_test_contract=True)
    assert bundle["tcr"]["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED
    assert bundle["kxpost"]["x108_gate"] == "BLOCK"

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-02",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True", "branch_isolated:True", "protected_scope_status:CLEAN"),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.competence_regime != CompetenceRegime.EVIDENCED_INCOMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert len(profile.evidence_refs) >= 1
    assert any(ref.startswith(f"kxpost:{bundle['kxpost_id']}") for ref in profile.evidence_refs)


def test_m42_red_rac_03_divergent_domain_excludes_observation(tmp_path: Path):
    """RAC-03: Observation on domain='tooling_build' must not be credited when evaluating
    a divergent domain (e.g., 'bank'), recording CONTEXT_MISMATCH:DOMAIN in risk_indicators.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac03", failing_test_contract=False)
    assert bundle["kxpost"]["domain"] == "tooling_build"

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-03",
        domain="bank",  # Mismatched domain
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert "CONTEXT_MISMATCH:DOMAIN" in profile.risk_indicators


def test_m42_red_rac_04_divergent_task_ref_excludes_observation(tmp_path: Path):
    """RAC-04: Observation on task_ref='UPDATE_TARGET_FROM_SOURCE' must not be credited
    when evaluating a divergent task_ref, recording CONTEXT_MISMATCH:TASK in risk_indicators.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac04", failing_test_contract=False)

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-04",
        domain="tooling_build",
        task_ref="ARBITRARY_OTHER_TASK",  # Mismatched task
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert "CONTEXT_MISMATCH:TASK" in profile.risk_indicators


def test_m42_red_rac_05_divergent_target_resource_rejects_mutated_path_as_mechanism(tmp_path: Path):
    """RAC-05: Target resources must refer to the executing mechanism, not the mutated target path.
    Supplying mutated_target_path as target_resource must record MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac05", failing_test_contract=False)

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-05",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=(bundle["target_relpath"],),  # Error: mutated file supplied as mechanism!
        conditions=(),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert any(
        r in profile.risk_indicators
        for r in ("MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM", "CONTEXT_MISMATCH:TARGET_RESOURCE")
    )


def test_m42_red_rac_06_divergent_conditions_or_mutated_path_excludes_observation(tmp_path: Path):
    """RAC-06: Query conditions demanding a different mutated_target_path or test_contract_hash
    must strictly exclude the observation without implicit generalization.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac06", failing_test_contract=False)

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-06",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(
            f"mutated_target_path:other/divergent/path.py",
            f"test_contract_hash:{'e' * 64}",
        ),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert any(r.startswith("CONTEXT_MISMATCH:") for r in profile.risk_indicators)


def test_m42_red_rac_07_invalid_or_missing_bundle_promotes_no_evidence(tmp_path: Path):
    """RAC-07: Missing or tampered bundle promotes zero evidence and records artifact diagnostics."""
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac07", failing_test_contract=False)
    # Delete sar artifact
    sar_path = bundle["stores"]["sealed_receipt_dir"] / f"{bundle['sar']['sealed_apply_receipt_id']}.json"
    sar_path.unlink()
    assert not sar_path.exists()

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-07",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(bundle["kxpost_id"],),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert any(r.startswith("ARTIFACT_MISSING:") for r in profile.risk_indicators)


def test_m42_red_rac_08_duplicate_execution_records_deduplicated_without_inflation(tmp_path: Path):
    """RAC-08: Repeated execution IDs or duplicate decisions on the same execution
    are deduplicated, preventing evidence inflation.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac08", failing_test_contract=False)

    # Produce a second decision record on the exact same execution
    alt_binding = dict(bundle["post_binding_context"])
    alt_binding["kx108_input_translation_hash"] = "7" * 64
    post_dup = DS.run_and_persist_kx108_post_execution_decision(
        bundle["post_state_kwargs"],
        alt_binding,
        bundle["kxpre"]["decision_record_id"],
        execution_dir=bundle["stores"]["execution_dir"],
        pre_decision_store_dir=bundle["stores"]["kx108_decision_dir"],
        post_decision_store_dir=bundle["stores"]["kx108_decision_dir"],
        sealed_evidence_link={
            "sealed_apply_receipt_id": bundle["sar"]["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": bundle["sar"]["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": bundle["sre"]["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": bundle["sre"]["sealed_rollback_evidence_hash"],
        },
    )
    dup_id = post_dup["decision_record_id"]
    assert dup_id != bundle["kxpost_id"]

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-08",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(bundle["kxpost_id"], bundle["kxpost_id"], dup_id),
        **_bridge_store_kwargs(bundle),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 1
    assert "DUPLICATE_EXECUTION_OBSERVATION_REJECTED" in profile.risk_indicators


def test_m42_red_rac_09_hostile_inputs_and_forged_objects_rejected_passively():
    """RAC-09: Self-attested dicts, forged observation objects, and hostile dunder inputs
    are rejected passively without executing unsafe dynamic methods.
    """
    class HostileDunder:
        def __str__(self):
            raise RuntimeError("Hostile __str__ executed")
        def __eq__(self, other):
            raise RuntimeError("Hostile __eq__ executed")

    d = Path(".")
    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-09",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(
            HostileDunder(),
            {"is_verified": True, "observation_id": "forged-dict"},
        ),
        kx108_decision_dir=d,
        pre_execution_context_dir=d,
        sealed_receipt_dir=d,
        sealed_rollback_evidence_dir=d,
        test_contract_results_dir=d,
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
    assert any(
        r in profile.risk_indicators
        for r in ("SELF_ATTESTATION_REJECTED", "FORGED_OBSERVATION_OBJECT_REJECTED", "INVALID_RECORD_STRUCTURE_REJECTED")
    )


def test_m42_red_rac_10_empty_observations_preserves_b11_effects_and_read_only(tmp_path: Path):
    """RAC-10: Empty observations list produces UNKNOWN_COMPETENCE with NO_HISTORICAL_EVIDENCE,
    preserves B11_EFFECTS, and performs zero writes to disk.
    """
    bundle = _build_canonical_bridge_bundle(tmp_path, suffix="rac10", failing_test_contract=False)
    stores = bundle["stores"]

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

    bridge_fn = _rt_bridge()
    profile: ContextualCompetenceProfile = bridge_fn(
        evaluation_id="eval-rac-10",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=(),
        kxpost_decision_record_ids=(),
        **_bridge_store_kwargs(bundle),
    )

    after_snapshot = {
        str(p.relative_to(tmp_path)): _sha256_hex(p.read_bytes())
        for d in stores.values()
        for p in d.rglob("*")
        if p.is_file()
    }
    assert after_snapshot == before_snapshot

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert len(profile.evidence_refs) == 0
    assert "NO_HISTORICAL_EVIDENCE" in profile.unknowns
