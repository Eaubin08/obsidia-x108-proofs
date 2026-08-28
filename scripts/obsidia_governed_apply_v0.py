"""
obsidia_governed_apply_v0.py
============================
CONTENT_BOUND_GOVERNED_PREFLIGHT_C1_V0 — préflight de gouvernance
pré-mutation, STRICTEMENT READ_ONLY et NON_SOVEREIGN.

Ce module ne mute AUCUNE cible et ne contient AUCUNE fonction d'écriture.
`run_governed_content_apply` N'EXISTE PAS ici (Checkpoint C2).

`validate_governed_apply_preflight(...)` prouve que TOUTES les liaisons
d'exécution courantes concordent encore, dans l'ordre canonique gelé :

  ExecutionEnvelope → execution_authority_hash (recalculé)
  → HumanApproval canonique (chargée/vérifiée/validée)
  → KX108_PRE decision (decision_phase=PRE_EXECUTION, x108_gate=ALLOW,
    lié au même execution_authority_hash + au même approval_id)
  → PreExecutionContext canonique vérifié
  → confinement du chemin source + SHA256 COMPLET du contenu source
  → précondition de cible (SHA256 complet) + scope/protection
  → PREFLIGHT_PASS

decision_authority reste KX108_ONLY. KX108_PRE est le seul ALLOW souverain ;
ce préflight n'émet JAMAIS "ALLOW". Un PREFLIGHT_PASS n'est PAS un jeton
d'autorisation d'exécution : C2 devra tout RECHARGER/REVÉRIFIER juste avant
la mutation (PREFLIGHT_CACHE_AUTHORITY = NONE).
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_batch_execution as _E
import obsidia_content_apply as _C
import obsidia_pre_execution_context as _PEC
import obsidia_kx108_decision_store as _DS
import obsidia_batch_selector as _S

AUTHORITY = "NON_SOVEREIGN"
DECISION_AUTHORITY = "KX108_ONLY"
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"
PREFLIGHT_CACHE_AUTHORITY = "NONE"

STATUS_PASS = "PREFLIGHT_PASS"
STATUS_HOLD = "PREFLIGHT_HOLD"

_SHA256_HEX_LEN = 64


def _hold(reason: str, **extra) -> dict:
    return {
        "status": STATUS_HOLD,
        "reason": reason,
        "authority": AUTHORITY,
        "write_capability": False,
        **extra,
    }


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_full_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == _SHA256_HEX_LEN and all(
        c in "0123456789abcdef" for c in v.lower()
    )


def validate_governed_apply_preflight(
    batch_execution_id: str,
    child_execution_id: str,
    approval_id: str,
    kx108_pre_decision_record_id: str,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
    kx108_decision_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    ledger_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    *,
    derived_authority_context=None,
) -> dict:
    """
    Retourne un dict {status: PREFLIGHT_PASS | PREFLIGHT_HOLD, reason, ...}.
    L'appelant fournit UNIQUEMENT des identifiants ; cette fonction charge
    elle-même les artefacts canoniques depuis leurs magasins et recalcule
    les hash d'autorité. Aucun dict/hash/octet fourni par l'appelant n'est
    traité comme autorité. Aucune mutation, aucune écriture.
    """
    root = Path(repo_root or _C._REPO_ROOT).resolve()

    # ── 1. ExecutionEnvelope ────────────────────────────────────────────
    envelope = _E._load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return _hold("ENVELOPE_NOT_FOUND")
    if not isinstance(envelope, dict):
        return _hold("ENVELOPE_MALFORMED")
    if not envelope.get("integrity_verified"):
        return _hold("ENVELOPE_INTEGRITY_NOT_VERIFIED")
    if envelope.get("decision_authority") != DECISION_AUTHORITY:
        return _hold("ENVELOPE_DECISION_AUTHORITY_NOT_KX108_ONLY")

    stored_eah = envelope.get("execution_authority_hash")
    recomputed_eah = _E.compute_execution_authority_hash(envelope)
    if not stored_eah or recomputed_eah != stored_eah:
        return _hold("EXECUTION_AUTHORITY_HASH_DRIFT",
                     expected=stored_eah, recomputed=recomputed_eah)

    # ── 2. ChildExecutionRecord exact ──────────────────────────────────
    child = next(
        (c for c in (envelope.get("children") or [])
         if c.get("child_execution_id") == child_execution_id),
        None,
    )
    if child is None:
        return _hold("CHILD_NOT_FOUND")
    if child.get("execution_status") != _E.PLANNED:
        return _hold("CHILD_NOT_PLANNED", actual=child.get("execution_status"))
    if child.get("operation_type") != OPERATION_TYPE:
        # couvre l'absence de support DELETE / toute autre opération
        return _hold("UNSUPPORTED_OPERATION", operation_type=child.get("operation_type"))

    # ── 3. HumanApproval canonique ────────────────────────────────────
    approval = _E.load_approval_artifact(approval_id, execution_dir)
    if approval is None:
        return _hold("HUMAN_APPROVAL_NOT_FOUND")
    ok_a, reason_a = _E.verify_approval_artifact(approval)
    if not ok_a:
        return _hold(f"HUMAN_APPROVAL_ARTIFACT_INVALID:{reason_a}")
    ok_v, reason_v = _E._validate_approval(
        approval, envelope, derived_authority_context=derived_authority_context)
    if not ok_v:
        return _hold(f"HUMAN_APPROVAL_NOT_BOUND_TO_EXECUTION:{reason_v}")
    if approval.get("execution_authority_hash") != recomputed_eah:
        return _hold("HUMAN_APPROVAL_EXECUTION_AUTHORITY_HASH_MISMATCH")

    # ── 4. KX108_PRE decision record ─────────────────────────────────
    pre = _DS.load_kx108_decision_record(kx108_pre_decision_record_id, kx108_decision_dir)
    if pre is None:
        return _hold("KX108_PRE_DECISION_NOT_FOUND")
    ok_p, reason_p = _DS.verify_kx108_decision_record(pre)
    if not ok_p:
        return _hold(f"KX108_PRE_DECISION_INVALID:{reason_p}")
    if _DS.decision_phase_of(pre) != _DS.PRE_DECISION_PHASE:
        return _hold("KX108_DECISION_NOT_PRE_EXECUTION_PHASE", phase=_DS.decision_phase_of(pre))
    if pre.get("x108_gate") != "ALLOW":
        return _hold("KX108_PRE_GATE_NOT_ALLOW", x108_gate=pre.get("x108_gate"))
    if pre.get("execution_authority_hash") != recomputed_eah:
        return _hold("KX108_PRE_EXECUTION_AUTHORITY_HASH_MISMATCH")
    if pre.get("approval_id") != approval_id:
        return _hold("KX108_PRE_APPROVAL_ID_MISMATCH",
                     pre_approval_id=pre.get("approval_id"), approval_id=approval_id)

    # ── 5. PreExecutionContext canonique ────────────────────────────
    pcid = envelope.get("pre_execution_context_id")
    if not pcid:
        return _hold("PRE_EXECUTION_CONTEXT_REQUIRED")
    pctx = _PEC.load_pre_execution_context_record(pcid, pre_execution_context_dir)
    ok_c, reason_c = _PEC.verify_pre_execution_context_record(pctx)
    if not ok_c:
        return _hold(f"PRE_EXECUTION_CONTEXT_INVALID:{reason_c}")
    if pctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
        return _hold("PRE_EXECUTION_CONTEXT_HASH_MISMATCH")
    if pctx.get("decision_authority") != DECISION_AUTHORITY:
        return _hold("PRE_EXECUTION_CONTEXT_DECISION_AUTHORITY_NOT_KX108_ONLY")
    if not (pctx.get("worktree_isolated") and pctx.get("branch_isolated")):
        return _hold("PRE_EXECUTION_CONTEXT_ISOLATION_NOT_VERIFIED")
    if pctx.get("protected_scope_status") != "CLEAN":
        return _hold("PRE_EXECUTION_CONTEXT_PROTECTED_SCOPE_NOT_CLEAN")

    # ── 6. Confinement du chemin source (durcissement C1) ──────────
    source_path = child.get("source_path")
    if not source_path or not str(source_path).strip():
        return _hold("SOURCE_PATH_MISSING")
    sp = Path(str(source_path).strip())
    sp = sp if sp.is_absolute() else (root / str(source_path).strip())
    try:
        sp_resolved = sp.resolve()
    except OSError as exc:
        return _hold(f"SOURCE_PATH_UNRESOLVABLE:{exc}")
    try:
        sp_resolved.relative_to(root)
    except ValueError:
        return _hold("SOURCE_PATH_ESCAPE", resolved=str(sp_resolved))
    if os.path.islink(str(sp)) and not str(sp_resolved).startswith(str(root) + os.sep):
        return _hold("SOURCE_SYMLINK_ESCAPE", resolved=str(sp_resolved))
    if not sp_resolved.exists():
        return _hold("SOURCE_FILE_MISSING", resolved=str(sp_resolved))
    if not sp_resolved.is_file():
        return _hold("SOURCE_NOT_REGULAR_FILE", resolved=str(sp_resolved))
    source_path_confined = True

    # ── 7. Contenu source : octets relus MAINTENANT + SHA256 COMPLET ──
    bound_source_sha256 = child.get("source_content_sha256")
    if not _is_full_sha256(bound_source_sha256):
        return _hold("SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX")
    src_bytes, src_reason = _C.resolve_source_bytes(child, root)
    if src_bytes is None:
        return _hold(f"SOURCE_RESOLVE_FAILED:{src_reason}")
    actual_source_sha256 = _sha256_hex(src_bytes)          # comparaison INDÉPENDANTE, complète
    if actual_source_sha256 != bound_source_sha256:
        return _hold("SOURCE_CONTENT_SHA256_MISMATCH",
                     expected=bound_source_sha256, actual=actual_source_sha256)
    source_content_sha256_verified = True

    # ── 8. Cible : canonicalisation + protection + précondition ─────
    target_abs, target_reason = _C.canonicalize_write_target(child.get("target_path"), root)
    if target_reason == "REFUSED_PROTECTED_TARGET":
        return _hold("PROTECTED_TARGET", target_path=child.get("target_path"))
    if target_reason:
        return _hold(f"TARGET_SCOPE_REJECTED:{target_reason}", target_path=child.get("target_path"))

    if target_abs.exists() and target_abs.is_file():
        try:
            cur_target_sha256 = _sha256_hex(target_abs.read_bytes())
        except OSError:
            return _hold("TARGET_UNREADABLE")
    elif target_abs.exists():
        return _hold("TARGET_NOT_REGULAR_FILE")
    else:
        cur_target_sha256 = None

    expected_pre = child.get("target_pre_sha256")
    if expected_pre is None:
        # CREATE : la cible DOIT être absente
        if cur_target_sha256 is not None:
            return _hold("TARGET_EXISTS_FOR_CREATE", actual=cur_target_sha256)
        target_operation = "CREATE"
    else:
        # REPLACE : SHA256 complet de la cible relue == précondition liée
        if not _is_full_sha256(expected_pre):
            return _hold("TARGET_PRE_SHA256_NOT_FULL_64_HEX")
        if cur_target_sha256 != expected_pre:
            return _hold("TARGET_PRECONDITION_MISMATCH",
                         expected=expected_pre, actual=cur_target_sha256)
        expected_pre16 = child.get("target_pre_hash")
        if expected_pre16 is not None and (cur_target_sha256 or "")[:16] != expected_pre16:
            return _hold("TARGET_PRE_HASH16_MISMATCH")
        target_operation = "REPLACE"
    target_pre_sha256_verified = True

    # ── 9. Scope / BatchProposal ──────────────────────────────────
    batch_id = envelope.get("batch_id")
    batch_integrity_checked = False
    scope_source = None
    if selector_dir is not None and batch_id:
        batch = _S._load_batch(batch_id, selector_dir)
        if batch is None:
            return _hold("BATCH_PROPOSAL_NOT_FOUND", batch_id=batch_id)
        if batch.get("batch_hash") != envelope.get("batch_hash"):
            return _hold("BATCH_HASH_MISMATCH")
        ok_b, reason_b = _E.verify_batch_integrity(batch, ledger_dir)
        if not ok_b:
            return _hold(f"BATCH_INTEGRITY_FAILED:{reason_b}")
        sel_target = next(
            (e.get("target_path") for e in (batch.get("selected_entries") or [])
             if e.get("candidate_id") == child.get("candidate_entry_id")),
            None,
        )
        sel_abs, _ = _C.canonicalize_write_target(sel_target, root)
        if sel_abs is None or sel_abs != target_abs:
            return _hold("TARGET_NOT_IN_APPROVED_BATCH_SCOPE", batch_target=sel_target)
        batch_integrity_checked = True
        scope_source = "BATCH_PROPOSAL"
    else:
        # Aucun batch dans la chaîne d'autorité fournie : scope vérifié
        # contre le PreExecutionContext canonique (approved_scope) —
        # jamais un pass silencieux : batch_integrity_checked reste FALSE.
        approved = pctx.get("approved_scope") or []
        if child.get("target_path") not in approved:
            return _hold("TARGET_NOT_IN_PRE_EXECUTION_CONTEXT_SCOPE", approved_scope=approved)
        scope_source = "PRE_EXECUTION_CONTEXT"
    scope_verified = True

    # ── 10. PREFLIGHT_PASS — aucune mutation, non-souverain ─────────
    return {
        "status": STATUS_PASS,
        "reason": None,
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "operation_type": OPERATION_TYPE,
        "target_operation": target_operation,
        "execution_authority_hash": recomputed_eah,
        "approval_id": approval_id,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_pre_gate": pre.get("x108_gate"),
        "source_content_sha256_verified": source_content_sha256_verified,
        "target_pre_sha256_verified": target_pre_sha256_verified,
        "source_path_confined": source_path_confined,
        "scope_verified": scope_verified,
        "scope_source": scope_source,
        "batch_integrity_checked": batch_integrity_checked,
        "protected_scope_status": "CLEAN",
        "pre_execution_context_verified": True,
        "authority": AUTHORITY,
        "write_capability": False,
        "preflight_cache_authority": PREFLIGHT_CACHE_AUTHORITY,
        # jamais d'octets source bruts, jamais de jeton d'exécution réutilisable
    }


# ══════════════════════════════════════════════════════════════════════════
#  C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1 — ENTRYPOINT GOUVERNÉ D'ÉCRITURE
# ══════════════════════════════════════════════════════════════════════════
#
# `run_governed_content_apply(...)` est le SEUL point du système qui porte
# `write_capability = True`. Entrées : identifiants + répertoires de magasin
# UNIQUEMENT. Aucun dict/octet/hash/chemin/EAH/record/disposition fourni par
# l'appelant n'est autorité. Aucun jeton PREFLIGHT_PASS réutilisable.
#
# Aucune issue publique de SUCCÈS avant KX108_POST ALLOW vérifié. La
# fonction poursuit SYNCHRONEMENT : preflight -> source/cible durcies ->
# SealedRollbackEvidence (persistée+vérifiée AVANT écriture) -> mutation ->
# B mesuré -> SealedApplyReceipt (persisté+vérifié) -> TestContractResult ->
# évidence POST liée cryptographiquement au scellé -> KX108_POST lié ->
# disposition D1 -> KEEP | rollback D2.

C2_INTERNAL_APPLY_STAGE_APPLIED = "INTERNAL_APPLY_STAGE_APPLIED_RECEIPT_SEALED"

GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW = "GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW"
GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK = "GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK"
GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE = "GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE"
GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION = "GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION"
GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE = "GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE"

_C2_PUBLIC_STATES = frozenset({
    GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW,
    GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK,
    GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE,
    GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION,
    GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE,
})

KX108_PRE_REVERIFIED_IMMEDIATELY_BEFORE_WRITE = True
C2_SOURCE_CONTENT_REHASH_IMMEDIATELY_BEFORE_WRITE = True
C2_TARGET_PRESTATE_DOUBLE_CHECK = True
WRITE_EXCEPTION_TARGET_STATE_REMEASURED = True
PUBLIC_SUCCESS_BEFORE_KX108_POST_ALLOW = False


def _c2_mod():
    import sys as _s
    _d = str(Path(__file__).resolve().parent)
    if _d not in _s.path:
        _s.path.insert(0, _d)
    import obsidia_sealed_evidence_v0 as SEV
    import obsidia_test_contract as TC
    import obsidia_kx108_evidence_adapter as ADP
    import obsidia_post_execution_disposition_v0 as DISP
    import obsidia_governed_rollback_v0 as RB
    import obsidia_governed_write_guard_v0 as WG
    return SEV, TC, ADP, DISP, RB, WG


def _rej(reason: str, **extra) -> dict:
    return {"status": GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION,
            "reason": reason, "target_mutated": False,
            "authority": AUTHORITY, "decision_authority": DECISION_AUTHORITY, **extra}


def _quarantine(reason: str, **extra) -> dict:
    return {"status": GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE,
            "reason": reason, "authority": AUTHORITY,
            "decision_authority": DECISION_AUTHORITY, **extra}


def _sha256_file(p: Path) -> "Optional[str]":
    try:
        if not p.exists() or not p.is_file():
            return None
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def run_governed_content_apply(
    batch_execution_id: str,
    child_execution_id: str,
    approval_id: str,
    kx108_pre_decision_record_id: str,
    *,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
    kx108_decision_dir: Optional[Path] = None,
    post_decision_store_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    ledger_dir: Optional[Path] = None,
    test_contract_results_dir: Optional[Path] = None,
    sealed_receipt_dir: Optional[Path] = None,
    sealed_rollback_evidence_dir: Optional[Path] = None,
    rollback_result_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    derived_authority_context=None,
) -> dict:
    """Chemin de PRODUCTION gouverné unique — cf. bannière ci-dessus.

    STAGE 4F REPAIR — `derived_authority_context` :
      * ABSENT + `approved_by == HUMAN`  → chemin historique STRICTEMENT
        inchangé (aucun verrou, aucune re-vérif d'autorité de mission).
      * ABSENT + `approved_by` dérivé    → `_validate_approval` échoue fermé
        (`DERIVED_APPROVAL_REQUIRES_CANONICAL_CONTEXT`).
      * PRÉSENT → l'approbation dérivée est re-vérifiée CANONIQUEMENT à
        l'entrée, PUIS la re-vérif finale de fraîcheur + la mutation
        physique + la mesure post-écriture s'exécutent SOUS LE MÊME verrou
        inter-processus (`mission_id`) que le writer de révocation HMA.
    """
    SEV, TC, ADP, DISP, RB, WG = _c2_mod()
    root = Path(repo_root or _C._REPO_ROOT).resolve()

    # ── 1. Revalidation pré-écriture COMPLÈTE (preflight_cache_authority = NONE) ──
    pf = validate_governed_apply_preflight(
        batch_execution_id, child_execution_id, approval_id, kx108_pre_decision_record_id,
        execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
        kx108_decision_dir=kx108_decision_dir, selector_dir=selector_dir,
        ledger_dir=ledger_dir, repo_root=root,
        derived_authority_context=derived_authority_context,
    )
    if pf.get("status") != STATUS_PASS:
        return _rej(f"PREFLIGHT_HOLD:{pf.get('reason')}", preflight=pf)

    # ── 2. Rechargement + revérification isolée (jamais le retour du preflight) ──
    envelope = _E._load_execution(batch_execution_id, execution_dir)
    if envelope is None or not envelope.get("integrity_verified") \
            or envelope.get("decision_authority") != DECISION_AUTHORITY:
        return _rej("ENVELOPE_INVALID_AT_WRITE_BOUNDARY")
    current_eah = _E.compute_execution_authority_hash(envelope)
    if not current_eah or current_eah != envelope.get("execution_authority_hash"):
        return _rej("EXECUTION_AUTHORITY_HASH_DRIFT_AT_WRITE_BOUNDARY")
    child = next((c for c in (envelope.get("children") or [])
                 if c.get("child_execution_id") == child_execution_id), None)
    if child is None:
        return _rej("CHILD_NOT_FOUND_AT_WRITE_BOUNDARY")
    if child.get("execution_status") != _E.PLANNED:
        return _rej("CHILD_NOT_PLANNED_AT_WRITE_BOUNDARY", actual=child.get("execution_status"))
    if child.get("operation_type") != OPERATION_TYPE:
        return _rej("UNSUPPORTED_OPERATION_AT_WRITE_BOUNDARY", op=child.get("operation_type"))
    child_source_sha = child.get("source_content_sha256")
    child_target_pre = child.get("target_pre_sha256")
    if not _is_full_sha256(child_source_sha):
        return _rej("CHILD_SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX")
    if not _is_full_sha256(child_target_pre):
        return _rej("CHILD_TARGET_PRE_SHA256_NOT_FULL_64_HEX")  # C2 V0 = REPLACE only

    approval = _E.load_approval_artifact(approval_id, execution_dir)
    ok_a, r_a = _E.verify_approval_artifact(approval)
    if not ok_a:
        return _rej(f"HUMAN_APPROVAL_ARTIFACT_INVALID:{r_a}")
    ok_v, r_v = _E._validate_approval(
        approval, envelope, derived_authority_context=derived_authority_context)
    if not ok_v or approval.get("execution_authority_hash") != current_eah:
        return _rej(f"HUMAN_APPROVAL_NOT_BOUND:{r_v}")
    _stage4_derived = (approval.get("approved_by") == "HUMAN_MISSION_AUTHORITY_DERIVED")
    if _stage4_derived and derived_authority_context is None:
        return _rej("STAGE4_DERIVED_APPROVAL_WITHOUT_CANONICAL_CONTEXT")
    if (derived_authority_context is not None) and not _stage4_derived:
        return _rej("STAGE4_CONTEXT_WITH_NON_DERIVED_APPROVAL")

    pre = _DS.load_kx108_decision_record(kx108_pre_decision_record_id, kx108_decision_dir)
    ok_p, r_p = _DS.verify_kx108_decision_record(pre)
    if not ok_p:
        return _rej(f"KX108_PRE_DECISION_INVALID:{r_p}")
    if _DS.decision_phase_of(pre) != _DS.PRE_DECISION_PHASE:
        return _rej("KX108_PRE_NOT_PRE_EXECUTION_PHASE")
    if pre.get("x108_gate") != "ALLOW":
        return _rej("KX108_PRE_GATE_NOT_ALLOW", gate=pre.get("x108_gate"))
    if pre.get("execution_authority_hash") != current_eah:
        return _rej("KX108_PRE_EAH_MISMATCH")
    if pre.get("approval_id") != approval_id:
        return _rej("KX108_PRE_APPROVAL_ID_MISMATCH")
    pre_hash = pre["decision_record_hash"]

    pcid = envelope.get("pre_execution_context_id")
    if not pcid:
        return _rej("PRE_EXECUTION_CONTEXT_REQUIRED")
    pctx = _PEC.load_pre_execution_context_record(pcid, pre_execution_context_dir)
    ok_c, r_c = _PEC.verify_pre_execution_context_record(pctx)
    if not ok_c:
        return _rej(f"PRE_EXECUTION_CONTEXT_INVALID:{r_c}")
    if pctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
        return _rej("PRE_EXECUTION_CONTEXT_HASH_MISMATCH")
    if not (pctx.get("worktree_isolated") and pctx.get("branch_isolated")):
        return _rej("PRE_EXECUTION_CONTEXT_ISOLATION_NOT_VERIFIED")
    if pctx.get("protected_scope_status") != "CLEAN":
        return _rej("PRE_EXECUTION_CONTEXT_PROTECTED_SCOPE_NOT_CLEAN")

    # ── 3. Source : confinement + reparse + SHA256 COMPLET, relu MAINTENANT ──
    src_bytes, r_src = _C.resolve_source_bytes(child, root)
    if src_bytes is None:
        return _rej(f"SOURCE_RESOLVE_FAILED:{r_src}")
    if hashlib.sha256(src_bytes).hexdigest() != child_source_sha:
        return _rej("SOURCE_CONTENT_SHA256_MISMATCH")
    # re-lecture ultime immédiatement avant l'écriture (fenêtre preflight->write)
    src_bytes2, r_src2 = _C.resolve_source_bytes(child, root)
    if src_bytes2 is None or src_bytes2 != src_bytes \
            or hashlib.sha256(src_bytes2).hexdigest() != child_source_sha:
        return _rej("SOURCE_CONTENT_DRIFT_BEFORE_WRITE")

    # ── 4. Cible : canonicalisation + protection + reparse + précondition ──
    target_abs, treason = _C.canonicalize_write_target(child.get("target_path"), root)
    if treason == "REFUSED_PROTECTED_TARGET":
        return _rej("PROTECTED_TARGET", target_path=child.get("target_path"))
    if treason or target_abs is None:
        return _rej(f"TARGET_SCOPE_REJECTED:{treason}", target_path=child.get("target_path"))
    target_literal = (root / Path(str(child.get("target_path")).replace("\\", "/")))
    try:
        target_literal.relative_to(root)
    except ValueError:
        return _rej("TARGET_LITERAL_OUTSIDE_REPO")
    if target_literal.exists() and target_literal.is_dir():
        return _rej("TARGET_IS_DIRECTORY")
    ok_rp, r_rp = WG.verify_path_reparse_safe(root, target_literal, kind="TARGET")
    if not ok_rp:
        return _rej(f"TARGET_REPARSE_UNSAFE:{r_rp}")
    cur_before = _sha256_file(target_literal)
    if cur_before != child_target_pre:
        return _rej("TARGET_PRECONDITION_MISMATCH", expected=child_target_pre, actual=cur_before)

    # ── 5. SealedRollbackEvidence — persistée + rechargée + vérifiée AVANT write ──
    preimage = target_literal.read_bytes()
    sre_rec, r_sre = SEV.build_sealed_rollback_evidence(
        batch_execution_id=batch_execution_id, child=child,
        execution_authority_hash=current_eah, approval_id=approval_id,
        kx108_pre_decision_record_id=kx108_pre_decision_record_id,
        kx108_pre_decision_record_hash=pre_hash, preimage_bytes=preimage,
    )
    if sre_rec is None:
        return _rej(f"ROLLBACK_EVIDENCE_SEAL_BUILD_FAILED:{r_sre}")
    sre_store = SEV.store_sealed_rollback_evidence(sre_rec, sealed_rollback_evidence_dir)
    if sre_store.get("status") not in (SEV.STATUS_STORED, SEV.STATUS_IDEMPOTENT):
        return _rej(f"ROLLBACK_EVIDENCE_SEAL_STORE_FAILED:{sre_store.get('status')}")
    sre_reloaded = SEV.load_sealed_rollback_evidence(sre_rec["sealed_rollback_evidence_id"],
                                                    sealed_rollback_evidence_dir)
    ok_sre, r_sre2 = SEV.verify_sealed_rollback_evidence(sre_reloaded)
    if not ok_sre:
        return _rej(f"ROLLBACK_EVIDENCE_SEAL_VERIFY_FAILED:{r_sre2}")
    sre_id = sre_rec["sealed_rollback_evidence_id"]
    sre_hash = sre_rec["sealed_rollback_evidence_hash"]

    # ── 6. MUTATION — double-check pré-état + reparse juste avant, remesure ──
    if derived_authority_context is not None:
        # STAGE 4F REPAIR — section critique LINÉARISÉE : la re-vérif canonique
        # finale de fraîcheur (révocations rechargées) + la mutation physique +
        # la mesure post-écriture s'exécutent sous le MÊME verrou inter-processus
        # (`mission_id`) que `record_mission_authority_revocation`. Aucun autre
        # processus ne peut committer une révocation entre le check et l'écriture.
        try:
            import obsidia_mission_authority_freshness_lock_v0 as _LK
            import obsidia_mission_authority_pre_adapter_v0 as _PADP
        except Exception as exc:  # noqa: BLE001
            return _rej(f"STAGE4_LINEARIZATION_PRIMITIVE_UNAVAILABLE:{exc!r}")
        _mid = (derived_authority_context or {}).get("mission_id")
        _lroot = (derived_authority_context or {}).get("authority_lock_root")
        if not (isinstance(_mid, str) and _mid and isinstance(_lroot, str) and _lroot):
            return _rej("STAGE4_LOCK_CONTEXT_INCOMPLETE")
        write_exc = None
        try:
            with _LK.mission_authority_lock(_mid, lock_root=_lroot):
                ok_fr, why_fr = _PADP.verify_derived_approval_with_context(
                    approval, envelope, derived_authority_context)
                if not ok_fr:
                    return _rej(f"STAGE4_AUTHORITY_STALE_UNDER_LOCK:{why_fr}")
                ok_rp2, r_rp2 = WG.verify_path_reparse_safe(root, target_literal, kind="TARGET")
                if not ok_rp2:
                    return _rej(f"TARGET_REPARSE_UNSAFE_PRE_REPLACE:{r_rp2}")
                if _sha256_file(target_literal) != child_target_pre:
                    return _rej("TARGET_DRIFT_BEFORE_REPLACE")
                try:
                    wres = _C.atomic_replace_with_bytes(target_abs, src_bytes, child_target_pre)
                except Exception as exc:  # noqa: BLE001 — toute défaillance -> remesure
                    write_exc = repr(exc)
                    wres = {"status": "ATOMIC_REPLACE_RAISED", "exc": write_exc}
                measured = _sha256_file(target_literal)
        except _LK.MissionAuthorityLockTimeout as exc:
            return _rej(f"STAGE4_AUTHORITY_LOCK_TIMEOUT:{exc}")
    else:
        ok_rp2, r_rp2 = WG.verify_path_reparse_safe(root, target_literal, kind="TARGET")
        if not ok_rp2:
            return _rej(f"TARGET_REPARSE_UNSAFE_PRE_REPLACE:{r_rp2}")
        if _sha256_file(target_literal) != child_target_pre:
            return _rej("TARGET_DRIFT_BEFORE_REPLACE")

        write_exc = None
        try:
            wres = _C.atomic_replace_with_bytes(target_abs, src_bytes, child_target_pre)
        except Exception as exc:  # noqa: BLE001 — toute défaillance -> remesure
            write_exc = repr(exc)
            wres = {"status": "ATOMIC_REPLACE_RAISED", "exc": write_exc}

        measured = _sha256_file(target_literal)
    ctx_common = {
        "batch_execution_id": batch_execution_id, "child_execution_id": child_execution_id,
        "execution_authority_hash": current_eah, "approval_id": approval_id,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "sealed_rollback_evidence_id": sre_id, "sealed_rollback_evidence_hash": sre_hash,
        "target_path": child.get("target_path"),
    }

    if wres.get("status") != _C.CONTENT_APPLIED:
        # §13 — état re-MESURÉ, jamais supposé
        if measured == child_target_pre:
            return _rej(f"APPLY_FAILED_NO_CONFIRMED_MUTATION:{wres.get('status')}",
                        write_result=wres, write_exception=write_exc, **ctx_common)
        if measured == child_source_sha:
            return _rollback_after_mutation(
                RB, DISP, reason=f"WRITE_ANOMALY_MUTATION_OCCURRED:{wres.get('status')}",
                trigger_code="POST_EVIDENCE_UNAVAILABLE",
                child_execution_id=child_execution_id,
                kx108_pre_decision_record_id=kx108_pre_decision_record_id,
                execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
                post_decision_store_dir=post_decision_store_dir,
                rollback_result_dir=rollback_result_dir, repo_root=root,
                sealed_rollback_evidence_id=sre_id,
                sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
                sealed_receipt_dir=sealed_receipt_dir, ctx_common=ctx_common)
        return _quarantine(f"APPLY_STATE_UNKNOWN:{wres.get('status')}",
                           measured_sha256=measured, write_exception=write_exc, **ctx_common)

    # §14 — mesure post-écriture ; ne jamais faire confiance au seul retour primitive
    if measured != child_source_sha:
        if measured == child_target_pre:
            return _rej("POST_WRITE_MEASUREMENT_STILL_PRE_STATE", **ctx_common)
        return _quarantine("POST_WRITE_MEASUREMENT_UNEXPECTED", measured_sha256=measured, **ctx_common)
    target_b = measured
    bytes_written = wres.get("bytes_written")

    # ── 7. SealedApplyReceipt — persisté + rechargé + vérifié ──
    sar_rec, r_sar = SEV.build_sealed_apply_receipt(
        batch_execution_id=batch_execution_id, child=child,
        execution_authority_hash=current_eah, approval_id=approval_id,
        kx108_pre_decision_record_id=kx108_pre_decision_record_id,
        kx108_pre_decision_record_hash=pre_hash,
        sealed_rollback_evidence_id=sre_id, sealed_rollback_evidence_hash=sre_hash,
        target_pre_sha256=child_target_pre, target_post_sha256=target_b,
        bytes_written=bytes_written,
    )
    sar_ok = sar_rec is not None
    if sar_ok:
        sar_store = SEV.store_sealed_apply_receipt(sar_rec, sealed_receipt_dir)
        sar_ok = sar_store.get("status") in (SEV.STATUS_STORED, SEV.STATUS_IDEMPOTENT)
        if sar_ok:
            sar_re = SEV.load_sealed_apply_receipt(sar_rec["sealed_apply_receipt_id"], sealed_receipt_dir)
            ok_sar_v, _ = SEV.verify_sealed_apply_receipt(sar_re)
            sar_ok = ok_sar_v
    if not sar_ok:
        # §22 — B existe mais le reçu scellé n'a pu être persisté/vérifié.
        return _rollback_after_mutation(
            RB, DISP, reason=f"SEALED_APPLY_RECEIPT_SEAL_FAILED:{r_sar}",
            trigger_code="POST_EVIDENCE_UNAVAILABLE",
            child_execution_id=child_execution_id,
            kx108_pre_decision_record_id=kx108_pre_decision_record_id,
            execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
            post_decision_store_dir=post_decision_store_dir,
            rollback_result_dir=rollback_result_dir, repo_root=root,
            sealed_rollback_evidence_id=sre_id,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            sealed_receipt_dir=sealed_receipt_dir, ctx_common=ctx_common)
    sar_id = sar_rec["sealed_apply_receipt_id"]
    sar_hash = sar_rec["sealed_apply_receipt_hash"]

    # ── 8. TestContractResult — §23 : absence de preuve -> MUST_ROLLBACK ──
    contract = envelope.get("test_contract")
    tcr_id = None
    tcr_hash = None
    try:
        outcome = TC.run_and_persist_test_contract(
            contract, root,
            batch_execution_id=batch_execution_id,
            child_execution_id=child_execution_id,
            execution_authority_hash=current_eah,
            approval_id=approval_id,
            results_dir=test_contract_results_dir,
        )
        if outcome.get("verify_ok") and outcome.get("record"):
            tcr_id = outcome["result_id"]
            tcr_hash = outcome["record"]["result_record_hash"]
    except Exception:  # noqa: BLE001
        tcr_id = None
    if not tcr_id:
        return _rollback_after_mutation(
            RB, DISP, reason="TEST_CONTRACT_RESULT_UNAVAILABLE",
            trigger_code="TEST_INFRA_FAILURE",
            child_execution_id=child_execution_id,
            kx108_pre_decision_record_id=kx108_pre_decision_record_id,
            execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
            post_decision_store_dir=post_decision_store_dir,
            rollback_result_dir=rollback_result_dir, repo_root=root,
            sealed_rollback_evidence_id=sre_id,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            sealed_apply_receipt_id=sar_id, sealed_receipt_dir=sealed_receipt_dir,
            ctx_common=ctx_common)

    # ── 9. Évidence POST liée cryptographiquement au scellé (§17) ──
    tr = ADP.translate_evidence_to_tooling_build_state(
        batch_execution_id, child_execution_id, approval_id, tcr_id,
        execution_dir=execution_dir, selector_dir=selector_dir, ledger_dir=ledger_dir,
        results_dir=test_contract_results_dir, evidence_dir=None, repo_root=root,
        pre_execution_context_dir=pre_execution_context_dir,
        sealed_apply_receipt_id=sar_id, sealed_rollback_evidence_id=sre_id,
        sealed_receipt_dir=sealed_receipt_dir,
        sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
    )
    if tr.get("status") != ADP.READY_FOR_KX108_SUBMISSION:
        return _rollback_after_mutation(
            RB, DISP, reason=f"POST_EVIDENCE_TRANSLATION_FAILED:{tr.get('reason')}",
            trigger_code="POST_EVIDENCE_UNAVAILABLE",
            child_execution_id=child_execution_id,
            kx108_pre_decision_record_id=kx108_pre_decision_record_id,
            execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
            post_decision_store_dir=post_decision_store_dir,
            rollback_result_dir=rollback_result_dir, repo_root=root,
            sealed_rollback_evidence_id=sre_id,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            sealed_apply_receipt_id=sar_id, sealed_receipt_dir=sealed_receipt_dir,
            ctx_common=ctx_common)
    translation_hash = tr["translation_report"]["kx108_input_translation_hash"]

    # ── 10. KX108_POST lié (D1 + lien d'évidence scellée) — kernel 1× ──
    binding_context = {
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": current_eah,
        "approval_id": approval_id,
        "test_contract_hash": envelope.get("test_contract_hash"),
        "test_result_id": tcr_id,
        "test_result_record_hash": tcr_hash,
        "kx108_input_translation_hash": translation_hash,
    }
    post_out = _DS.run_and_persist_kx108_post_execution_decision(
        tr["tooling_build_state_kwargs"], binding_context, kx108_pre_decision_record_id,
        execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
        post_decision_store_dir=post_decision_store_dir,
        sealed_evidence_link={
            "sealed_apply_receipt_id": sar_id, "sealed_apply_receipt_hash": sar_hash,
            "sealed_rollback_evidence_id": sre_id, "sealed_rollback_evidence_hash": sre_hash,
        },
    )
    if post_out.get("status") != "STORED" or not post_out.get("verify_ok"):
        return _rollback_after_mutation(
            RB, DISP, reason=f"KX108_POST_STORE_OR_VERIFY_FAILED:{post_out.get('reason') or post_out.get('verify_reason')}",
            trigger_code="KX108_POST_STORE_FAILURE",
            child_execution_id=child_execution_id,
            kx108_pre_decision_record_id=kx108_pre_decision_record_id,
            execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
            post_decision_store_dir=post_decision_store_dir,
            rollback_result_dir=rollback_result_dir, repo_root=root,
            sealed_rollback_evidence_id=sre_id,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            sealed_apply_receipt_id=sar_id, sealed_receipt_dir=sealed_receipt_dir,
            ctx_common=ctx_common)
    post_id = post_out["decision_record_id"]

    # ── 11. Disposition D1 (recalculée, jamais fournie) ──
    disp = DISP.classify_post_execution_disposition(
        post_decision_record_id=post_id, post_decision_store_dir=post_decision_store_dir,
    )
    common_out = {
        "execution_authority_hash": current_eah,
        "sealed_apply_receipt_id": sar_id, "sealed_apply_receipt_hash": sar_hash,
        "sealed_rollback_evidence_id": sre_id, "sealed_rollback_evidence_hash": sre_hash,
        "kx108_post_decision_record_id": post_id,
        "kx108_post_gate": post_out.get("x108_gate"),
        "kx108_input_translation_hash": translation_hash,
        "test_contract_result_id": tcr_id,
        "target_final_sha256": target_b,
        "authority": AUTHORITY, "decision_authority": DECISION_AUTHORITY,
    }
    if disp.get("disposition") == DISP.KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW \
            and post_out.get("x108_gate") == "ALLOW":
        return {"status": GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW,
                "reason": "KX108_POST_GATE_ALLOW", "target_mutated": True,
                "commit_review_eligible": True, "rollback_required": False, **common_out}

    # MUST_ROLLBACK (POST HOLD/BLOCK ou signal) -> D2
    return _rollback_after_mutation(
        RB, DISP, reason=f"KX108_POST_DISPOSITION_{disp.get('disposition')}_GATE_{post_out.get('x108_gate')}",
        post_decision_record_id=post_id,
        child_execution_id=child_execution_id,
        kx108_pre_decision_record_id=kx108_pre_decision_record_id,
        execution_dir=execution_dir, pre_decision_store_dir=kx108_decision_dir,
        post_decision_store_dir=post_decision_store_dir,
        rollback_result_dir=rollback_result_dir, repo_root=root,
        sealed_rollback_evidence_id=sre_id,
        sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
        sealed_apply_receipt_id=sar_id, sealed_receipt_dir=sealed_receipt_dir,
        ctx_common={**ctx_common, **common_out})


def _rollback_after_mutation(RB, DISP, *, reason, child_execution_id,
                             kx108_pre_decision_record_id, execution_dir,
                             pre_decision_store_dir, post_decision_store_dir,
                             rollback_result_dir, repo_root,
                             sealed_rollback_evidence_id, sealed_rollback_evidence_dir,
                             sealed_receipt_dir, ctx_common,
                             trigger_code=None, post_decision_record_id=None,
                             sealed_apply_receipt_id=None) -> dict:
    """Invoque D2 (jamais KX108) et projette le résultat vers une issue
    publique C2. B attendu par D2 = autorité EAH-liée child.source_content_sha256."""
    kw = dict(
        child_execution_id=child_execution_id,
        kx108_pre_decision_record_id=kx108_pre_decision_record_id,
        execution_dir=execution_dir, pre_decision_store_dir=pre_decision_store_dir,
        post_decision_store_dir=post_decision_store_dir,
        rollback_result_dir=rollback_result_dir, repo_root=repo_root,
        sealed_rollback_evidence_id=sealed_rollback_evidence_id,
        sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
        sealed_apply_receipt_id=sealed_apply_receipt_id,
        sealed_receipt_dir=sealed_receipt_dir,
    )
    if post_decision_record_id is not None:
        kw["kx108_post_decision_record_id"] = post_decision_record_id
    else:
        kw["rollback_trigger_code"] = trigger_code
    rb = RB.run_governed_rollback(**kw)
    st = rb.get("status")
    ok = st in (RB.ROLLBACK_SUCCEEDED, RB.ALREADY_ROLLED_BACK,
                RB.ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED)
    public = (GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK if ok
              else GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE)
    return {
        "status": public,
        "reason": reason,
        "target_mutated": True,
        "rollback_status": st,
        "rollback_result_id": rb.get("rollback_result_id"),
        "rollback_expected_b_authority": rb.get("rollback_expected_b_authority"),
        "expected_post_sha256": rb.get("expected_post_sha256"),
        "quarantine_required": rb.get("quarantine_required"),
        "kx108_invocations_during_rollback": rb.get("kx108_invocations_during_rollback", 0),
        "commit_review_eligible": False,
        "rollback_required": not ok,
        **{k: v for k, v in ctx_common.items() if k not in ("status", "reason")},
    }
