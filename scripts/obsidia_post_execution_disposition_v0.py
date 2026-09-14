"""
obsidia_post_execution_disposition_v0.py
========================================
KX108_POST_PRE_BINDING_D1_V0 — classificateur de disposition post-exécution,
STRICTEMENT READ_ONLY et NON_SOVEREIGN.

`classify_post_execution_disposition(...)` ne fait qu'énoncer ce qui DOIT
se produire ensuite après une exécution bornée gouvernée :

    KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW   (x108_gate POST == ALLOW)
    MUST_ROLLBACK                            (x108_gate POST ∈ {HOLD, BLOCK}
                                             OU tout signal d'échec canonique)

Il N'EXÉCUTE AUCUN rollback, AUCUNE écriture (write_capability = false),
AUCUNE closure, AUCUNE mutation. Seul x108_gate est souverain ;
READY_FOR_COMMIT_REVIEW / ACT / market_verdict ne sont jamais traités
comme autorité. "KEEP_ELIGIBLE..." ne déclenche JAMAIS git add/commit/
push/merge/PR — cela signifie seulement : éligible à une revue Git
humaine ultérieure.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_kx108_decision_store as _DS

AUTHORITY = "NON_SOVEREIGN"

DISPOSITION_CLASSIFIED = "DISPOSITION_CLASSIFIED"
DISPOSITION_HOLD = "DISPOSITION_HOLD"  # erreur d'entrée — jamais une disposition

KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW = "KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW"
MUST_ROLLBACK = "MUST_ROLLBACK"

# Signaux d'échec canoniques : dans le futur flux C2+D, une cible a déjà
# été appliquée et aucune décision KX108_POST souveraine de conservation
# n'est disponible -> rollback obligatoire.
CANONICAL_FAILURE_SIGNALS = frozenset({
    "POST_EVIDENCE_UNAVAILABLE",
    "TEST_INFRA_FAILURE",
    "KX108_POST_INVOCATION_FAILURE",
    "KX108_POST_STORE_FAILURE",
    "KX108_POST_RECORD_INVALID",
})


def _hold(reason: str, **extra) -> dict:
    return {
        "status": DISPOSITION_HOLD,
        "reason": reason,
        "authority": AUTHORITY,
        "write_capability": False,
        **extra,
    }


def _classified(disposition: str, reason: str, *, commit_review_eligible: bool,
                rollback_required: bool, post_decision_record_id: Optional[str] = None,
                kx108_post_gate: Optional[str] = None,
                execution_authority_hash: Optional[str] = None,
                kx108_pre_decision_record_id: Optional[str] = None) -> dict:
    return {
        "status": DISPOSITION_CLASSIFIED,
        "disposition": disposition,
        "reason": reason,
        "post_decision_record_id": post_decision_record_id,
        "kx108_post_gate": kx108_post_gate,
        "execution_authority_hash": execution_authority_hash,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "authority": AUTHORITY,
        "write_capability": False,
        "commit_review_eligible": commit_review_eligible,
        "rollback_required": rollback_required,
    }


def classify_post_execution_disposition(
    post_decision_record_id: Optional[str] = None,
    failure_signal: Optional[str] = None,
    post_decision_store_dir: Optional[Path] = None,
) -> dict:
    """
    EXACTEMENT UN des deux : soit `post_decision_record_id` (une décision
    KX108_POST persistée), soit `failure_signal` (un signal d'échec
    canonique dans CANONICAL_FAILURE_SIGNALS).

    Aucun texte libre d'appelant n'est traité comme autorité.
    Aucune mutation, aucune écriture.
    """
    has_id = bool(post_decision_record_id and str(post_decision_record_id).strip())
    has_sig = bool(failure_signal and str(failure_signal).strip())
    if has_id == has_sig:
        return _hold("EXACTLY_ONE_OF_post_decision_record_id_OR_failure_signal_REQUIRED")

    # --- Signal d'échec canonique -> MUST_ROLLBACK ---
    if has_sig:
        sig = str(failure_signal).strip()
        if sig not in CANONICAL_FAILURE_SIGNALS:
            return _hold(f"UNKNOWN_FAILURE_SIGNAL:{sig}")
        return _classified(
            MUST_ROLLBACK, f"CANONICAL_FAILURE_SIGNAL:{sig}",
            commit_review_eligible=False, rollback_required=True,
        )

    # --- Décision KX108_POST persistée ---
    rec_id = str(post_decision_record_id).strip()
    rec = _DS.load_kx108_decision_record(rec_id, post_decision_store_dir)
    if rec is None:
        return _classified(
            MUST_ROLLBACK, "KX108_POST_RECORD_NOT_FOUND",
            commit_review_eligible=False, rollback_required=True,
            post_decision_record_id=rec_id,
        )
    ok, reason = _DS.verify_kx108_decision_record(rec)
    if not ok:
        return _classified(
            MUST_ROLLBACK, f"KX108_POST_RECORD_INVALID:{reason}",
            commit_review_eligible=False, rollback_required=True,
            post_decision_record_id=rec_id,
        )
    if _DS.decision_phase_of(rec) != _DS.POST_DECISION_PHASE:
        return _hold(f"NOT_A_POST_EXECUTION_RECORD:{_DS.decision_phase_of(rec)}",
                     post_decision_record_id=rec_id)
    if not (rec.get("kx108_pre_decision_record_id") and rec.get("kx108_pre_decision_record_hash")):
        return _hold("POST_RECORD_NOT_LINKED_TO_PRE_DECISION", post_decision_record_id=rec_id)

    gate = rec.get("x108_gate")
    common = dict(
        post_decision_record_id=rec_id,
        kx108_post_gate=gate,
        execution_authority_hash=rec.get("execution_authority_hash"),
        kx108_pre_decision_record_id=rec.get("kx108_pre_decision_record_id"),
    )
    if gate == "ALLOW":
        return _classified(
            KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, "KX108_POST_GATE_ALLOW",
            commit_review_eligible=True, rollback_required=False, **common,
        )
    if gate in ("HOLD", "BLOCK"):
        return _classified(
            MUST_ROLLBACK, f"KX108_POST_GATE_{gate}",
            commit_review_eligible=False, rollback_required=True, **common,
        )
    return _hold(f"UNEXPECTED_X108_GATE:{gate}", post_decision_record_id=rec_id)
