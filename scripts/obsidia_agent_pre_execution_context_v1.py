"""
obsidia_agent_pre_execution_context_v1.py
=========================================
AGENT_RUNTIME_PRE_EXECUTION_CONTEXT_V1 — capture canonique, immuable,
append-only, hors dépôt, des faits d'un cycle agent gouverné FIGÉS AVANT
toute invocation de provider.

Ce module est le pendant, pour un cycle agent -> provider interne, de
obsidia_pre_execution_context.py (qui capture une isolation Git avant une
mutation de contenu). Il ne le remplace pas, ne l'affaiblit pas et ne
partage aucun de ses champs : le rail de remédiation garde intégralement
son contrat (HumanApproval, execution_authority_hash, isolation Git,
test_contract_hash), qui n'est ni assoupli ni rendu optionnel ici.

Ce module NE DÉCIDE RIEN. Il ne produit aucun x108_gate, aucune
autorisation, aucun consentement. Il fige des faits pour que la décision
KX108 qui suit porte sur EXACTEMENT ce qui sera exécuté :

    execution_plan_digest = H(mission, provider, capability, payload,
                              action, domain, context packet)

Recalculé juste avant l'invocation, il ferme la fenêtre TOCTOU :
substitution de provider, de capability, de payload, de mission ou de
contexte -> digest différent -> refus, provider jamais atteint.

PORTÉE STRICTE : exécution INTERNE bornée (handler local déterministe,
sans effet de bord observable hors du processus). Ce rail ne dit RIEN
d'une actuation monde externe ni d'une opération irréversible, qui
gardent leur propre rail de consentement.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT_EXISTING_IDENTICAL = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_CONTEXT_ID = "INVALID_CONTEXT_ID"

# Portée d'exécution couverte par ce contexte. Une actuation externe ou
# irréversible n'est PAS couverte et exige son propre rail.
EXECUTION_SCOPE_INTERNAL_BOUNDED = "INTERNAL_BOUNDED_PROVIDER_EXECUTION"

AGENT_PRE_EXECUTION_CONTEXT_DIR = (
    Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "agent_pre_execution_contexts"
)

_CONTEXT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# Faits figés qui définissent l'exécution soumise à KX108.
_EXECUTION_PLAN_BOUND_FIELDS = (
    "action_id", "domain", "context_packet_id",
    "mission_id", "provider_id", "capability", "payload_sha256",
    "execution_scope",
)

_AGENT_CONTEXT_BOUND_FIELDS = (
    "context_schema_version", "context_id", "created_at",
    "agent_id", "agent_layer", "action_id", "domain",
    "context_packet_id", "context_packet_boundary",
    "mission_id", "provider_id", "capability", "payload_sha256",
    "execution_scope", "execution_plan_digest",
    "evidence_refs", "recommended_gate",
    # Invariants figés — jamais des drapeaux d'autorisation.
    "runtime_allowed_now", "emits_act", "memory_write", "kernel_mutation",
    "decision_authority",
)


class AgentPreExecutionContextError(Exception):
    """Erreur de contrat. Jamais un refus de gouvernance."""


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def compute_payload_sha256(payload: Optional[dict]) -> str:
    """Hash canonique du payload réellement transmis au provider."""
    return _sha256_json(dict(payload or {}))


def compute_execution_plan_digest(fields: dict) -> str:
    """
    Digest canonique du plan d'exécution — la seule chose sur laquelle
    KX108 se prononce en termes d'exécution. Fonction pure.
    """
    return _sha256_json({k: fields.get(k) for k in _EXECUTION_PLAN_BOUND_FIELDS})


def compute_agent_context_record_hash(record: dict) -> str:
    """SHA256 complet (64 hex) sur les champs liés. Exclut le hash lui-même."""
    return _sha256_json({k: record.get(k) for k in _AGENT_CONTEXT_BOUND_FIELDS})


def _compute_context_identity(record: dict) -> str:
    """
    Identité d'ÉVÉNEMENT — préfixe distinct de tout autre magasin.

    created_at entre dans l'identité : deux captures successives du même
    plan sont deux événements distincts qui COEXISTENT (append-only), au
    lieu d'entrer en collision sous un même identifiant avec des octets
    divergents. Le déterminisme rejouable est porté par
    execution_plan_digest, qui ne dépend d'aucun horodatage : c'est lui
    qui lie la décision KX108 à l'exécution.
    """
    digest = _sha256_json({k: record.get(k) for k in _AGENT_CONTEXT_BOUND_FIELDS})
    return f"apec-{digest[:32]}"


def _context_path(context_id: "str | None", store_dir: Optional[Path] = None) -> Path:
    """Validation purement lexicale — context_id est un identifiant, jamais un chemin."""
    if not context_id or not _CONTEXT_ID_RE.match(context_id):
        raise ValueError("INVALID_CONTEXT_ID")
    d = store_dir or AGENT_PRE_EXECUTION_CONTEXT_DIR
    return d / f"{context_id}.json"


def create_agent_pre_execution_context(
    *,
    agent_id: str,
    agent_layer: str,
    action_id: str,
    domain: str,
    context_packet_id: str,
    context_packet_boundary: str,
    mission_id: str,
    provider_id: str,
    capability: str,
    payload: Optional[dict] = None,
    evidence_refs: Optional[list] = None,
    recommended_gate: str = "NONE",
    execution_scope: str = EXECUTION_SCOPE_INTERNAL_BOUNDED,
) -> dict:
    """
    Fige les faits du cycle AVANT décision et AVANT exécution.

    Tout provient de données réellement présentes dans le cycle : identité
    de l'agent, du ContextPacket produit par le binder canonique, et du
    plan d'exécution qui sera passé au rail canonique. Aucun champ n'est
    une assertion de l'appelant sur une autorité quelconque.
    """
    for name, value in (
        ("agent_id", agent_id),
        ("action_id", action_id),
        ("domain", domain),
        ("context_packet_id", context_packet_id),
        ("mission_id", mission_id),
        ("provider_id", provider_id),
        ("capability", capability),
    ):
        if not value:
            raise AgentPreExecutionContextError(f"AGENT_CONTEXT_FIELD_REQUIRED:{name}")

    plan_fields = {
        "action_id": action_id,
        "domain": domain,
        "context_packet_id": context_packet_id,
        "mission_id": mission_id,
        "provider_id": provider_id,
        "capability": capability,
        "payload_sha256": compute_payload_sha256(payload),
        "execution_scope": execution_scope,
    }

    record: dict = {
        "context_schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "agent_id": agent_id,
        "agent_layer": agent_layer,
        "action_id": action_id,
        "domain": domain,
        "context_packet_id": context_packet_id,
        "context_packet_boundary": context_packet_boundary,
        "mission_id": mission_id,
        "provider_id": provider_id,
        "capability": capability,
        "payload_sha256": plan_fields["payload_sha256"],
        "execution_scope": execution_scope,
        "execution_plan_digest": compute_execution_plan_digest(plan_fields),
        "evidence_refs": sorted(set(evidence_refs or [])),
        "recommended_gate": recommended_gate,
        # Invariants figés : ce contexte n'autorise jamais rien par lui-même.
        "runtime_allowed_now": False,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "decision_authority": DECISION_AUTHORITY,
    }

    record["context_id"] = _compute_context_identity(record)
    record["context_record_hash"] = compute_agent_context_record_hash(record)
    return record


def store_agent_pre_execution_context_record(
    record: dict, store_dir: Optional[Path] = None
) -> dict:
    """Publication append-only ATOMIQUE (fichier temporaire puis os.link)."""
    context_id = record.get("context_id")
    try:
        p = _context_path(context_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_CONTEXT_ID, "context_id": context_id}

    payload = json.dumps(record, ensure_ascii=False, indent=2)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp = p.parent / (
        f".{p.name}.{os.getpid()}."
        f"{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    )
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, "context_id": context_id}
    except FileExistsError:
        if p.read_text(encoding="utf-8") == payload:
            return {"status": STATUS_IDEMPOTENT_EXISTING_IDENTICAL, "context_id": context_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, "context_id": context_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_agent_pre_execution_context_record(
    context_id: str, store_dir: Optional[Path] = None
) -> Optional[dict]:
    """Charge un contexte stocké — jamais reconstruit à la volée."""
    try:
        p = _context_path(context_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_agent_pre_execution_context_record(
    record: Optional[dict],
) -> "tuple[bool, Optional[str]]":
    """
    Intégrité STRUCTURELLE : schéma supporté, champs liés présents,
    invariants de non-souveraineté intacts, execution_plan_digest
    recalculable depuis les octets persistés, hash stocké == recalculé.
    """
    if record is None:
        return False, "AGENT_CONTEXT_RECORD_MISSING"
    if record.get("context_schema_version") != SCHEMA_VERSION:
        return False, "AGENT_CONTEXT_SCHEMA_UNSUPPORTED"
    for f in _AGENT_CONTEXT_BOUND_FIELDS:
        if f not in record:
            return False, f"AGENT_CONTEXT_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    for flag in ("runtime_allowed_now", "emits_act", "memory_write", "kernel_mutation"):
        if record.get(flag) is not False:
            return False, f"AGENT_CONTEXT_INVARIANT_VIOLATED:{flag}"

    recomputed_plan = compute_execution_plan_digest(record)
    if recomputed_plan != record.get("execution_plan_digest"):
        return False, "EXECUTION_PLAN_DIGEST_NOT_SELF_CONTAINED"

    if record.get("context_record_hash") != compute_agent_context_record_hash(record):
        return False, "AGENT_CONTEXT_RECORD_HASH_MISMATCH"
    return True, None


def verify_execution_plan_binding(
    record: Optional[dict],
    *,
    context_packet_id: str,
    mission_id: str,
    provider_id: str,
    capability: str,
    payload: Optional[dict] = None,
) -> "tuple[bool, Optional[str]]":
    """
    Anti-TOCTOU : recalcule le digest depuis ce qui va RÉELLEMENT être
    invoqué et exige l'égalité stricte avec le contexte figé avant la
    décision. Toute substitution -> refus.
    """
    ok, reason = verify_agent_pre_execution_context_record(record)
    if not ok:
        return False, reason

    observed = compute_execution_plan_digest(
        {
            "action_id": record.get("action_id"),
            "domain": record.get("domain"),
            "context_packet_id": context_packet_id,
            "mission_id": mission_id,
            "provider_id": provider_id,
            "capability": capability,
            "payload_sha256": compute_payload_sha256(payload),
            "execution_scope": record.get("execution_scope"),
        }
    )

    if observed != record.get("execution_plan_digest"):
        return False, "EXECUTION_PLAN_BINDING_MISMATCH"
    if context_packet_id != record.get("context_packet_id"):
        return False, "CONTEXT_PACKET_BINDING_MISMATCH"
    return True, None
