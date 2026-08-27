"""
obsidia_kx108_decision_store.py
=================================
CLOSE_KX108_DECISION_PERSISTENCE_GAP_V0 — persistance canonique,
immuable, append-only, hors dépôt, d'un CanonicalDecisionEnvelope réel
produit par sigma/protocols.py::run_tooling_build_pipeline.

Ce module ne DÉCIDE rien : il ne fait que sérialiser sans perte,
lier aux identités d'évidence pré-KX108, et publier atomiquement une
décision KX108 déjà rendue. decision_authority reste KX108_ONLY —
GuardX108.decide() est la seule source du champ souverain x108_gate.

Distinction préservée explicitement :
  - x108_gate               -> résultat SOUVERAIN (GuardX108.decide)
  - raw_engine.consensus.*  -> surface non-souveraine ("aggregate4"),
                                authority=PROOF_SURFACE_ONLY, ne
                                remplace jamais x108_gate.

Le primitif de production run_and_persist_kx108_decision() invoque
run_tooling_build_pipeline EXACTEMENT UNE FOIS par appel et ne
persiste jamais une décision fournie par l'appelant.
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

VALID_X108_GATES = ("ALLOW", "HOLD", "BLOCK")

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT_EXISTING_IDENTICAL = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_DECISION_RECORD_ID = "INVALID_DECISION_RECORD_ID"

KX108_DECISION_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "kx108_decisions"

_DECISION_RECORD_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

_BINDING_CONTEXT_FIELDS = (
    "batch_execution_id", "child_execution_id", "execution_authority_hash",
    "approval_id", "test_contract_hash", "test_result_id",
    "test_result_record_hash", "kx108_input_translation_hash",
)

_RECORD_BOUND_FIELDS = (
    "decision_record_schema_version", "decision_record_id", "created_at",
    "batch_execution_id", "child_execution_id", "execution_authority_hash",
    "approval_id", "test_contract_hash", "test_result_id",
    "test_result_record_hash", "kx108_input_translation_hash",
    "decision_id", "trace_id", "domain",
    "x108_gate", "reason_code", "severity", "market_verdict",
    "contradictions", "unknowns", "risk_flags",
    "decision_authority", "canonical_envelope",
)

_IDENTITY_SEED_FIELDS = _BINDING_CONTEXT_FIELDS + ("canonical_envelope",)

# ── TWO_PHASE_KX108_PRE_EXECUTION_CHECKPOINT_A_V0 — support additif de phase ──
#
# decision_phase distingue une décision KX108 rendue AVANT toute mutation
# de cible (PRE_EXECUTION, évidence purement pré-action) d'une décision
# rendue APRÈS mutation + tests (POST_EXECUTION, chemin historique).
#
# Rétro-compatibilité STRICTE : un enregistrement historique n'a pas de
# clé "decision_phase" ; compute_kx108_decision_record_hash et
# verify_kx108_decision_record retombent alors EXACTEMENT sur le jeu de
# champs POST d'origine (_RECORD_BOUND_FIELDS) — hash et vérification
# byte-identiques à avant ce changement. Aucun record existant n'est lu,
# migré ni réécrit. run_and_persist_kx108_decision (POST) est INCHANGÉE.
#
# Ordre canonique gelé : ExecutionEnvelope -> HumanApproval -> KX108_PRE
# -> Guarded Apply. Une décision PRE_EXECUTION est donc rendue APRÈS une
# HumanApproval déjà validée : elle PORTE approval_id (l'artefact
# d'approbation est chargé + vérifié + validé contre l'enveloppe par
# l'adaptateur canonique AVANT soumission au kernel). Elle ne porte
# JAMAIS test_result_id / test_result_record_hash (ces preuves post-apply
# n'existent pas encore). Jeu de liaison dédié (_PRE_BINDING_CONTEXT_
# FIELDS) + validateur dédié (_validate_pre_binding_context).
PRE_DECISION_PHASE = "PRE_EXECUTION"
POST_DECISION_PHASE = "POST_EXECUTION"

_PRE_BINDING_CONTEXT_FIELDS = (
    "batch_execution_id", "child_execution_id", "execution_authority_hash",
    "approval_id",
    "pre_execution_context_id", "pre_execution_context_record_hash",
    "test_contract_hash", "kx108_input_translation_hash",
)

_PRE_RECORD_BOUND_FIELDS = (
    "decision_record_schema_version", "decision_record_id", "created_at",
    "decision_phase",
    "batch_execution_id", "child_execution_id", "execution_authority_hash",
    "approval_id",
    "pre_execution_context_id", "pre_execution_context_record_hash",
    "test_contract_hash", "kx108_input_translation_hash",
    "decision_id", "trace_id", "domain",
    "x108_gate", "reason_code", "severity", "market_verdict",
    "contradictions", "unknowns", "risk_flags",
    "decision_authority", "canonical_envelope",
)

_PRE_IDENTITY_SEED_FIELDS = _PRE_BINDING_CONTEXT_FIELDS + ("decision_phase", "canonical_envelope")


def decision_phase_of(record: "Optional[dict]") -> str:
    """Phase d'un enregistrement de décision KX108.

    Clé absente (schéma historique) => POST_EXECUTION. Ne lève jamais.
    """
    if not record:
        return POST_DECISION_PHASE
    return record.get("decision_phase") or POST_DECISION_PHASE


def _record_bound_fields_for(record: dict) -> tuple:
    """PRE => _PRE_RECORD_BOUND_FIELDS ; sinon (absent / POST) => jeu POST d'origine."""
    if record.get("decision_phase") == PRE_DECISION_PHASE:
        return _PRE_RECORD_BOUND_FIELDS
    return _RECORD_BOUND_FIELDS


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def compute_kx108_decision_record_hash(record: dict) -> str:
    """
    SHA256 COMPLET (64 hex). Sérialisation canonique (sort_keys). Exclut
    uniquement decision_record_hash lui-même — toute mutation d'une
    autorité liée, d'une identité d'évidence, ou d'un seul champ de
    l'enveloppe canonique change ce hash.
    """
    payload = json.dumps(
        {k: record.get(k) for k in _record_bound_fields_for(record)},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compute_decision_record_identity(seed: dict) -> str:
    """
    Identité CONTENU, pas un UUID aléatoire — une tentative
    d'évaluation réellement identique (même contexte de liaison, même
    enveloppe canonique) republie de façon idempotente ; une tentative
    différente (même un second run réel sur le même child) produit une
    identité distincte et COEXISTE, sans jamais écraser la précédente
    (APPEND_ONLY, cf. mandat §5).
    """
    payload = json.dumps(
        {k: seed.get(k) for k in _IDENTITY_SEED_FIELDS},
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"kxd-{digest[:32]}"


def _decision_record_path(decision_record_id: "str | None", store_dir: Optional[Path] = None) -> Path:
    """Validation purement lexicale (jamais .resolve()) — même modèle que _result_path."""
    if not decision_record_id or not _DECISION_RECORD_ID_RE.match(decision_record_id):
        raise ValueError("INVALID_DECISION_RECORD_ID")
    d = store_dir or KX108_DECISION_DIR
    return d / f"{decision_record_id}.json"


def store_kx108_decision_record(record: dict, store_dir: Optional[Path] = None) -> dict:
    """
    Publication STRICTE, append-only, ATOMIQUE — même modèle que
    store_approval_artifact / store_test_contract_result : fichier
    temporaire complet puis publication via os.link (échoue si la
    cible existe déjà), jamais de fichier partiel visible.
    """
    decision_record_id = record.get("decision_record_id")
    try:
        p = _decision_record_path(decision_record_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_DECISION_RECORD_ID, "decision_record_id": decision_record_id}

    payload = json.dumps(record, ensure_ascii=False, indent=2)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = f".{p.name}.{os.getpid()}.{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    tmp = p.parent / tmp_name
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, "decision_record_id": decision_record_id}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": STATUS_IDEMPOTENT_EXISTING_IDENTICAL, "decision_record_id": decision_record_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, "decision_record_id": decision_record_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_kx108_decision_record(decision_record_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    """Charge une décision KX108 stockée — jamais reconstruite à la volée."""
    try:
        p = _decision_record_path(decision_record_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_kx108_decision_record(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    """
    Intégrité STRUCTURELLE : schéma supporté, champs liés présents,
    hash stocké == recalculé, decision_authority == KX108_ONLY,
    x108_gate dans l'énumération valide.
    """
    if record is None:
        return False, "DECISION_RECORD_MISSING"
    if record.get("decision_record_schema_version") != SCHEMA_VERSION:
        return False, "DECISION_RECORD_SCHEMA_UNSUPPORTED"
    for f in _record_bound_fields_for(record):
        if f not in record:
            return False, f"DECISION_RECORD_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if record.get("x108_gate") not in VALID_X108_GATES:
        return False, "X108_GATE_INVALID"
    expected_hash = compute_kx108_decision_record_hash(record)
    if record.get("decision_record_hash") != expected_hash:
        return False, "DECISION_RECORD_HASH_MISMATCH"
    return True, None


def _validate_binding_context(binding_context: dict) -> Optional[str]:
    for f in _BINDING_CONTEXT_FIELDS:
        if not binding_context.get(f):
            return f"BINDING_CONTEXT_FIELD_MISSING:{f}"
    return None


def run_and_persist_kx108_decision(
    tooling_build_state_kwargs: dict,
    binding_context: dict,
    store_dir: Optional[Path] = None,
) -> dict:
    """
    Chemin de production UNIQUE reliant une ToolingBuildState exacte,
    déjà revue, à une décision KX108 canonique persistée :

      1. valide le contexte de liaison (identités d'évidence pré-KX108)
      2. invoke run_tooling_build_pipeline EXACTEMENT UNE FOIS
      3. reçoit le CanonicalDecisionEnvelope réel (jamais fabriqué)
      4. le sérialise sans perte (canonical_envelope)
      5. le lie aux identités d'évidence exactes
      6. calcule le hash d'enregistrement de décision
      7. publie atomiquement
      8. recharge
      9. vérifie
      10. retourne la référence à l'enregistrement persisté

    N'accepte JAMAIS x108_gate/reason_code/contradictions/etc. fournis
    par l'appelant en lieu et place d'une invocation réelle. Un échec
    de persistance NE réinvoque JAMAIS KX108 (l'invocation a déjà eu
    lieu et son résultat est déjà en main au moment de l'échec).
    """
    binding_error = _validate_binding_context(binding_context)
    if binding_error:
        return {"status": "REJECTED", "reason": binding_error}

    from sigma.contracts import ToolingBuildState
    from sigma.protocols import run_tooling_build_pipeline

    state = ToolingBuildState(**tooling_build_state_kwargs)
    decision = run_tooling_build_pipeline(state)  # EXACTEMENT UNE FOIS
    envelope = dataclasses.asdict(decision)

    created_at = _now()
    record: dict = {
        "decision_record_schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        **{k: binding_context[k] for k in _BINDING_CONTEXT_FIELDS},
        "decision_id": envelope.get("decision_id"),
        "trace_id": envelope.get("trace_id"),
        "domain": envelope.get("domain"),
        "x108_gate": envelope.get("x108_gate"),
        "reason_code": envelope.get("reason_code"),
        "severity": envelope.get("severity"),
        "market_verdict": envelope.get("market_verdict"),
        "contradictions": list(envelope.get("contradictions") or []),
        "unknowns": list(envelope.get("unknowns") or []),
        "risk_flags": list(envelope.get("risk_flags") or []),
        "decision_authority": DECISION_AUTHORITY,
        "canonical_envelope": envelope,
    }

    identity_seed = {k: record[k] for k in _BINDING_CONTEXT_FIELDS}
    identity_seed["canonical_envelope"] = envelope
    record["decision_record_id"] = _compute_decision_record_identity(identity_seed)
    record["decision_record_hash"] = compute_kx108_decision_record_hash(record)

    store_result = store_kx108_decision_record(record, store_dir)
    reloaded = load_kx108_decision_record(record["decision_record_id"], store_dir)
    verify_ok, verify_reason = verify_kx108_decision_record(reloaded)

    return {
        "decision_record_id": record["decision_record_id"],
        "store_result": store_result,
        "record": reloaded,
        "verify_ok": verify_ok,
        "verify_reason": verify_reason,
    }


# ── PRE-EXECUTION (phase 1) ──────────────────────────────────────────────────

def _compute_pre_decision_record_identity(seed: dict) -> str:
    """Identité CONTENU d'une décision PRE — préfixe distinct (kxpre-) de la
    décision POST (kxd-), aucune collision d'ID possible entre phases."""
    payload = json.dumps(
        {k: seed.get(k) for k in _PRE_IDENTITY_SEED_FIELDS},
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"kxpre-{digest[:32]}"


def _validate_pre_binding_context(binding_context: dict) -> Optional[str]:
    """Jeu de liaison PRE — exige approval_id (HumanApproval précède KX108_PRE
    dans l'ordre canonique) mais JAMAIS test_result_id / test_result_record_hash
    (preuves post-apply inexistantes). Fail-closed sur tout champ absent."""
    for f in _PRE_BINDING_CONTEXT_FIELDS:
        if not binding_context.get(f):
            return f"PRE_BINDING_CONTEXT_FIELD_MISSING:{f}"
    return None


def run_and_persist_kx108_pre_execution_decision(
    pre_tooling_build_state_kwargs: dict,
    pre_binding_context: dict,
    store_dir: Optional[Path] = None,
) -> dict:
    """
    Chemin de production PRE-EXECUTION — phase 1 du gate KX108 deux phases.

    Relie une ToolingBuildState PRÉ-ACTION (aucune évidence post-apply :
    aucun apply receipt, aucun TestContractResult, aucun target_post_sha256)
    à une décision KX108 canonique persistée avec decision_phase=PRE_EXECUTION.
    Ordre canonique : HumanApproval déjà validée -> KX108_PRE. Le contexte
    de liaison PORTE donc approval_id ; il ne porte jamais test_result_*.

      1. valide le contexte de liaison PRE (approval_id requis ; aucun test_result_*)
      2. invoke sigma.protocols.run_tooling_build_pipeline EXACTEMENT UNE FOIS
         (kernel souverain INCHANGÉ — c'est l'évidence qui change de phase,
          pas le moteur de décision)
      3. reçoit le CanonicalDecisionEnvelope réel (jamais fabriqué)
      4. persiste un enregistrement immuable decision_phase=PRE_EXECUTION
      5. recharge + vérifie (jamais une seconde invocation KX108 :
         la vérification porte sur les octets stockés / le hash)

    N'accepte JAMAIS x108_gate fourni par l'appelant. Aucune HumanApproval.
    Aucune mutation de cible. Aucun TestContractResult. Seul
    x108_gate == "ALLOW" autorise la progression (interprétation appelante) ;
    "HOLD"/"BLOCK" arrêtent.
    """
    binding_error = _validate_pre_binding_context(pre_binding_context)
    if binding_error:
        return {"status": "REJECTED", "reason": binding_error}

    from sigma.contracts import ToolingBuildState
    from sigma.protocols import run_tooling_build_pipeline

    state = ToolingBuildState(**pre_tooling_build_state_kwargs)
    decision = run_tooling_build_pipeline(state)  # EXACTEMENT UNE FOIS
    envelope = dataclasses.asdict(decision)

    record: dict = {
        "decision_record_schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "decision_phase": PRE_DECISION_PHASE,
        **{k: pre_binding_context[k] for k in _PRE_BINDING_CONTEXT_FIELDS},
        "decision_id": envelope.get("decision_id"),
        "trace_id": envelope.get("trace_id"),
        "domain": envelope.get("domain"),
        "x108_gate": envelope.get("x108_gate"),
        "reason_code": envelope.get("reason_code"),
        "severity": envelope.get("severity"),
        "market_verdict": envelope.get("market_verdict"),
        "contradictions": list(envelope.get("contradictions") or []),
        "unknowns": list(envelope.get("unknowns") or []),
        "risk_flags": list(envelope.get("risk_flags") or []),
        "decision_authority": DECISION_AUTHORITY,
        "canonical_envelope": envelope,
    }

    identity_seed = {k: record[k] for k in _PRE_BINDING_CONTEXT_FIELDS}
    identity_seed["decision_phase"] = PRE_DECISION_PHASE
    identity_seed["canonical_envelope"] = envelope
    record["decision_record_id"] = _compute_pre_decision_record_identity(identity_seed)
    record["decision_record_hash"] = compute_kx108_decision_record_hash(record)

    store_result = store_kx108_decision_record(record, store_dir)
    reloaded = load_kx108_decision_record(record["decision_record_id"], store_dir)
    verify_ok, verify_reason = verify_kx108_decision_record(reloaded)

    return {
        "decision_record_id": record["decision_record_id"],
        "decision_phase": PRE_DECISION_PHASE,
        "x108_gate": record["x108_gate"],
        "store_result": store_result,
        "record": reloaded,
        "verify_ok": verify_ok,
        "verify_reason": verify_reason,
    }
