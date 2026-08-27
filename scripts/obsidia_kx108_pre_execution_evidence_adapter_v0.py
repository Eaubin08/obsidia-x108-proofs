"""
obsidia_kx108_pre_execution_evidence_adapter_v0.py
==================================================
TWO_PHASE_KX108_PRE_EXECUTION_CHECKPOINT_A1_V0 — adaptateur d'évidence
PRÉ-EXÉCUTION pour le kernel souverain KX108, ordre canonique gelé :

    ExecutionEnvelope → HumanApproval (déjà validée) → KX108_PRE → Guarded Apply

HumanApproval N'EST PAS decision_authority et n'autorise JAMAIS seule une
mutation de cible. KX108_PRE reste le veto souverain final avant mutation.

Cet adaptateur transforme :

    ExecutionEnvelope (integrity_verified)
    + PreExecutionContext canonique vérifié
    + HumanApproval canonique chargée / vérifiée / validée contre l'enveloppe
    + child.source_content_sha256 (lié transitivement dans execution_authority_hash)

    → un `pre_tooling_build_state_kwargs` pour sigma.contracts.ToolingBuildState

soumissible au MÊME kernel souverain (sigma.protocols.run_tooling_build_pipeline)
AVANT toute mutation de cible. C'est l'ÉVIDENCE qui change de phase, pas le
moteur de décision.

`human_approval_status = "APPROVED"` n'est posé QU'APRÈS validation canonique
de l'artefact d'approbation stocké (jamais une chaîne arbitraire fournie par
l'appelant). L'appelant ne fournit qu'un `approval_id`.

READ_ONLY vis-à-vis de l'état cible. Ne charge JAMAIS : apply receipt /
CONTENT_APPLIED / TestContractResult / target_post_sha256 / `git diff`
post-apply. Ne crée AUCUNE approbation, n'applique RIEN, ne mute AUCUNE cible.
Échoue fermé (status = NOT_READY_PRE_EVIDENCE_INTEGRITY) sur toute divergence —
aucun chemin ALLOW dégradé.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_batch_execution as _E          # load/verify/validate approval — jamais modifié ici
import obsidia_pre_execution_context as _PEC  # load/verify pre-execution context — jamais modifié ici
import obsidia_test_contract as _TC           # compute_test_contract_hash uniquement

DECISION_AUTHORITY = "KX108_ONLY"
EVIDENCE_SCHEMA_TAG = "KX108_PRE_EVIDENCE_V1"

STATUS_READY = "READY_FOR_KX108_PRE_SUBMISSION"
STATUS_NOT_READY = "NOT_READY_PRE_EVIDENCE_INTEGRITY"

_SHA256_HEX_LEN = 64


def _not_ready(reason: str, **extra) -> dict:
    return {
        "status": STATUS_NOT_READY,
        "reason": reason,
        "pre_tooling_build_state_kwargs": None,
        "pre_binding_context": None,
        "kx108_input_translation_hash": None,
        "translation_report": None,
        **extra,
    }


def _is_full_sha256(value) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256_HEX_LEN
        and all(c in "0123456789abcdef" for c in value.lower())
    )


def compute_pre_kx108_input_translation_hash(authority_payload: dict) -> str:
    """SHA256 COMPLET (64 hex) d'une sérialisation canonique et DÉTERMINISTE
    du paquet d'évidence PRE. Aucun horodatage n'entre dans ce hash : la
    même évidence pré-action (mêmes identités, même approbation liée)
    produit exactement le même hash ; toute entrée pertinente pour
    l'autorité qui change → hash différent."""
    payload = json.dumps(authority_payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def translate_pre_execution_evidence_to_tooling_build_state(
    batch_execution_id: str,
    child_execution_id: str,
    approval_id: str,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    Retourne :
      {
        "status": STATUS_READY | STATUS_NOT_READY,
        "reason": <str si NOT_READY>,
        "pre_tooling_build_state_kwargs": {...} | None,
        "pre_binding_context": {...} | None,   # cf. obsidia_kx108_decision_store._PRE_BINDING_CONTEXT_FIELDS
        "kx108_input_translation_hash": <64 hex> | None,
        "translation_report": {...} | None,
      }

    Aucune mutation, aucune écriture, aucune lecture d'évidence post-apply.
    """
    # 1. Enveloppe d'exécution -------------------------------------------------
    envelope = _E._load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return _not_ready("ENVELOPE_NOT_FOUND")
    if not isinstance(envelope, dict):
        return _not_ready("ENVELOPE_MALFORMED")
    if not envelope.get("integrity_verified"):
        return _not_ready("ENVELOPE_INTEGRITY_NOT_VERIFIED")
    if envelope.get("decision_authority") != DECISION_AUTHORITY:
        return _not_ready("ENVELOPE_DECISION_AUTHORITY_NOT_KX108_ONLY")

    # 2. execution_authority_hash recalculé == stocké ----------------------
    stored_eah = envelope.get("execution_authority_hash")
    recomputed_eah = _E.compute_execution_authority_hash(envelope)
    if not stored_eah or recomputed_eah != stored_eah:
        return _not_ready("EXECUTION_AUTHORITY_HASH_DRIFT",
                          expected=stored_eah, recomputed=recomputed_eah)

    # 3. Child exact -----------------------------------------------------
    child = next(
        (c for c in (envelope.get("children") or [])
         if c.get("child_execution_id") == child_execution_id),
        None,
    )
    if child is None:
        return _not_ready("CHILD_NOT_FOUND")

    target_path = child.get("target_path")
    if not isinstance(target_path, str) or not target_path.strip():
        return _not_ready("CHILD_TARGET_PATH_MISSING")
    target_path = target_path.strip()

    source_content_sha256 = child.get("source_content_sha256")
    if not _is_full_sha256(source_content_sha256):
        return _not_ready("SOURCE_CONTENT_SHA256_ABSENT_OR_MALFORMED")

    target_pre_sha256 = child.get("target_pre_sha256")
    if target_pre_sha256 is None or (isinstance(target_pre_sha256, str) and not target_pre_sha256):
        return _not_ready("TARGET_PRE_SHA256_ABSENT")

    operation_type = child.get("operation_type") or ""

    # 4. Cible protégée (recalculée maintenant) -------------------------
    if _E._is_protected(target_path):
        return _not_ready("PROTECTED_TARGET")

    # 5. PreExecutionContext canonique vérifié — REQUIS (aucun chemin legacy)
    pre_ctx_id = envelope.get("pre_execution_context_id")
    if not pre_ctx_id:
        return _not_ready("PRE_EXECUTION_CONTEXT_REQUIRED")
    pre_ctx = _PEC.load_pre_execution_context_record(pre_ctx_id, pre_execution_context_dir)
    ok_ctx, reason_ctx = _PEC.verify_pre_execution_context_record(pre_ctx)
    if not ok_ctx:
        return _not_ready(f"PRE_EXECUTION_CONTEXT_INVALID:{reason_ctx}")
    if pre_ctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
        return _not_ready("PRE_EXECUTION_CONTEXT_HASH_MISMATCH")
    if pre_ctx.get("decision_authority") != DECISION_AUTHORITY:
        return _not_ready("PRE_EXECUTION_CONTEXT_DECISION_AUTHORITY_NOT_KX108_ONLY")

    # 6. Isolation vérifiée (valeurs LUES du contexte canonique) -------
    if not (pre_ctx.get("worktree_isolated") and pre_ctx.get("branch_isolated")):
        return _not_ready("ISOLATION_NOT_VERIFIED")
    if pre_ctx.get("protected_scope_status") != "CLEAN":
        return _not_ready("PRE_EXECUTION_CONTEXT_PROTECTED_SCOPE_NOT_CLEAN")

    base_sha = pre_ctx.get("base_sha")
    manifest_hash = pre_ctx.get("manifest_sha256")
    if not base_sha:
        return _not_ready("BASE_SHA_ABSENT_IN_PRE_EXECUTION_CONTEXT")
    if not manifest_hash:
        return _not_ready("MANIFEST_SHA256_ABSENT_IN_PRE_EXECUTION_CONTEXT")

    # 7. Contrat de test immuable, lié dans execution_authority_hash ---
    contract = envelope.get("test_contract")
    test_contract_hash = envelope.get("test_contract_hash")
    if not contract or not test_contract_hash:
        return _not_ready("TEST_CONTRACT_ABSENT")
    if _TC.compute_test_contract_hash(contract) != test_contract_hash:
        return _not_ready("TEST_CONTRACT_HASH_MISMATCH")

    # 8. Cohérence cible enveloppe <-> contexte pré-exécution ---------
    if pre_ctx.get("target_path") != target_path:
        return _not_ready("TARGET_PATH_MISMATCH_ENVELOPE_VS_CONTEXT")
    if pre_ctx.get("target_pre_sha256") != target_pre_sha256:
        return _not_ready("TARGET_PRE_SHA256_MISMATCH_ENVELOPE_VS_CONTEXT")

    # 9. HumanApproval canonique — CHARGÉE / VÉRIFIÉE / VALIDÉE contre l'enveloppe
    #    (jamais un dict fourni par l'appelant ; l'appelant ne fournit qu'un id)
    if not isinstance(approval_id, str) or not approval_id.strip():
        return _not_ready("APPROVAL_ID_ABSENT")
    approval_id = approval_id.strip()
    approval = _E.load_approval_artifact(approval_id, execution_dir)
    if approval is None:
        return _not_ready("HUMAN_APPROVAL_NOT_FOUND")
    ok_a, reason_a = _E.verify_approval_artifact(approval)
    if not ok_a:
        return _not_ready(f"HUMAN_APPROVAL_ARTIFACT_INVALID:{reason_a}")
    ok_v, reason_v = _E._validate_approval(approval, envelope)
    if not ok_v:
        return _not_ready(f"HUMAN_APPROVAL_NOT_BOUND_TO_EXECUTION:{reason_v}")
    # défense en profondeur : lie explicitement à l'EAH RECALCULÉ (étape 2)
    if approval.get("execution_authority_hash") != recomputed_eah:
        return _not_ready("HUMAN_APPROVAL_EXECUTION_AUTHORITY_HASH_MISMATCH")

    human_approval_record_hash = approval.get("approval_record_hash")

    # 10. ToolingBuildState PRÉ-ACTION — human_approval_status="APPROVED"
    #     dérivé d'une approbation stockée vérifiée, jamais fabriqué.
    pre_tooling_build_state_kwargs = {
        "session_id": child_execution_id,
        "objective": child.get("operation_reason") or f"pre-execution gate: {target_path}",
        "base_sha": base_sha,
        "manifest_hash": manifest_hash,
        "diff_hash": "",
        "approved_scope": [target_path],
        "actual_touched_files": [],
        "new_files": [],
        "deleted_files": [],
        "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED",   # dérivé de l'approbation canonique validée
        "obsidure_status": "UNKNOWN",
        "worktree_isolated": True,
        "branch_isolated": True,
        "auto_commit_disabled": True,
        "auto_push_disabled": True,
        "auto_merge_disabled": True,
        "tests_results": "UNKNOWN",            # aucun test avant l'apply
        "gates_results": "UNKNOWN",
        "first_failure": "",
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
        "decision_authority": DECISION_AUTHORITY,
    }

    # 11. Hash de traduction déterministe (aucun horodatage) ---------
    authority_payload = {
        "schema": EVIDENCE_SCHEMA_TAG,
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": recomputed_eah,
        "approval_id": approval_id,
        "human_approval_record_hash": human_approval_record_hash,
        "pre_execution_context_id": pre_ctx_id,
        "pre_execution_context_record_hash": envelope.get("pre_execution_context_record_hash"),
        "test_contract_hash": test_contract_hash,
        "target_path": target_path,
        "target_pre_sha256": target_pre_sha256,
        "source_content_sha256": source_content_sha256,
        "operation_type": operation_type,
        "approved_scope": [target_path],
        "base_sha": base_sha,
        "manifest_hash": manifest_hash,
        "pre_tooling_build_state_kwargs": pre_tooling_build_state_kwargs,
    }
    kx108_input_translation_hash = compute_pre_kx108_input_translation_hash(authority_payload)

    pre_binding_context = {
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": recomputed_eah,
        "approval_id": approval_id,
        "pre_execution_context_id": pre_ctx_id,
        "pre_execution_context_record_hash": envelope.get("pre_execution_context_record_hash"),
        "test_contract_hash": test_contract_hash,
        "kx108_input_translation_hash": kx108_input_translation_hash,
    }

    return {
        "status": STATUS_READY,
        "reason": None,
        "pre_tooling_build_state_kwargs": pre_tooling_build_state_kwargs,
        "pre_binding_context": pre_binding_context,
        "kx108_input_translation_hash": kx108_input_translation_hash,
        "translation_report": {
            "schema": EVIDENCE_SCHEMA_TAG,
            "target_path": target_path,
            "operation_type": operation_type,
            "source_content_sha256": source_content_sha256,
            "target_pre_sha256": target_pre_sha256,
            "execution_authority_hash": recomputed_eah,
            "approval_id": approval_id,
            "human_approval_status": "APPROVED",
            "human_approval_bound_to_current_execution": True,
            "human_approval_record_hash": human_approval_record_hash,
            "pre_execution_context_id": pre_ctx_id,
            "isolation_verified": True,
            "base_sha": base_sha,
            "manifest_hash": manifest_hash,
            "post_action_fields_present": [],   # preuve : aucun champ post-apply
        },
    }
