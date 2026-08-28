#!/usr/bin/env python3
"""OBSIDIA CG-C — CognitiveCapabilityLease + EngineeringLease : REPRÉSENTATION
RUNTIME CANONIQUE, ENTIÈREMENT INERTE.

Un bail CG-C peut être : construit, persisté (write-once), rechargé, vérifié
structurellement, vérifié contextuellement, révoqué (append-only), devenir
périmé/clos, et rejeté (rejeu / falsification / hors-portée).

Un bail CG-C N'ACCORDE JAMAIS : Edit / Write / Bash / Git / spawn d'agent /
mutation de système de fichiers ; N'AUTORISE JAMAIS une exécution gouvernée
ni KX108_PRE ; N'ACTIVE JAMAIS une ingénierie Claude.

  LEASE_RECORD_RUNTIME_IMPLEMENTED = TRUE
  LEASE_ENFORCEMENT_ACTIVE         = FALSE
  LEASE_GRANTS_TOOL_ACCESS         = FALSE
  HARD_TOOL_GATE_ACTIVE            = FALSE

Invariants d'autorité :
  COGNITIVE_CAPABILITY_LEASE = ENGINEERING_LEASE = NON_SOVEREIGN
  ENGINEERING_LEASE != EXECUTION_AUTHORITY ; != KX_AUTHORITY
  MORE_TOOLS / MORE_REASONING / RESOURCE_DISCOVERY  !=  MORE_AUTHORITY
  CLAUDE_REQUESTS_ENGINEERING = ALLOWED ; CLAUDE_SELF_AUTHORIZES_ENGINEERING = FALSE

Réutilise CG-B : CapabilityRequest, RouteDecision, RouteReceipt, mission_submission_id,
mission_contract_ref, human_decision_ref, capability_request_refs, context_request_ref.
Pas de seconde Gateway. Pas d'enveloppe de mission dupliquée.
`decision_authority = KX108_ONLY` — affirmé, jamais fixé ici.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_gateway_route_decision_v0 as _RD  # CG-B (schémas + store + helpers)

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"
LEASE_DOMAIN_TAG = "OBSIDIA_CGC_COGNITIVE_CAPABILITY_LEASE_V0"
REVOCATION_DOMAIN_TAG = "OBSIDIA_CGC_LEASE_REVOCATION_V0"

# ── Bornes d'inertie explicites ──────────────────────────────────────────
LEASE_RECORD_RUNTIME_IMPLEMENTED = True
LEASE_ENFORCEMENT_ACTIVE = False
LEASE_GRANTS_TOOL_ACCESS = False
HARD_TOOL_GATE_ACTIVE = False
PRE_TOOL_LEASE_LOOKUP_ACTIVE = False
COGNITIVE_CAPABILITY_LEASE_ACTIVE = False
ENGINEERING_LEASE_ACTIVE = False
CLAUDE_SELF_AUTHORIZES_ENGINEERING = False
PROVIDER_SELF_ISSUES_LEASE = False
LEASE_CLASS_IMPLICIT_GLOBAL_RIGHTS = False
LANGUAGE_LEASE_AUTO_CALLS_PROVIDER = False
REASONING_LEASE_AUTO_CALLS_PROVIDER = False
ENGINEERING_LEASE_AUTO_CALLS_PROVIDER = False
MISSION_CAPABILITY_SCOPE_BINDING = "NOT_YET_ACTIVE"
LEASE_CAN_AUTHORIZE_TOOL_ACCESS_WHILE_MISSION_SCOPE_UNBOUND = False
MAX_GOVERNED_MUTATION_OPERATION_V0 = "UPDATE_TARGET_FROM_SOURCE"
MULTI_OPERATION_GENERALIZATION = "NOT_YET_PROVEN"
GAP_CG_9_COGNITIVE_PROVIDER_ABSTRACTION = "OPEN"
GAP_CG_7_PRE_TOOL_LEASE_LOOKUP = "OPEN"
GAP_CG_4_GOVERNED_ENGINEERING_ROUTE = "OPEN"
OBSIDURE_PROPOSAL_ONLY = True
OBSIDURE_ENGINEERING_EXECUTION_ACTIVE = False

# ── Classes de bail (descriptives — AUCUN droit global implicite) ────────
LANGUAGE_LEASE = "LANGUAGE_LEASE"
REASONING_LEASE = "REASONING_LEASE"
ENGINEERING_LEASE = "ENGINEERING_LEASE"
_LEASE_CLASSES = (LANGUAGE_LEASE, REASONING_LEASE, ENGINEERING_LEASE)

_CLASS_TO_ROUTE = {
    LANGUAGE_LEASE: _RD.ROUTE_LLM_LANGUAGE,
    REASONING_LEASE: _RD.ROUTE_LLM_REASONING,
    ENGINEERING_LEASE: _RD.ROUTE_LLM_ENGINEERING,
}
# Aucune route ne donne un bail hors de ces 3 correspondances.
_NO_LEASE_ROUTES = (_RD.ROUTE_HUMAN_AUTHORITY, _RD.ROUTE_UNKNOWN, _RD.ROUTE_STACK_NATIVE)

# ── Issuers ────────────────────────────────────────────────────────────
ISSUER_GATEWAY_CAPABILITY_DECISION = "OBSIDIA_GATEWAY_CAPABILITY_DECISION"
_AUTHORIZED_ISSUERS = (ISSUER_GATEWAY_CAPABILITY_DECISION,)
_FORBIDDEN_ISSUERS = ("CLAUDE", "BRODY", "OBSIDURE")

# ── Providers (liste bornée, PAS une abstraction) ──────────────────────
_KNOWN_PROVIDERS = ("brody", "obsidure", "claude")

# ── Portées : ordres partiels (jamais ALL / wildcard non borné) ────────
_READ_WRITE_ORDER = ("NONE", "BOUNDED_PATHS")
_TEST_ORDER = ("NONE", "BOUNDED")
_GIT_ORDER = ("NONE", "READ_ONLY")
_MUTATION_ORDER = ("NONE", "UPDATE_TARGET_FROM_SOURCE")
_UNBOUNDED_TOKENS = {"*", "**", "ALL", "ANY", "/", "/**", ".", "./**"}

# ── Terminaisons (mission-bound ; pas de dépendance à l'horloge murale) ─
TERM_MISSION_CLOSED = "MISSION_CLOSED"
TERM_MISSION_HOLD = "MISSION_HOLD"
TERM_REVOKED = "REVOKED"
TERM_EXPIRED_EPOCH = "EXPIRED_EPOCH"
TERM_MISSION_BOUND_ACTIVE = "MISSION_BOUND_ACTIVE"
_TERMINATIONS = (TERM_MISSION_BOUND_ACTIVE, TERM_MISSION_CLOSED, TERM_MISSION_HOLD,
                 TERM_REVOKED, TERM_EXPIRED_EPOCH)
_STALE_TERMINATIONS = (TERM_MISSION_CLOSED, TERM_MISSION_HOLD, TERM_REVOKED, TERM_EXPIRED_EPOCH)

# ── Statuts ───────────────────────────────────────────────────────────
STATUS_CANDIDATE_INERT = "CANDIDATE_INERT"
STATUS_LEASE_REJECTED = "LEASE_REJECTED"
STATUS_LEASE_BUILT_INERT = "LEASE_BUILT_INERT"

# ── Verdicts contextuels (jamais un booléen effondré) ─────────────────
V_VALID_INERT = "VALID_INERT"
V_REVOKED = "REVOKED"
V_MISSION_MISMATCH = "MISSION_MISMATCH"
V_REQUEST_MISMATCH = "REQUEST_MISMATCH"
V_ROUTE_MISMATCH = "ROUTE_MISMATCH"
V_SCOPE_EXPANSION = "SCOPE_EXPANSION"
V_MISSION_SCOPE_UNBOUND = "MISSION_SCOPE_UNBOUND"
V_MISSION_CLOSED = "MISSION_CLOSED"
V_MISSION_HOLD = "MISSION_HOLD"
V_TAMPERED = "TAMPERED"
V_STALE = "STALE"
V_ISSUER_INVALID = "ISSUER_INVALID"
V_STRUCTURAL_INVALID = "STRUCTURAL_INVALID"
# CG-C2 — chaîne à 3 niveaux liée à la mission (schéma v2)
V_REQUEST_SCOPE_EXCEEDS_MISSION = "REQUEST_SCOPE_EXCEEDS_MISSION"
V_MISSION_SCOPE_INVALID = "MISSION_SCOPE_INVALID"
V_MISSION_SCOPE_MISMATCH = "MISSION_SCOPE_MISMATCH"
V_ISSUANCE_INVALID = "ISSUANCE_INVALID"
V_ISSUANCE_MISMATCH = "ISSUANCE_MISMATCH"
V_ISSUANCE_NOT_ELIGIBLE = "ISSUANCE_NOT_ELIGIBLE"
V_LEASE_CLASS_NOT_IN_MISSION = "LEASE_CLASS_NOT_IN_MISSION"
V_HUMAN_GRANT_INVALID = "HUMAN_GRANT_INVALID"
V_HUMAN_GRANT_MISMATCH = "HUMAN_GRANT_MISMATCH"
V_HUMAN_GRANT_SCOPE_EXPANSION = "HUMAN_GRANT_SCOPE_EXPANSION"

# ── Schéma de bail ───────────────────────────────────────────────────
#   v1 = bail CG-C (portée de mission NON liée ; INERTE, jamais exécutoire)
#   v2 = bail CG-C2 (MissionCapabilityScope + LeaseIssuanceDecision liés par hash)
SCHEMA_VERSION_MISSION_BOUND = 2
_SUPPORTED_SCHEMA_VERSIONS = (SCHEMA_VERSION, SCHEMA_VERSION_MISSION_BOUND)
LEGACY_CGC_LEASE_WITHOUT_MISSION_SCOPE = "INERT_NOT_ENFORCEABLE"

_now = _RD._now
_canon = _RD._canon
_sha = _RD._sha256_hex


def _lease_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "capability_leases"


# ══════════════════════════════════════════════════════════════════════════
#  1 — Modèle de portée bornée (jamais d'élargissement, jamais ALL)
# ══════════════════════════════════════════════════════════════════════════

_SCOPE_FIELDS = ("allowed_providers", "allowed_tools", "allowed_paths",
                 "allowed_operations", "read_scope", "write_scope",
                 "test_scope", "git_scope", "max_mutation_category")


def empty_scope() -> dict:
    """Portée fail-closed : rien n'est permis tant que rien n'est explicitement borné."""
    return {
        "allowed_providers": [], "allowed_tools": [], "allowed_paths": [],
        "allowed_operations": [], "read_scope": "NONE", "write_scope": "NONE",
        "test_scope": "NONE", "git_scope": "NONE", "max_mutation_category": "NONE",
    }


def normalize_scope(scope: Optional[dict]) -> "tuple[Optional[dict], Optional[str]]":
    """Normalise + rejette toute portée non bornée. Champs omis -> NONE / []."""
    s = empty_scope()
    if scope:
        if not isinstance(scope, dict):
            return None, "SCOPE_NOT_A_DICT"
        for k in scope:
            if k not in _SCOPE_FIELDS:
                return None, f"SCOPE_UNKNOWN_FIELD:{k}"
        for k in ("allowed_providers", "allowed_tools", "allowed_paths", "allowed_operations"):
            v = scope.get(k, [])
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                return None, f"SCOPE_FIELD_NOT_STR_LIST:{k}"
            for x in v:
                if x.strip().upper() in _UNBOUNDED_TOKENS or x.strip() in _UNBOUNDED_TOKENS:
                    return None, f"SCOPE_UNBOUNDED_WILDCARD:{k}:{x}"
            s[k] = sorted(set(v))
        for p in s["allowed_providers"]:
            if p not in _KNOWN_PROVIDERS:
                return None, f"SCOPE_UNKNOWN_PROVIDER:{p}"
        if s["allowed_operations"] and any(op != MAX_GOVERNED_MUTATION_OPERATION_V0
                                           for op in s["allowed_operations"]):
            return None, "SCOPE_OPERATION_BEYOND_V0_CARDINALITY"
        for k, order in (("read_scope", _READ_WRITE_ORDER), ("write_scope", _READ_WRITE_ORDER),
                         ("test_scope", _TEST_ORDER), ("git_scope", _GIT_ORDER),
                         ("max_mutation_category", _MUTATION_ORDER)):
            v = scope.get(k, "NONE")
            if v not in order:
                return None, f"SCOPE_VALUE_INVALID:{k}:{v}"
            s[k] = v
        # cohérence : écriture bornée sans chemins => incomplet (fail-closed)
        if s["write_scope"] != "NONE" and not s["allowed_paths"]:
            return None, "SCOPE_WRITE_WITHOUT_ALLOWED_PATHS"
        if s["max_mutation_category"] != "NONE" and s["write_scope"] == "NONE":
            return None, "SCOPE_MUTATION_WITHOUT_WRITE_SCOPE"
    return s, None


def _ord_le(a: str, b: str, order: tuple) -> bool:
    return order.index(a) <= order.index(b)


def scope_le(sub: dict, sup: dict) -> "tuple[bool, Optional[str]]":
    """`sub` <= `sup` : sous-ensemble sur les listes, ordre partiel sur les scopes.
    Utilisé pour LEASE_CAPABILITY_SCOPE <= REQUESTED (build) et <= MISSION (futur)."""
    for k in ("allowed_providers", "allowed_tools", "allowed_paths", "allowed_operations"):
        if not set(sub.get(k, [])) <= set(sup.get(k, [])):
            extra = sorted(set(sub.get(k, [])) - set(sup.get(k, [])))
            return False, f"{k}:{extra}"
    for k, order in (("read_scope", _READ_WRITE_ORDER), ("write_scope", _READ_WRITE_ORDER),
                     ("test_scope", _TEST_ORDER), ("git_scope", _GIT_ORDER),
                     ("max_mutation_category", _MUTATION_ORDER)):
        if not _ord_le(sub.get(k, "NONE"), sup.get(k, "NONE"), order):
            return False, f"{k}:{sub.get(k)}>{sup.get(k)}"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  2 — Construction du bail canonique (INERTE)
# ══════════════════════════════════════════════════════════════════════════

_BOUND_FIELDS = (
    "schema_version", "domain_tag", "lease_class",
    "mission_submission_id", "mission_contract_ref", "mission_genesis_record_hash",
    "plan_hash", "capability_request_id", "route_decision_ref", "route_class",
    "requested_capability", "reason", "human_decision_ref",
    "capability_scope", "requested_capability_scope",
    "termination_condition", "issued_by", "issuer_ref", "status",
    "is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access",
)
# v2 (CG-C2) : liaisons additionnelles hachées vers la borne humaine de mission.
_BOUND_FIELDS_V2 = _BOUND_FIELDS + (
    "mission_capability_scope_ref", "mission_capability_scope_hash",
    "lease_issuance_decision_ref", "lease_issuance_decision_hash",
)


def _bound_fields(schema_version) -> tuple:
    return _BOUND_FIELDS_V2 if schema_version == SCHEMA_VERSION_MISSION_BOUND else _BOUND_FIELDS


def _reject(reason: str, **extra) -> dict:
    return {"status": STATUS_LEASE_REJECTED, "reason": reason,
            "lease": None, "grants_tool_access": False,
            "is_execution_authority": False, "is_kx_authority": False, **extra}


def prepare_cognitive_capability_lease(
    *, lease_class: str,
    capability_request: dict,
    route_decision: dict,
    mission_submission: dict,
    lease_scope: Optional[dict] = None,
    requested_capability_scope: Optional[dict] = None,
    human_decision_ref: Optional[str] = None,
    issued_by: str = ISSUER_GATEWAY_CAPABILITY_DECISION,
    issuer_ref: Optional[str] = None,
    mission_capability_scope: Optional[dict] = None,
    lease_issuance_decision: Optional[dict] = None,
) -> dict:
    """Valide toutes les liaisons puis construit un bail INERTE, ou rejette
    de façon fermée. Le bail construit N'ACCORDE RIEN.

    v1 (défaut) : `mission_capability_scope` et `lease_issuance_decision` absents
    -> bail CG-C, portée de mission NON liée, `NOT_YET_ACTIVE`, jamais exécutoire.
    v2 (CG-C2) : les DEUX fournis -> chaîne à 3 niveaux vérifiée
    `LEASE <= REQUESTED <= MISSION_ALLOWED`, liaisons hachées, binding `ACTIVE`.
    Toujours INERTE : `grants_tool_access=False`, `lease_enforcement_active=False`."""
    if lease_class not in _LEASE_CLASSES:
        return _reject(f"UNKNOWN_LEASE_CLASS:{lease_class}")
    if issued_by in _FORBIDDEN_ISSUERS or issued_by not in _AUTHORIZED_ISSUERS:
        return _reject(f"ISSUER_NOT_AUTHORIZED:{issued_by}")  # §11 : Claude/Brody/Obsidure ne DÉLIVRENT pas

    ok_r, why_r = _RD.verify_route_decision(route_decision)
    if not ok_r:
        return _reject(f"ROUTE_DECISION_INVALID:{why_r}")
    rclass = route_decision.get("route_class")
    if route_decision.get("fail_closed_hold") or route_decision.get("gate_verdict") in ("DENY", "HOLD", "CLARIFY"):
        return _reject("NO_LEASE_FOR_HOLD_OR_DENY_OR_FAILCLOSED")
    if rclass in _NO_LEASE_ROUTES:
        return _reject(f"NO_LEASE_FOR_ROUTE:{rclass}")
    if _CLASS_TO_ROUTE.get(lease_class) != rclass:
        return _reject(f"ROUTE_CLASS_INCOMPATIBLE:{lease_class}!={rclass}")

    if not isinstance(capability_request, dict) or \
       capability_request.get("domain_tag") != "OBSIDIA_CGB_CAPABILITY_REQUEST_V0":
        return _reject("CAPABILITY_REQUEST_INVALID")
    if capability_request.get("granted") is not False:
        return _reject("CAPABILITY_REQUEST_NOT_INERT")
    cap_id = capability_request.get("capability_request_id")
    if not (isinstance(cap_id, str) and cap_id.startswith("gcap-")):
        return _reject("CAPABILITY_REQUEST_ID_INVALID")
    cr_route = (capability_request.get("route_decision") or {}).get("route_decision_id")
    if cr_route != route_decision.get("route_decision_id"):
        return _reject("CAPABILITY_REQUEST_ROUTE_DECISION_MISMATCH")

    if not isinstance(mission_submission, dict) or \
       mission_submission.get("domain_tag") != "OBSIDIA_CGB_MISSION_SUBMISSION_V0":
        return _reject("MISSION_SUBMISSION_INVALID")
    msid = mission_submission.get("mission_submission_id")
    if not (isinstance(msid, str) and msid.startswith("gsub-")):
        return _reject("MISSION_SUBMISSION_ID_INVALID")
    if capability_request.get("mission_submission_id") != msid:
        return _reject("CAPABILITY_REQUEST_MISSION_MISMATCH")

    scope, why_s = normalize_scope(lease_scope)
    if scope is None:
        return _reject(f"LEASE_SCOPE_INVALID:{why_s}")
    req_scope, why_rs = normalize_scope(requested_capability_scope)
    if req_scope is None:
        return _reject(f"REQUESTED_SCOPE_INVALID:{why_rs}")
    # §15 : le bail NARROW la portée demandée, jamais l'inverse.
    le, extra = scope_le(scope, req_scope)
    if not le:
        return _reject(f"LEASE_SCOPE_EXPANSION_OVER_REQUEST:{extra}")
    if lease_class == ENGINEERING_LEASE and scope == empty_scope():
        # §17 : un ENGINEERING_LEASE sans portée explicite est un candidat
        # INCOMPLET, jamais un droit large silencieux.
        pass  # autorisé comme candidat inerte incomplet ; jamais élargi

    # ── CG-C2 : liaison optionnelle à la borne humaine de mission ──
    _v2 = mission_capability_scope is not None or lease_issuance_decision is not None
    _mcs_ref = _mcs_hash = _lidec_ref = _lidec_hash = None
    if _v2:
        if mission_capability_scope is None or lease_issuance_decision is None:
            return _reject("MISSION_SCOPE_AND_ISSUANCE_DECISION_MUST_BE_PAIRED")
        import obsidia_mission_capability_scope_v0 as _MCS
        ok_m, why_m = _MCS.verify_mission_capability_scope(mission_capability_scope)
        if not ok_m:
            return _reject(f"MISSION_CAPABILITY_SCOPE_INVALID:{why_m}")
        if mission_capability_scope.get("mission_submission_id") != msid:
            return _reject("MISSION_CAPABILITY_SCOPE_MISSION_MISMATCH")
        if lease_class not in mission_capability_scope.get("allowed_lease_classes", []):
            return _reject(f"LEASE_CLASS_NOT_IN_MISSION_SCOPE:{lease_class}")
        ok_i, why_i = _MCS.verify_lease_issuance_decision(lease_issuance_decision)
        if not ok_i:
            return _reject(f"LEASE_ISSUANCE_DECISION_INVALID:{why_i}")
        if lease_issuance_decision.get("outcome") != _MCS.LEASE_ELIGIBLE_INERT:
            return _reject(f"LEASE_ISSUANCE_NOT_ELIGIBLE:{lease_issuance_decision.get('outcome')}")
        if lease_issuance_decision.get("mission_capability_scope_ref") != \
           mission_capability_scope["mission_capability_scope_id"]:
            return _reject("ISSUANCE_DECISION_MCS_MISMATCH")
        if lease_issuance_decision.get("mission_capability_scope_hash") != \
           mission_capability_scope["scope_record_hash"]:
            return _reject("ISSUANCE_DECISION_MCS_HASH_MISMATCH")
        if lease_issuance_decision.get("capability_request_id") != cap_id:
            return _reject("ISSUANCE_DECISION_REQUEST_MISMATCH")
        if lease_issuance_decision.get("route_decision_ref") != route_decision.get("route_decision_id"):
            return _reject("ISSUANCE_DECISION_ROUTE_MISMATCH")
        if lease_issuance_decision.get("proposed_lease_class") != lease_class:
            return _reject("ISSUANCE_DECISION_CLASS_MISMATCH")
        # CG-C2 repair : la décision d'émission DOIT lier le même HumanCapabilityGrant que la MCS.
        if lease_issuance_decision.get("human_capability_grant_ref") != \
           mission_capability_scope.get("human_capability_grant_id"):
            return _reject("ISSUANCE_DECISION_HUMAN_GRANT_MISMATCH")
        if lease_issuance_decision.get("human_capability_grant_hash") != \
           mission_capability_scope.get("human_capability_grant_hash"):
            return _reject("ISSUANCE_DECISION_HUMAN_GRANT_HASH_MISMATCH")
        _msc = mission_capability_scope["capability_scope"]
        le_rm, extra_rm = scope_le(req_scope, _msc)
        if not le_rm:
            return _reject(f"REQUEST_SCOPE_EXCEEDS_MISSION_SCOPE:{extra_rm}")
        le_lm, extra_lm = scope_le(scope, _msc)      # transitif via LEASE<=REQUEST déjà vérifié
        if not le_lm:
            return _reject(f"LEASE_SCOPE_EXCEEDS_MISSION_SCOPE:{extra_lm}")
        _mcs_ref = mission_capability_scope["mission_capability_scope_id"]
        _mcs_hash = mission_capability_scope["scope_record_hash"]
        _lidec_ref = lease_issuance_decision["lease_issuance_decision_id"]
        _lidec_hash = lease_issuance_decision["issuance_decision_record_hash"]

    env = mission_submission.get("envelope_refs") or {}
    core = {
        "schema_version": SCHEMA_VERSION_MISSION_BOUND if _v2 else SCHEMA_VERSION,
        "domain_tag": LEASE_DOMAIN_TAG,
        "lease_class": lease_class,
        "mission_submission_id": msid,
        "mission_contract_ref": env.get("mission_contract_ref"),
        # §8 : pas de hash de mission fabriqué — une soumission CG-B inerte n'a pas de genèse canonique.
        "mission_genesis_record_hash": "NOT_BOUND",
        "plan_hash": "NOT_BOUND",
        "capability_request_id": cap_id,
        "route_decision_ref": route_decision.get("route_decision_id"),
        "route_class": rclass,
        "requested_capability": (capability_request.get("requested_capability") or "")[:200],
        "reason": (capability_request.get("reason") or "")[:400],
        "human_decision_ref": human_decision_ref or capability_request.get("human_decision_ref"),
        "capability_scope": scope,
        "requested_capability_scope": req_scope,
        "termination_condition": TERM_MISSION_BOUND_ACTIVE,
        "issued_by": issued_by,
        "issuer_ref": issuer_ref,
        "status": STATUS_CANDIDATE_INERT,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
    }
    if _v2:
        core["mission_capability_scope_ref"] = _mcs_ref
        core["mission_capability_scope_hash"] = _mcs_hash
        core["lease_issuance_decision_ref"] = _lidec_ref
        core["lease_issuance_decision_hash"] = _lidec_hash
    bf = _bound_fields(core["schema_version"])
    rh = _sha(_canon({k: core.get(k) for k in bf}))
    core["lease_record_hash"] = rh
    core["lease_id"] = "cclease-" + rh[:32]
    core["created_at"] = _now()
    core["revocation_state"] = "NONE"
    core["mission_capability_scope_binding"] = "ACTIVE" if _v2 else MISSION_CAPABILITY_SCOPE_BINDING
    core["lease_enforcement_active"] = False
    core["engineering_lease"] = (lease_class == ENGINEERING_LEASE)
    return {"status": STATUS_LEASE_BUILT_INERT, "reason": None, "lease": core,
            "grants_tool_access": False}


def build_cognitive_capability_lease(**kw) -> Optional[dict]:
    """Raccourci : renvoie le record de bail seul (ou None si rejeté)."""
    out = prepare_cognitive_capability_lease(**kw)
    return out.get("lease")


# ══════════════════════════════════════════════════════════════════════════
#  3 — Vérificateur STRUCTUREL (déterministe)
# ══════════════════════════════════════════════════════════════════════════

def verify_capability_lease(lease: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if not isinstance(lease, dict):
        return False, "LEASE_MISSING"
    sv = lease.get("schema_version")
    if sv not in _SUPPORTED_SCHEMA_VERSIONS:
        return False, "SCHEMA_UNSUPPORTED"
    if lease.get("domain_tag") != LEASE_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if lease.get("lease_class") not in _LEASE_CLASSES:
        return False, "LEASE_CLASS_UNKNOWN"
    if lease.get("issued_by") not in _AUTHORIZED_ISSUERS:
        return False, f"ISSUER_NOT_AUTHORIZED:{lease.get('issued_by')}"
    for b in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        if lease.get(b) is not False:
            return False, f"LEASE_CLAIMS_AUTHORITY:{b}"
    if lease.get("lease_enforcement_active") not in (False, None):
        return False, "LEASE_ENFORCEMENT_ACTIVE_SET"
    for ref in ("route_decision_ref", "capability_request_id", "mission_submission_id"):
        v = lease.get(ref)
        if not (isinstance(v, str) and v):
            return False, f"MISSING_REF:{ref}"
    if not str(lease.get("capability_request_id", "")).startswith("gcap-"):
        return False, "CAPABILITY_REQUEST_ID_MALFORMED"
    if not str(lease.get("mission_submission_id", "")).startswith("gsub-"):
        return False, "MISSION_SUBMISSION_ID_MALFORMED"
    if not str(lease.get("route_decision_ref", "")).startswith("rdec-"):
        return False, "ROUTE_DECISION_REF_MALFORMED"
    if lease.get("route_class") not in _RD._ALL_ROUTE_CLASSES:
        return False, "ROUTE_CLASS_INVALID"
    if _CLASS_TO_ROUTE.get(lease["lease_class"]) != lease.get("route_class"):
        return False, "LEASE_CLASS_ROUTE_CLASS_INCONSISTENT"
    if lease.get("termination_condition") not in _TERMINATIONS:
        return False, "TERMINATION_CONDITION_INVALID"
    if lease.get("status") not in (STATUS_CANDIDATE_INERT, STATUS_LEASE_BUILT_INERT):
        return False, "STATUS_INVALID"
    sc, why = normalize_scope(lease.get("capability_scope"))
    if sc is None or sc != lease.get("capability_scope"):
        return False, f"CAPABILITY_SCOPE_INVALID:{why}"
    rsc, why2 = normalize_scope(lease.get("requested_capability_scope"))
    if rsc is None:
        return False, f"REQUESTED_SCOPE_INVALID:{why2}"
    le, extra = scope_le(sc, rsc)
    if not le:
        return False, f"CAPABILITY_SCOPE_EXPANSION:{extra}"

    # ── Discipline de version : v1 = jamais lié à la mission ; v2 = liaisons présentes ──
    if sv == SCHEMA_VERSION_MISSION_BOUND:
        for ref, pfx in (("mission_capability_scope_ref", "mcs-"),
                         ("lease_issuance_decision_ref", "lidec-")):
            if not str(lease.get(ref, "")).startswith(pfx):
                return False, f"{ref.upper()}_MALFORMED"
        for h in ("mission_capability_scope_hash", "lease_issuance_decision_hash"):
            if not (isinstance(lease.get(h), str) and lease.get(h)):
                return False, f"MISSING_REF:{h}"
        if lease.get("mission_capability_scope_binding") != "ACTIVE":
            return False, "MISSION_SCOPE_BINDING_NOT_ACTIVE"
    else:
        for f in ("mission_capability_scope_ref", "mission_capability_scope_hash",
                  "lease_issuance_decision_ref", "lease_issuance_decision_hash"):
            if lease.get(f) is not None:
                return False, f"V1_LEASE_CARRIES_V2_FIELD:{f}"
        if lease.get("mission_capability_scope_binding") not in (None, MISSION_CAPABILITY_SCOPE_BINDING):
            return False, "V1_LEASE_CLAIMS_MISSION_BINDING"

    rh = _sha(_canon({k: lease.get(k) for k in _bound_fields(sv)}))
    if lease.get("lease_record_hash") != rh:
        return False, "LEASE_RECORD_HASH_MISMATCH"
    if lease.get("lease_id") != "cclease-" + rh[:32]:
        return False, "LEASE_ID_NOT_DERIVED"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  4 — Persistance WRITE-ONCE + rechargement (restart-safe)
# ══════════════════════════════════════════════════════════════════════════

def persist_capability_lease(lease: dict, store_dir=None) -> dict:
    ok, why = verify_capability_lease(lease)
    if not ok:
        return {"status": "LEASE_PERSIST_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _lease_store(store_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "LEASE_PERSIST_REJECTED", "reason": f"MKDIR:{exc}"}
    p = d / f"{lease['lease_id']}.json"
    payload = json.dumps(lease, indent=2, sort_keys=True) + "\n"
    if p.exists():
        try:
            existing = p.read_text(encoding="utf-8")
        except OSError as exc:
            return {"status": "LEASE_PERSIST_REJECTED", "reason": f"READ:{exc}"}
        if existing == payload:
            return {"status": "IDEMPOTENT_ALREADY_EXISTS", "lease_id": lease["lease_id"]}
        return {"status": "LEASE_IMMUTABILITY_VIOLATION", "lease_id": lease["lease_id"],
                "divergent_lease_rewrite": "FAIL_CLOSED"}
    tmp = p.with_suffix(".json.tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(p)
    except OSError as exc:
        return {"status": "LEASE_PERSIST_REJECTED", "reason": f"WRITE:{exc}"}
    return {"status": "STORED", "lease_id": lease["lease_id"]}


def load_capability_lease(lease_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(lease_id, str) and lease_id.startswith("cclease-")):
        return None
    p = _lease_store(store_dir) / f"{lease_id}.json"
    if not p.is_file():
        return None
    try:
        lease = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ok, _ = verify_capability_lease(lease)
    return lease if ok else None


# ══════════════════════════════════════════════════════════════════════════
#  5 — Révocation append-only (patron Stage 4C, sans autorité HMA)
# ══════════════════════════════════════════════════════════════════════════

_REV_BOUND_FIELDS = ("schema_version", "domain_tag", "lease_id",
                     "mission_submission_id", "reason", "issued_by", "issuer_ref")


def build_lease_revocation(*, lease: dict, reason: str,
                           issued_by: str = ISSUER_GATEWAY_CAPABILITY_DECISION,
                           issuer_ref: Optional[str] = None) -> dict:
    ok, why = verify_capability_lease(lease)
    if not ok:
        return _reject(f"LEASE_INVALID_FOR_REVOCATION:{why}")
    if issued_by in _FORBIDDEN_ISSUERS or issued_by not in _AUTHORIZED_ISSUERS:
        return _reject(f"ISSUER_NOT_AUTHORIZED:{issued_by}")
    if not (isinstance(reason, str) and reason.strip()):
        return _reject("REVOCATION_REASON_REQUIRED")
    rec = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": REVOCATION_DOMAIN_TAG,
        "lease_id": lease["lease_id"],
        "mission_submission_id": lease["mission_submission_id"],
        "reason": reason[:400],
        "issued_by": issued_by,
        "issuer_ref": issuer_ref,
    }
    rh = _sha(_canon({k: rec.get(k) for k in _REV_BOUND_FIELDS}))
    rec["revocation_record_hash"] = rh
    rec["revocation_id"] = "cclrev-" + rh[:32]
    rec["created_at"] = _now()
    rec["is_execution_authority"] = False
    rec["is_kx_authority"] = False
    return {"status": "REVOCATION_BUILT", "reason": None, "revocation": rec}


def verify_lease_revocation(rev: Optional[dict],
                            lease: Optional[dict] = None) -> "tuple[bool, Optional[str]]":
    if not isinstance(rev, dict):
        return False, "REVOCATION_MISSING"
    if rev.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if rev.get("domain_tag") != REVOCATION_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if rev.get("issued_by") not in _AUTHORIZED_ISSUERS:
        return False, "ISSUER_NOT_AUTHORIZED"
    rh = _sha(_canon({k: rev.get(k) for k in _REV_BOUND_FIELDS}))
    if rev.get("revocation_record_hash") != rh:
        return False, "REVOCATION_HASH_MISMATCH"
    if rev.get("revocation_id") != "cclrev-" + rh[:32]:
        return False, "REVOCATION_ID_NOT_DERIVED"
    if lease is not None:
        if rev.get("lease_id") != lease.get("lease_id"):
            return False, "REVOCATION_LEASE_ID_MISMATCH"
        if rev.get("mission_submission_id") != lease.get("mission_submission_id"):
            return False, "REVOCATION_MISSION_MISMATCH"
    return True, None


def record_lease_revocation(rev: dict, store_dir=None) -> dict:
    ok, why = verify_lease_revocation(rev)
    if not ok:
        return {"status": "REVOCATION_RECORD_REJECTED", "reason": why}
    d = _lease_store(store_dir) / "revocations"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "REVOCATION_RECORD_REJECTED", "reason": f"MKDIR:{exc}"}
    p = d / f"{rev['revocation_id']}.json"
    payload = json.dumps(rev, indent=2, sort_keys=True) + "\n"
    if p.exists():
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": "IDEMPOTENT_ALREADY_EXISTS", "revocation_id": rev["revocation_id"]}
        return {"status": "REVOCATION_IMMUTABILITY_VIOLATION", "revocation_id": rev["revocation_id"]}
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(p)
    # journal append-only par bail
    try:
        with (d.parent / "revocations.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rev, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return {"status": "REVOCATION_RECORDED", "revocation_id": rev["revocation_id"]}


def load_lease_revocations(lease_id: str, store_dir=None) -> "list[dict]":
    d = _lease_store(store_dir) / "revocations"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("cclrev-*.json")):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if r.get("lease_id") == lease_id:
            out.append(r)
    return out


# ══════════════════════════════════════════════════════════════════════════
#  6 — Vérificateur CONTEXTUEL (verdict structuré, jamais un bool effondré)
# ══════════════════════════════════════════════════════════════════════════

def verify_capability_lease_context(
    *, lease: dict,
    mission_submission: dict,
    capability_request: dict,
    route_decision: dict,
    revocations: Optional[list] = None,
    mission_status: Optional[str] = None,   # "OPEN" | "CLOSED" | "HOLD"
    authorized_capability_scope: Optional[dict] = None,
    mission_capability_scope: Optional[dict] = None,
    lease_issuance_decision: Optional[dict] = None,
    human_capability_grant: Optional[dict] = None,
    human_capability_grant_authorization: Optional[dict] = None,
) -> dict:
    """Renvoie {verdict, reason, grants_tool_access: FALSE, enforcement_active: FALSE}.

    Bail v1 (CG-C) : toujours `V_MISSION_SCOPE_UNBOUND` — legacy INERT_NOT_ENFORCEABLE,
    quel que soit le `authorized_capability_scope` passé (§16 : pas d'activation
    rétroactive).

    Bail v2 (CG-C2) : exige `mission_capability_scope` + `lease_issuance_decision`
    canoniques ; vérifie la chaîne à 3 niveaux
    `LEASE <= REQUESTED <= MISSION_ALLOWED` + `outcome == LEASE_ELIGIBLE_INERT`.
    `V_VALID_INERT` signifie SEULEMENT : record cohérent + liaisons exactes + non
    révoqué + mission active + portée bornée. Il n'accorde AUCUN accès outil."""
    base = {"grants_tool_access": False, "enforcement_active": False,
            "lease_id": (lease or {}).get("lease_id")}

    ok, why = verify_capability_lease(lease)
    if not ok:
        return {**base, "verdict": V_STRUCTURAL_INVALID, "reason": why}
    if lease.get("issued_by") not in _AUTHORIZED_ISSUERS:
        return {**base, "verdict": V_ISSUER_INVALID, "reason": lease.get("issued_by")}

    if (mission_submission or {}).get("mission_submission_id") != lease["mission_submission_id"]:
        return {**base, "verdict": V_MISSION_MISMATCH, "reason": "submission_id"}
    if (capability_request or {}).get("capability_request_id") != lease["capability_request_id"]:
        return {**base, "verdict": V_REQUEST_MISMATCH, "reason": "capability_request_id"}
    if (capability_request or {}).get("mission_submission_id") != lease["mission_submission_id"]:
        return {**base, "verdict": V_REQUEST_MISMATCH, "reason": "request_mission_cross"}

    ok_r, why_r = _RD.verify_route_decision(route_decision)
    if not ok_r:
        return {**base, "verdict": V_ROUTE_MISMATCH, "reason": f"route_decision_invalid:{why_r}"}
    if route_decision.get("route_decision_id") != lease["route_decision_ref"]:
        return {**base, "verdict": V_ROUTE_MISMATCH, "reason": "route_decision_ref"}
    if route_decision.get("route_class") != lease["route_class"]:
        return {**base, "verdict": V_ROUTE_MISMATCH, "reason": "route_class_drift"}
    if _CLASS_TO_ROUTE.get(lease["lease_class"]) != route_decision.get("route_class"):
        return {**base, "verdict": V_ROUTE_MISMATCH, "reason": "class_route_incompatible"}
    if route_decision.get("fail_closed_hold") or route_decision.get("route_class") in _NO_LEASE_ROUTES:
        return {**base, "verdict": V_ROUTE_MISMATCH, "reason": "no_lease_route_or_hold"}

    revs = revocations if revocations is not None else []
    for rv in revs:
        okv, _ = verify_lease_revocation(rv, lease)
        if okv:
            return {**base, "verdict": V_REVOKED, "reason": rv.get("revocation_id")}

    tc = lease.get("termination_condition")
    if tc in _STALE_TERMINATIONS:
        return {**base, "verdict": V_STALE, "reason": tc}
    if mission_status == "CLOSED":
        return {**base, "verdict": V_MISSION_CLOSED, "reason": "mission_status"}
    if mission_status == "HOLD":
        return {**base, "verdict": V_MISSION_HOLD, "reason": "mission_status"}

    sc, _ = normalize_scope(lease.get("capability_scope"))
    rsc, _ = normalize_scope(lease.get("requested_capability_scope"))

    # ── Bail v1 legacy (CG-C) : INERT_NOT_ENFORCEABLE ; jamais de binding de
    #    mission, jamais d'enforcement, jamais d'accès outil — quelle que soit la
    #    portée ad-hoc passée. `V_VALID_INERT` ici == « record cohérent + dans la
    #    portée ad-hoc fournie », PAS « exécutoire » (§16 : pas de migration
    #    automatique accordant des droits). Le binding réel exige un bail v2. ──
    if lease.get("schema_version") != SCHEMA_VERSION_MISSION_BOUND:
        v1 = {**base, "mission_capability_scope_binding": "NOT_YET_ACTIVE",
              "legacy_lease": LEGACY_CGC_LEASE_WITHOUT_MISSION_SCOPE}
        if authorized_capability_scope is None:
            return {**v1, "verdict": V_MISSION_SCOPE_UNBOUND,
                    "reason": "MISSION_CAPABILITY_SCOPE_BINDING=NOT_YET_ACTIVE"}
        msc0, why_m0 = normalize_scope(authorized_capability_scope)
        if msc0 is None:
            return {**v1, "verdict": V_SCOPE_EXPANSION, "reason": f"mission_scope_invalid:{why_m0}"}
        le0, extra0 = scope_le(sc, msc0)
        if not le0:
            return {**v1, "verdict": V_SCOPE_EXPANSION, "reason": extra0}
        return {**v1, "verdict": V_VALID_INERT, "reason": None,
                "note": "bail v1 : record cohérent ; NON EXÉCUTOIRE ; aucun accès outil accordé"}

    # ── Bail v2 (CG-C2) : chaîne à 3 niveaux réellement vérifiée ──
    import obsidia_mission_capability_scope_v0 as _MCS
    if mission_capability_scope is None or lease_issuance_decision is None:
        return {**base, "verdict": V_MISSION_SCOPE_INVALID,
                "reason": "mission_capability_scope_or_issuance_decision_not_supplied"}
    ok_m, why_m = _MCS.verify_mission_capability_scope(mission_capability_scope)
    if not ok_m:
        return {**base, "verdict": V_MISSION_SCOPE_INVALID, "reason": why_m}
    if mission_capability_scope["mission_capability_scope_id"] != lease.get("mission_capability_scope_ref"):
        return {**base, "verdict": V_MISSION_SCOPE_MISMATCH, "reason": "mcs_id"}
    if mission_capability_scope["scope_record_hash"] != lease.get("mission_capability_scope_hash"):
        return {**base, "verdict": V_MISSION_SCOPE_MISMATCH, "reason": "mcs_hash"}
    if mission_capability_scope.get("mission_submission_id") != lease["mission_submission_id"]:
        return {**base, "verdict": V_MISSION_MISMATCH, "reason": "mcs_submission"}
    ok_i, why_i = _MCS.verify_lease_issuance_decision(lease_issuance_decision)
    if not ok_i:
        return {**base, "verdict": V_ISSUANCE_INVALID, "reason": why_i}
    if lease_issuance_decision.get("outcome") != _MCS.LEASE_ELIGIBLE_INERT:
        return {**base, "verdict": V_ISSUANCE_NOT_ELIGIBLE, "reason": lease_issuance_decision.get("outcome")}
    if lease_issuance_decision.get("lease_issuance_decision_id") != lease.get("lease_issuance_decision_ref"):
        return {**base, "verdict": V_ISSUANCE_MISMATCH, "reason": "lidec_id"}
    if lease_issuance_decision.get("issuance_decision_record_hash") != lease.get("lease_issuance_decision_hash"):
        return {**base, "verdict": V_ISSUANCE_MISMATCH, "reason": "lidec_hash"}
    if lease_issuance_decision.get("mission_capability_scope_ref") != \
       mission_capability_scope["mission_capability_scope_id"]:
        return {**base, "verdict": V_ISSUANCE_MISMATCH, "reason": "lidec_mcs"}
    if lease_issuance_decision.get("capability_request_id") != lease["capability_request_id"]:
        return {**base, "verdict": V_ISSUANCE_MISMATCH, "reason": "lidec_request"}
    if lease["lease_class"] not in mission_capability_scope.get("allowed_lease_classes", []):
        return {**base, "verdict": V_LEASE_CLASS_NOT_IN_MISSION, "reason": lease["lease_class"]}
    if lease_issuance_decision.get("human_capability_grant_ref") != \
       mission_capability_scope.get("human_capability_grant_id"):
        return {**base, "verdict": V_ISSUANCE_MISMATCH, "reason": "lidec_grant_ref"}

    # ── §10 : HumanCapabilityGrant OBLIGATOIRE + non substitué + non altéré ──
    if human_capability_grant is None:
        return {**base, "verdict": V_HUMAN_GRANT_INVALID, "reason": "human_capability_grant_not_supplied"}
    ok_g, why_g = _MCS.verify_human_capability_grant(
        human_capability_grant,
        human_capability_grant_authorization=human_capability_grant_authorization)
    if not ok_g:
        return {**base, "verdict": V_HUMAN_GRANT_INVALID, "reason": why_g}
    if human_capability_grant["human_capability_grant_id"] != \
       mission_capability_scope.get("human_capability_grant_id"):
        return {**base, "verdict": V_HUMAN_GRANT_MISMATCH, "reason": "grant_id"}
    if human_capability_grant["grant_record_hash"] != \
       mission_capability_scope.get("human_capability_grant_hash"):
        return {**base, "verdict": V_HUMAN_GRANT_MISMATCH, "reason": "grant_hash"}
    if human_capability_grant.get("mission_submission_id") != lease["mission_submission_id"]:
        return {**base, "verdict": V_HUMAN_GRANT_MISMATCH, "reason": "grant_submission"}
    if lease["lease_class"] not in human_capability_grant.get("allowed_lease_classes", []):
        return {**base, "verdict": V_LEASE_CLASS_NOT_IN_MISSION, "reason": "class_not_in_human_grant"}

    msc = mission_capability_scope["capability_scope"]
    gsc = human_capability_grant["capability_scope"]
    le_gm, extra_gm = scope_le(msc, gsc)          # MISSION ⊆ HUMAN_GRANT
    if not le_gm:
        return {**base, "verdict": V_HUMAN_GRANT_SCOPE_EXPANSION, "reason": extra_gm}
    le_rm, extra_rm = scope_le(rsc, msc)
    if not le_rm:
        return {**base, "verdict": V_REQUEST_SCOPE_EXCEEDS_MISSION, "reason": extra_rm}
    le_lm, extra_lm = scope_le(sc, msc)
    if not le_lm:
        return {**base, "verdict": V_SCOPE_EXPANSION, "reason": extra_lm}
    le_lg, extra_lg = scope_le(sc, gsc)           # LEASE ⊆ HUMAN_GRANT (défense explicite)
    if not le_lg:
        return {**base, "verdict": V_HUMAN_GRANT_SCOPE_EXPANSION, "reason": extra_lg}

    # Resserrement externe optionnel (jamais un élargissement).
    if authorized_capability_scope is not None:
        amsc, why_a = normalize_scope(authorized_capability_scope)
        if amsc is None:
            return {**base, "verdict": V_SCOPE_EXPANSION, "reason": f"authz_scope_invalid:{why_a}"}
        le_a, extra_a = scope_le(sc, amsc)
        if not le_a:
            return {**base, "verdict": V_SCOPE_EXPANSION, "reason": extra_a}

    return {**base, "verdict": V_VALID_INERT, "reason": None,
            "mission_capability_scope_binding": "ACTIVE",
            "human_capability_grant_binding": "VERIFIED_CONDITIONAL_ON_EXTERNAL_HUMAN_VERIFIER",
            "human_origin_proof_model": "EXTERNAL_TRUST_BOUNDARY",
            "note": "chaîne à 4 niveaux vérifiée (LEASE<=REQUEST<=MISSION<=HUMAN_GRANT ; "
                    "chemins/opérations <= HMA) ; origine humaine = frontière de confiance "
                    "externe (verifier hôte NON câblé ici) ; ENFORCEMENT INERTE ; aucun accès outil accordé"}


