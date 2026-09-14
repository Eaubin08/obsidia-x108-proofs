"""
obsidia_execution_closure.py
=================================
CLOSE_REAL_ACD01_BLOCKED_PILOT_V0 — persistance canonique, immuable,
append-only, hors dépôt, d'un ClosureRecord figeant le résultat final
d'une exécution bornée (functional_status / governance_status /
pilot_status / final_disposition) AVANT toute autorisation de rollback.

Ce module ne DÉCIDE rien : il ne fait que sérialiser sans perte le
résultat déjà rendu (KX108 DecisionRecord canonique) et le lier aux
identités d'évidence pré-KX108 déjà établies. decision_authority reste
KX108_ONLY.

Un ClosureRecord ne réinvoque jamais KX108, n'exécute jamais de
rollback, et ne stage/commit jamais rien dans le dépôt. Un rollback
ultérieur produit un artefact append-only séparé — l'artefact de
clôture d'origine n'est jamais réécrit.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT_EXISTING_IDENTICAL = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_CLOSURE_ID = "INVALID_CLOSURE_ID"

EXECUTION_CLOSURE_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "execution_closures"

_CLOSURE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

_CLOSURE_BOUND_FIELDS = (
    "closure_schema_version", "closure_id", "created_at",
    "batch_execution_id", "child_execution_id",
    "execution_authority_hash", "approval_id",
    "test_contract_hash", "test_result_id", "test_result_record_hash",
    "kx108_input_translation_hash",
    "kx108_decision_record_id", "kx108_decision_record_hash",
    "target_path",
    "target_pre_apply_sha256", "target_post_apply_sha256",
    "functional_status", "governance_status", "pilot_status",
    "kx108_gate", "kx108_reason_code",
    "final_disposition", "rollback_status",
    "decision_authority",
)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def compute_execution_closure_hash(record: dict) -> str:
    """
    SHA256 COMPLET (64 hex). Sérialisation canonique (sort_keys). Exclut
    uniquement closure_record_hash lui-même — toute mutation d'une
    identité de décision, d'une identité de résultat, d'un hash de
    cible, du pilot_status ou de la disposition change ce hash.
    """
    payload = json.dumps(
        {k: record.get(k) for k in _CLOSURE_BOUND_FIELDS},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _closure_path(closure_id: "str | None", store_dir: Optional[Path] = None) -> Path:
    """Validation purement lexicale (jamais .resolve()) — même modèle que les stores frères."""
    if not closure_id or not _CLOSURE_ID_RE.match(closure_id):
        raise ValueError("INVALID_CLOSURE_ID")
    d = store_dir or EXECUTION_CLOSURE_DIR
    return d / f"{closure_id}.json"


def store_execution_closure_record(record: dict, store_dir: Optional[Path] = None) -> dict:
    """
    Publication STRICTE, append-only, ATOMIQUE — même modèle que
    store_kx108_decision_record : fichier temporaire complet puis
    publication via os.link (échoue si la cible existe déjà), jamais de
    fichier partiel visible.
    """
    closure_id = record.get("closure_id")
    try:
        p = _closure_path(closure_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_CLOSURE_ID, "closure_id": closure_id}

    payload = json.dumps(record, ensure_ascii=False, indent=2)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = f".{p.name}.{os.getpid()}.{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    tmp = p.parent / tmp_name
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, "closure_id": closure_id}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": STATUS_IDEMPOTENT_EXISTING_IDENTICAL, "closure_id": closure_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, "closure_id": closure_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_execution_closure_record(closure_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    """Charge un ClosureRecord stocké — jamais reconstruit à la volée."""
    try:
        p = _closure_path(closure_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_execution_closure_record(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    """
    Intégrité STRUCTURELLE : schéma supporté, champs liés présents,
    hash stocké == recalculé, decision_authority == KX108_ONLY.
    """
    if record is None:
        return False, "CLOSURE_RECORD_MISSING"
    if record.get("closure_schema_version") != SCHEMA_VERSION:
        return False, "CLOSURE_RECORD_SCHEMA_UNSUPPORTED"
    for f in _CLOSURE_BOUND_FIELDS:
        if f not in record:
            return False, f"CLOSURE_RECORD_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    expected_hash = compute_execution_closure_hash(record)
    if record.get("closure_record_hash") != expected_hash:
        return False, "CLOSURE_RECORD_HASH_MISMATCH"
    return True, None


def create_execution_closure_record(
    kx108_decision_record: dict,
    binding_context: dict,
    target_path: str,
    target_pre_apply_sha256: str,
    target_post_apply_sha256: str,
    final_disposition: str,
    rollback_status: str,
    store_dir: Optional[Path] = None,
) -> dict:
    """
    Chemin de production UNIQUE gelant le résultat final d'une exécution
    bornée déjà décidée par KX108 :

      1. lit le CanonicalDecisionEnvelope déjà persisté (kx108_decision_record)
      2. dérive functional_status/governance_status/pilot_status du gate réel
      3. lie aux identités d'évidence exactes (binding_context)
      4. calcule le hash de clôture
      5. publie atomiquement
      6. recharge
      7. vérifie
      8. retourne la référence à l'enregistrement persisté

    N'invoque JAMAIS KX108, n'exécute JAMAIS de rollback, ne
    stage/commit JAMAIS rien dans le dépôt.
    """
    gate = kx108_decision_record.get("x108_gate")
    functional_status = "PASS"
    governance_status = gate
    pilot_status = f"FUNCTIONAL_{functional_status}_GOVERNANCE_{governance_status}"

    created_at = _now()
    record: dict = {
        "closure_schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        **{k: binding_context[k] for k in (
            "batch_execution_id", "child_execution_id",
            "execution_authority_hash", "approval_id",
            "test_contract_hash", "test_result_id", "test_result_record_hash",
            "kx108_input_translation_hash",
        )},
        "kx108_decision_record_id": kx108_decision_record.get("decision_record_id"),
        "kx108_decision_record_hash": kx108_decision_record.get("decision_record_hash"),
        "target_path": target_path,
        "target_pre_apply_sha256": target_pre_apply_sha256,
        "target_post_apply_sha256": target_post_apply_sha256,
        "functional_status": functional_status,
        "governance_status": governance_status,
        "pilot_status": pilot_status,
        "kx108_gate": gate,
        "kx108_reason_code": kx108_decision_record.get("reason_code"),
        "final_disposition": final_disposition,
        "rollback_status": rollback_status,
        "decision_authority": DECISION_AUTHORITY,
    }

    record["closure_id"] = f"clo-{kx108_decision_record.get('decision_record_id', '').removeprefix('kxd-')}"
    record["closure_record_hash"] = compute_execution_closure_hash(record)

    store_result = store_execution_closure_record(record, store_dir)
    reloaded = load_execution_closure_record(record["closure_id"], store_dir)
    verify_ok, verify_reason = verify_execution_closure_record(reloaded)

    return {
        "closure_id": record["closure_id"],
        "store_result": store_result,
        "record": reloaded,
        "verify_ok": verify_ok,
        "verify_reason": verify_reason,
    }
