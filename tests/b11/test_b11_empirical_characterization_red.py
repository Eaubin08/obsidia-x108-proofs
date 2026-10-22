"""M42 B11 Compétence & Calibration — RED test harness for Empirical Characterization V1.

Source of truth:
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_VERIFIED_OBSERVATION_SPEC_V1.md
  docs/architecture/M42_B11_RAIL_A_CONTEXTUAL_BRIDGE_SPEC_V1.md
  docs/architecture/M42_B11_EMPIRICAL_CHARACTERIZATION_SPEC_V1.md

Runtime target (absent at RED):
  ``characterize_empirical_observations`` in ``app.cognition.b11.empirical_characterization``

Design & Quality Guarantees:
1. All fixtures use real canonical producers from ``scripts/`` and the Rail A observation pipeline.
2. Every scenario performs and asserts discriminating preconditions on the canonical artifacts
   BEFORE invoking the lazy loader ``_rt_empirical()``.
3. Synthetic fixtures are explicitly labeled as such; test fixtures are not conflated with
   real production historical corpora.
4. Every test fails cleanly with certified RED when ``characterize_empirical_observations`` is absent.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence

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
from tests.b11.test_b11_rail_a_contextual_bridge_red import (  # noqa: E402
    _bridge_store_kwargs,
    _build_canonical_bridge_bundle,
)


def _rt_empirical():
    """Lazy loader for characterize_empirical_observations.
    Certified RED fails when the function is absent from app.cognition.b11.
    """
    try:
        import app.cognition.b11.empirical_characterization as ec

        if hasattr(ec, "characterize_empirical_observations"):
            return ec.characterize_empirical_observations
    except ImportError:
        pass
    try:
        import app.cognition.b11.evaluator as ev

        if hasattr(ev, "characterize_empirical_observations"):
            return ev.characterize_empirical_observations
    except ImportError:
        pass
    pytest.fail("M42 B11 characterize_empirical_observations is absent (certified RED)")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_canonical_empirical_bundle(
    tmp_path: Path,
    *,
    suffix: str = "b",
    base_dir: Path | None = None,
    contract_suffix: str | None = None,
    candidate_entry_id: str | None = None,
    target_relpath: str = "periphery/xdomain/bridge_target_v0.py",
    pre_bytes: bytes = b"# initial bridge state\nVALUE = 0\n",
    post_bytes: bytes = b"# remediated bridge state\nVALUE = 108\n",
    failing_test_contract: bool = False,
    batch_execution_id: str | None = None,
    child_execution_id: str | None = None,
) -> dict[str, Any]:
    """Produces a complete 6-artifact Rail A C2/D1 bundle using real repository producers.
    Allows passing a shared base_dir to co-locate multiple bundles in common canonical stores.
    """
    eff_base_dir = base_dir or (tmp_path / f"bridge_{suffix}")
    repo_dir = eff_base_dir / "repo"
    stores = {
        "execution_dir": eff_base_dir / "execution",
        "pre_execution_context_dir": eff_base_dir / "pre_execution_contexts",
        "kx108_decision_dir": eff_base_dir / "kx108_decisions",
        "sealed_receipt_dir": eff_base_dir / "sealed_receipts",
        "sealed_rollback_evidence_dir": eff_base_dir / "sealed_rollback_evidence",
        "test_contract_results_dir": eff_base_dir / "test_contract_results",
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
    cand_id = candidate_entry_id or f"cand-bridge-{suffix}"

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

    c_suf = contract_suffix or suffix
    expected_sha = "f" * 64 if failing_test_contract else sha_post
    chk = TC.build_check(
        check_id=f"chk_bridge_{c_suf}",
        check_type=TC.CHECK_TYPE_TARGET_SHA256,
        target_path=target_relpath,
        expected_target_sha256=expected_sha,
        required=True,
    )
    contract = TC.build_test_contract(
        contract_id=f"contract-bridge-{c_suf}",
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


_bundle_store_kwargs = _bridge_store_kwargs


# ============================================================================
# Scénarios RED REC-01 à REC-08
# ============================================================================


def test_m42_red_rec_01_absence_of_observation(tmp_path: Path):
    """REC-01: Absence totale d'observations.
    Compte zéro, taux descriptif indéfini (None), diagnostic NO_HISTORICAL_EVIDENCE,
    profil UNKNOWN_COMPETENCE (conf=0.0, rel=None, calib=None).
    """
    d = tmp_path / "empty_stores"
    for sub in ("dec", "pec", "sar", "sre", "tcr"):
        (d / sub).mkdir(parents=True, exist_ok=True)

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-01",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=(),
        kx108_decision_dir=d / "dec",
        pre_execution_context_dir=d / "pec",
        sealed_receipt_dir=d / "sar",
        sealed_rollback_evidence_dir=d / "sre",
        test_contract_results_dir=d / "tcr",
    )

    assert char.raw_observation_count == 0
    assert char.distinct_execution_count == 0
    assert char.retained_in_context_count == 0
    assert char.pass_count == 0
    assert char.fail_count == 0
    assert char.error_count == 0
    assert char.observed_success_rate is None
    assert char.descriptive_admissibility_status == "NO_DATA"
    assert char.data_provenance_type == "UNAUTHENTICATED"
    assert "NO_HISTORICAL_EVIDENCE" in char.unknowns

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None
    assert len(profile.evidence_refs) == 0
    assert "NO_HISTORICAL_EVIDENCE" in profile.unknowns


def test_m42_red_rec_02_two_distinct_successes_no_arbitrary_promotion(tmp_path: Path):
    """REC-02: Deux succès distincts vérifiés.
    Taux descriptif 2/2 = 1.0, admissibilité descriptive pure, mais aucune compétence promue
    et aucun N_min arbitraire appliqué (maintien sous UNKNOWN_COMPETENCE).
    """
    shared_base = tmp_path / "shared_rec02"
    b1 = _build_canonical_empirical_bundle(tmp_path, suffix="rec02_1", base_dir=shared_base, failing_test_contract=False)
    b2 = _build_canonical_empirical_bundle(tmp_path, suffix="rec02_2", base_dir=shared_base, failing_test_contract=False)

    assert b1["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
    assert b2["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
    assert b1["child_execution_id"] != b2["child_execution_id"]

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-02",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=(b1["kxpost_id"], b2["kxpost_id"]),
        **_bundle_store_kwargs(b1),
    )

    assert char.raw_observation_count == 2
    assert char.distinct_execution_count == 2
    assert char.retained_in_context_count == 2
    assert char.pass_count == 2
    assert char.fail_count == 0
    assert char.error_count == 0
    assert char.observed_success_rate == 1.0
    assert char.descriptive_admissibility_status == "ADMISSIBLE_DESCRIPTIVE_ONLY"

    # F-EMP-01 : Intégrité locale vérifiée mais provenance d'origine non attestée
    assert char.data_provenance_type == "PROVENANCE_UNESTABLISHED"
    assert char.data_provenance_type != "CANONICAL_FIXTURE_STORE"
    assert char.data_provenance_type != "HISTORICAL_PRODUCTION_STORE"
    assert "LOCAL_INTEGRITY_VERIFIED" in char.diagnostic_codes

    # Vérification doctrinale : aucune promotion positive sur 2 succès
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None
    assert len(profile.evidence_refs) == 2


def test_m42_red_rec_03_twenty_executions_single_target_not_established_independence(tmp_path: Path):
    """REC-03: Vingt exécutions distinctes sur la même cible et même contrat.
    Un seul groupe contextuel (context_group_count == 1), indépendance statistique NON ÉTABLIE.
    Rejet de l'inflation de preuve par répétition locale.
    """
    shared_base = tmp_path / "shared_rec03"
    ids = []
    bundle_ref = None
    for i in range(20):
        b = _build_canonical_empirical_bundle(
            tmp_path,
            suffix=f"rec03_{i:02d}",
            base_dir=shared_base,
            contract_suffix="rec03_shared",
            candidate_entry_id="cand-bridge-rec03_shared",
            target_relpath="shared/mono_target.py",
            failing_test_contract=False,
        )
        if bundle_ref is None:
            bundle_ref = b
        ids.append(b["kxpost_id"])

    assert len(ids) == 20
    assert len(set(ids)) == 20

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-03",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=tuple(ids),
        **_bundle_store_kwargs(bundle_ref),
    )

    assert char.raw_observation_count == 20
    assert char.distinct_execution_count == 20
    assert char.retained_in_context_count == 20
    assert char.context_group_count == 1
    assert char.statistical_independence_status == "MONO_CONTEXT_INDEPENDENCE_UNESTABLISHED"
    assert char.data_provenance_type == "PROVENANCE_UNESTABLISHED"

    # Invariant : pas de promotion par grand N corrélé
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None


def test_m42_red_rec_04_mixed_pass_and_fail_records_empirical_variability(tmp_path: Path):
    """REC-04: Quatre PASS et quatre FAIL vérifiés.
    Taux descriptif 4/8 = 0.5, variabilité empirique consignée (EMPIRICAL_VARIABILITY_OBSERVED),
    aucun diagnostic erroné de contradiction logique d'invariants.
    """
    shared_base = tmp_path / "shared_rec04"
    pass_ids = []
    fail_ids = []
    ref_bundle = None
    for i in range(4):
        bp = _build_canonical_empirical_bundle(tmp_path, suffix=f"rec04_p{i}", base_dir=shared_base, failing_test_contract=False)
        bf = _build_canonical_empirical_bundle(tmp_path, suffix=f"rec04_f{i}", base_dir=shared_base, failing_test_contract=True)
        if ref_bundle is None:
            ref_bundle = bp
        assert bp["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
        assert bf["tcr"]["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED
        pass_ids.append(bp["kxpost_id"])
        fail_ids.append(bf["kxpost_id"])

    all_ids = tuple(pass_ids + fail_ids)
    assert len(all_ids) == 8

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-04",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=all_ids,
        **_bundle_store_kwargs(ref_bundle),
    )

    assert char.retained_in_context_count == 8
    assert char.pass_count == 4
    assert char.fail_count == 4
    assert char.error_count == 0
    assert char.observed_success_rate == 0.5
    assert "EMPIRICAL_VARIABILITY_OBSERVED" in char.diagnostic_codes
    assert "CONTRADICTION" not in char.diagnostic_codes

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.contradictions) == 0


def test_m42_red_rec_05_six_failures_no_evidenced_incompetence_decreed(tmp_path: Path):
    """REC-05: Six échecs vérifiés.
    Taux observé 0/6 = 0.0, aucune fiabilité future nulle décrétée,
    aucune promotion prématurée en EVIDENCED_INCOMPETENCE (maintien sous UNKNOWN_COMPETENCE).
    """
    shared_base = tmp_path / "shared_rec05"
    fail_ids = []
    ref_b = None
    for i in range(6):
        bf = _build_canonical_empirical_bundle(tmp_path, suffix=f"rec05_{i}", base_dir=shared_base, failing_test_contract=True)
        if ref_b is None:
            ref_b = bf
        assert bf["tcr"]["aggregate_status"] == TC.AGGREGATE_REQUIRED_TEST_FAILED
        fail_ids.append(bf["kxpost_id"])

    assert len(fail_ids) == 6

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-05",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=tuple(fail_ids),
        **_bundle_store_kwargs(ref_b),
    )

    assert char.retained_in_context_count == 6
    assert char.pass_count == 0
    assert char.fail_count == 6
    assert char.observed_success_rate == 0.0

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.competence_regime != CompetenceRegime.EVIDENCED_INCOMPETENCE
    assert profile.reliability_score is None
    assert profile.confidence_score == 0.0


def test_m42_red_rec_06_ten_distinct_contexts_no_transcontextual_inference(tmp_path: Path):
    """REC-06: Dix succès sur des contextes distincts.
    Dix observations décrites, 10 groupes contextuels préservés, aucun regroupement transcontextuel
    inférentiel sans règle de transférabilité, aucune promotion EVIDENCED_COMPETENCE.
    """
    shared_base = tmp_path / "shared_rec06"
    ids = []
    ref_b = None
    for i in range(10):
        b = _build_canonical_empirical_bundle(
            tmp_path,
            suffix=f"rec06_{i}",
            base_dir=shared_base,
            target_relpath=f"modules/mod_{i}/target.py",
            failing_test_contract=False,
        )
        if ref_b is None:
            ref_b = b
        assert b["tcr"]["aggregate_status"] == TC.AGGREGATE_ALL_REQUIRED_PASS
        ids.append(b["kxpost_id"])

    assert len(ids) == 10

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-06",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=tuple(ids),
        **_bundle_store_kwargs(ref_b),
    )

    assert char.retained_in_context_count == 10
    assert char.pass_count == 10
    assert char.context_group_count == 10
    assert char.statistical_independence_status in ("INDEPENDENCE_NOT_ASSUMED", "NOT_ESTABLISHED")

    # Invariant : pas de promotion positive malgré 10 succès distincts
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.reliability_score is None
    assert profile.confidence_score == 0.0


def test_m42_red_rec_07_descriptive_rate_without_predictive_calibration(tmp_path: Path):
    """REC-07: Quatre PASS et un FAIL, sans prédictions probabilistes ex-ante.
    Taux descriptif 4/5 = 0.8 calculé, predictive_data_status="PREDICTIVE_DATA_ABSENT",
    calibration_metric=None (absence de prédictions ex-ante scellées).
    """
    shared_base = tmp_path / "shared_rec07"
    ids = []
    ref_b = None
    for i in range(4):
        bp = _build_canonical_empirical_bundle(tmp_path, suffix=f"rec07_p{i}", base_dir=shared_base, failing_test_contract=False)
        if ref_b is None:
            ref_b = bp
        ids.append(bp["kxpost_id"])
    bf = _build_canonical_empirical_bundle(tmp_path, suffix="rec07_f0", base_dir=shared_base, failing_test_contract=True)
    ids.append(bf["kxpost_id"])

    assert len(ids) == 5

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-07",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        target_resources=("rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=tuple(ids),
        **_bundle_store_kwargs(ref_b),
    )

    assert char.retained_in_context_count == 5
    assert char.pass_count == 4
    assert char.fail_count == 1
    assert char.observed_success_rate == 0.8
    assert char.predictive_data_status == "PREDICTIVE_DATA_ABSENT"
    assert "PREDICTIVE_CALIBRATION_UNAVAILABLE" in char.unknowns

    assert profile.calibration_metric is None
    assert "PREDICTIVE_CALIBRATION_UNAVAILABLE" in profile.unknowns


def test_m42_red_rec_08_causal_attribution_rejection_and_effects_invariance(tmp_path: Path):
    """REC-08: Tentative d'attribuer des observations Rail A à Brody ou à une autre ressource.
    Refus d'attribution immédiat (CAUSAL_ATTRIBUTION_MISMATCH), zéro preuve attribuée,
    respect strict de B11_EFFECTS et zéro I/O disque résiduel.
    """
    b = _build_canonical_empirical_bundle(tmp_path, suffix="rec08", failing_test_contract=False)
    stores = b["stores"]

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

    char_fn = _rt_empirical()
    char, profile = char_fn(
        characterization_id="char-rec-08",
        domain="tooling_build",
        task_ref="UPDATE_TARGET_FROM_SOURCE",
        # Incompatible target resource: Brody is not the Rail A mechanism!
        target_resources=("brody:cognitive_resolution",),
        conditions=("worktree_isolated:True",),
        kxpost_decision_record_ids=(b["kxpost_id"],),
        **_bundle_store_kwargs(b),
    )

    after_snapshot = {
        str(p.relative_to(tmp_path)): _sha256_hex(p.read_bytes())
        for d in stores.values()
        for p in d.rglob("*")
        if p.is_file()
    }
    assert after_snapshot == before_snapshot

    assert char.retained_in_context_count == 0
    assert char.excluded_count >= 1
    assert any(
        d in char.diagnostic_codes
        for d in ("CAUSAL_ATTRIBUTION_MISMATCH", "CONTEXT_MISMATCH:TARGET_RESOURCE")
    )
    assert len(char.evidence_refs) == 0

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert len(profile.evidence_refs) == 0