# ══════════════════════════════════════════════════════════════════════════
#  7 — CLI mince (diagnostic uniquement)
# ══════════════════════════════════════════════════════════════════════════

def _main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="obsidia_cognitive_capability_lease_v0",
                                 description="CG-C bail de capacité cognitive — RUNTIME INERTE")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)
    if a.self_check:
        print(json.dumps({
            "LEASE_RECORD_RUNTIME_IMPLEMENTED": LEASE_RECORD_RUNTIME_IMPLEMENTED,
            "LEASE_ENFORCEMENT_ACTIVE": LEASE_ENFORCEMENT_ACTIVE,
            "LEASE_GRANTS_TOOL_ACCESS": LEASE_GRANTS_TOOL_ACCESS,
            "HARD_TOOL_GATE_ACTIVE": HARD_TOOL_GATE_ACTIVE,
            "PRE_TOOL_LEASE_LOOKUP_ACTIVE": PRE_TOOL_LEASE_LOOKUP_ACTIVE,
            "COGNITIVE_CAPABILITY_LEASE_ACTIVE": COGNITIVE_CAPABILITY_LEASE_ACTIVE,
            "ENGINEERING_LEASE_ACTIVE": ENGINEERING_LEASE_ACTIVE,
            "CLAUDE_SELF_AUTHORIZES_ENGINEERING": CLAUDE_SELF_AUTHORIZES_ENGINEERING,
            "MISSION_CAPABILITY_SCOPE_BINDING": MISSION_CAPABILITY_SCOPE_BINDING,
            "lease_classes": list(_LEASE_CLASSES),
        }, indent=2))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
