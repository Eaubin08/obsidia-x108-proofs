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
    ok_v, reason_v = _E._validate_approval(approval, envelope)
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
