#!/usr/bin/env python3
"""OBSIDIA CG-C2 — MissionCapabilityScope + LeaseIssuanceDecision : REPRÉSENTATION
RUNTIME CANONIQUE, ENTIÈREMENT INERTE.

Ce module ferme exactement deux liens manquants de CG-C :

  A. MISSION_CAPABILITY_SCOPE_BINDING   (borne supérieure de capacité cognitive
     autorisée par l'humain, liée à une mission exacte)
  B. LEASE_ISSUANCE_DECISION_AUTHORITY  (règle déterministe décidant s'il est
     structurellement/contextuellement permis de CRÉER un enregistrement de bail
     cognitif INERTE sous cette borne)

Invariant cible (devient une propriété runtime réellement vérifiée) :

  LEASE_CAPABILITY_SCOPE  <=  REQUESTED_CAPABILITY_SCOPE  <=  MISSION_ALLOWED_CAPABILITY_SCOPE

CG-C2 reste COMPLÈTEMENT INERTE :
  - N'accorde AUCUN accès outil (Edit/Write/Bash/Git/spawn/mutation FS).
  - N'active AUCUN enforcement pre-tool, AUCUN hard tool gate.
  - Ne délègue AUCUNE autorité d'exécution ni KX108_PRE.
  - `MissionCapabilityScope` et `LeaseIssuanceDecision` sont NON_SOVEREIGN.
  - Ne peut PAS être créé à partir d'une requête LLM seule NI d'une chaîne opaque :
    exige (1) une HMA Stage 4 vérifiée (racine humaine) ET (2) un
    `HumanCapabilityGrant` dérivé d'une `HumanCapabilityGrantAuthorization` VÉRIFIÉE
    par un `human_authorization_verifier` INJECTÉ par l'hôte, dont le
    `candidate_material_hash` == recalcul indépendant du matériel candidat exact.

FRONTIÈRE DE CONFIANCE (formulation VÉRIDIQUE — pas de surclamation) :
  CG-C2 DÉFINIT ET VÉRIFIE le CONTRAT de la frontière de confiance externe ; il
  n'instancie PAS lui-même la racine externe de vérification humaine.
    HUMAN_ORIGIN_PROOF_MODEL                          = EXTERNAL_TRUST_BOUNDARY
    HUMAN_AUTHORIZATION_VERIFIER_REQUIRED             = TRUE
    HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED = FALSE
    TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING          = NOT_YET_ENFORCED
    CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY          = NOT_YET_PROVEN
  Prouvé ici : aucun grant sans hash candidat exact approuvé par le vérificateur.
  NON prouvé ici : qui contrôle le vérificateur fourni par l'hôte. Le câblage
  d'une racine que Claude ne peut ni forger ni substituer est une PRÉCONDITION de
  l'enforcement CG-E, pas une restriction Claude déjà techniquement imposée.

Chaîne d'autorité (§11) :
  HUMAN AUTHORITY
    ├─ HumanMissionAuthorization (HMA Stage 4) → mission / plan / target paths / operation shapes
    └─ HumanCapabilityGrant (issued_by=HUMAN)  → capacités COGNITIVES (lease classes,
                                                 providers, tools, read/write/test/git scope)
                     ↓
           MissionCapabilityScope   (≤ HMA sur paths/ops ; ≤ HumanCapabilityGrant sur le cognitif)
                     ↓
              CapabilityRequest
                     ↓
           LeaseIssuanceDecision
                     ↓
                   Lease
  Invariant : LEASE ≤ REQUESTED ≤ MISSION_CAPABILITY_SCOPE ≤ HUMAN_CAPABILITY_GRANT_SCOPE
              (dimensions chemin/opération additionnellement bornées par la HMA vérifiée).

GEL STAGE 4 : ce module N'IMPORTE PAS le runtime d'autorité de mission Stage 4.
Le vérificateur d'HMA canonique est INJECTÉ par l'appelant sous forme de callable
`hma_verifier(hma) -> (bool, reason)` (fail-closed `HMA_VERIFIER_REQUIRED` s'il est
absent). Aucune sémantique d'autorité Stage 4 n'est réimplémentée ici.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_cognitive_capability_lease_v0 as _CCL   # CG-C (schémas de portée + helpers)
import obsidia_gateway_route_decision_v0 as _RD        # CG-B (RouteDecision + store)

SCHEMA_VERSION = 1
HCG_DOMAIN_TAG = "OBSIDIA_CGC2_HUMAN_CAPABILITY_GRANT_V0"
MCS_DOMAIN_TAG = "OBSIDIA_CGC2_MISSION_CAPABILITY_SCOPE_V0"
LIDEC_DOMAIN_TAG = "OBSIDIA_CGC2_LEASE_ISSUANCE_DECISION_V0"
DECISION_AUTHORITY = "KX108_ONLY"

# ── Bornes d'inertie explicites ──────────────────────────────────────────
MISSION_CAPABILITY_SCOPE_RUNTIME = "IMPLEMENTED_INERT_V0"
LEASE_ISSUANCE_DECISION_RUNTIME = "IMPLEMENTED_INERT_V0"
MISSION_CAPABILITY_SCOPE_BINDING = "ACTIVE"
LEASE_ISSUANCE_DECISION_RULE = "ACTIVE_INERT"
LEASE_TO_MISSION_SCOPE_RUNTIME_CHECK = "ACTIVE"
REQUEST_TO_MISSION_SCOPE_CHECK = "ACTIVE"
LEASE_TO_REQUEST_SCOPE_CHECK = "ACTIVE"

MISSION_CAPABILITY_SCOPE_IS_EXECUTION_AUTHORITY = False
MISSION_CAPABILITY_SCOPE_IS_KX_AUTHORITY = False
MISSION_CAPABILITY_SCOPE_IS_SOVEREIGN = False
LEASE_ISSUANCE_DECISION_IS_EXECUTION_AUTHORITY = False
LEASE_ISSUANCE_DECISION_IS_KX_AUTHORITY = False
LEASE_ISSUANCE_DECISION_IS_SOVEREIGN = False

MISSION_CAPABILITY_SCOPE_CAN_BE_CREATED_FROM_CLAUDE_REQUEST_ALONE = False
MISSION_CAPABILITY_SCOPE_CAN_BE_CREATED_FROM_ROUTE_DECISION_ALONE = False
MISSION_CAPABILITY_SCOPE_CAN_BE_CREATED_FROM_CAPABILITY_REQUEST_ALONE = False

LEASE_GRANTS_TOOL_ACCESS = False
LEASE_ENFORCEMENT_ACTIVE = False
PRE_TOOL_LEASE_LOOKUP_ACTIVE = False
HARD_TOOL_GATE_ACTIVE = False
CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED = False
CLAUDE_SELF_AUTHORIZES_ENGINEERING = False
CAPABILITY_REQUEST_IS_AUTHORITY = False
CAPABILITY_REQUEST_CAN_EXPAND_MISSION_SCOPE = False
DEFAULT_MISSION_CAPABILITY_SCOPE = "EMPTY_NOT_ALL"
DEFAULT_HUMAN_CAPABILITY_GRANT_SCOPE = "EMPTY_NOT_ALL"
HUMAN_CAPABILITY_GRANT_VERIFICATION = "ACTIVE"
HUMAN_CAPABILITY_GRANT_AUTHORIZATION_VERIFICATION = "ACTIVE"
# ── Frontière de confiance externe (formulation VÉRIDIQUE) ──────────────
#  CG-C2 DÉFINIT ET VÉRIFIE le CONTRAT de la frontière de confiance ; il
#  n'instancie PAS lui-même la racine externe de vérification humaine. Un
#  grant ne peut pas être créé sans un `human_authorization_verifier`
#  approuvant le hash exact du matériel candidat — MAIS CG-C2 ne prouve pas
#  qui contrôle ce vérificateur fourni par l'hôte.
HUMAN_CAPABILITY_GRANT_ORIGIN_SELF_ASSERTED = False
HUMAN_AUTHORIZATION_VERIFIER_REQUIRED = True
HUMAN_AUTHORIZATION_VERIFIER_CALLABLE_REQUIRED = True
HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED = False
HUMAN_ORIGIN_PROOF_MODEL = "EXTERNAL_TRUST_BOUNDARY"
TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = "NOT_YET_ENFORCED"
CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY = "NOT_YET_PROVEN"
HUMAN_COGNITIVE_CAPABILITY_GRANT_BINDING = "VERIFIED_CONDITIONAL_ON_EXTERNAL_HUMAN_VERIFIER"
CG_D_SHADOW_MAY_PROCEED_WITH_EXTERNAL_TRUST_BOUNDARY_UNWIRED = True
CG_E_ACTIVE_ENFORCEMENT_REQUIRES_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = True
PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = "OPEN"
MAX_GOVERNED_MUTATION_OPERATION_V0 = _CCL.MAX_GOVERNED_MUTATION_OPERATION_V0
MULTI_OPERATION_GENERALIZATION = "NOT_YET_PROVEN"

# ── Issuers ────────────────────────────────────────────────────────────
ISSUER_GATEWAY_CAPABILITY_DECISION = _CCL.ISSUER_GATEWAY_CAPABILITY_DECISION
_AUTHORIZED_ISSUERS = _CCL._AUTHORIZED_ISSUERS
_FORBIDDEN_ISSUERS = _CCL._FORBIDDEN_ISSUERS
# Un HumanCapabilityGrant N'EST délivré QUE par l'humain.
HCG_ISSUER_HUMAN = "HUMAN"
_HCG_FORBIDDEN_ISSUERS = ("CLAUDE", "BRODY", "OBSIDURE", ISSUER_GATEWAY_CAPABILITY_DECISION,
                          "GATEWAY", "OBSIDIA_GATEWAY", "STACK")

HCGA_DOMAIN_TAG = "OBSIDIA_CGC2_HUMAN_CAPABILITY_GRANT_AUTHORIZATION_V0"

# ── Statuts / verdicts ─────────────────────────────────────────────────
STATUS_HCGA_ACTIVE = "HUMAN_CAPABILITY_GRANT_AUTHORIZATION_ACTIVE"
STATUS_HCGA_REJECTED = "HUMAN_CAPABILITY_GRANT_AUTHORIZATION_REJECTED"
STATUS_HCG_ACTIVE = "HUMAN_CAPABILITY_GRANT_ACTIVE"
STATUS_HCG_REJECTED = "HUMAN_CAPABILITY_GRANT_REJECTED"
STATUS_MCS_ACTIVE_INERT = "MISSION_CAPABILITY_SCOPE_ACTIVE_INERT"
STATUS_MCS_REJECTED = "MISSION_CAPABILITY_SCOPE_REJECTED"

# LeaseIssuanceDecision — sorties canoniques (§12)
LEASE_ELIGIBLE_INERT = "LEASE_ELIGIBLE_INERT"
LEASE_DENIED_SCOPE = "LEASE_DENIED_SCOPE"
LEASE_DENIED_ROUTE = "LEASE_DENIED_ROUTE"
LEASE_DENIED_MISSION_STATE = "LEASE_DENIED_MISSION_STATE"
LEASE_DENIED_REQUEST_MISMATCH = "LEASE_DENIED_REQUEST_MISMATCH"
LEASE_DENIED_AUTHORITY_GAP = "LEASE_DENIED_AUTHORITY_GAP"
LEASE_DENIED_UNKNOWN = "LEASE_DENIED_UNKNOWN"
LEASE_DENIED_ISSUER = "LEASE_DENIED_ISSUER"
LEASE_HOLD_MISSION_SCOPE_MISSING = "LEASE_HOLD_MISSION_SCOPE_MISSING"
LEASE_HOLD_HUMAN_AUTHORITY_REQUIRED = "LEASE_HOLD_HUMAN_AUTHORITY_REQUIRED"
LEASE_HOLD_HUMAN_CAPABILITY_GRANT_MISSING = "LEASE_HOLD_HUMAN_CAPABILITY_GRANT_MISSING"

_ELIGIBLE = LEASE_ELIGIBLE_INERT

_canon = _CCL._canon
_sha = _CCL._sha
_now = _CCL._now
_normalize_scope = _CCL.normalize_scope
_scope_le = _CCL.scope_le
_empty_scope = _CCL.empty_scope
_LEASE_CLASSES = _CCL._LEASE_CLASSES
_CLASS_TO_ROUTE = _CCL._CLASS_TO_ROUTE
_NO_LEASE_ROUTES = _CCL._NO_LEASE_ROUTES


def _mcs_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "mission_capability_scopes"


def _lidec_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "lease_issuance_decisions"


def _reject(status: str, reason: str, **extra) -> dict:
    return {"status": status, "reason": reason, "record": None,
            "grants_tool_access": False, "is_execution_authority": False,
            "is_kx_authority": False, "is_sovereign": False, **extra}


# ══════════════════════════════════════════════════════════════════════════
#  1 — MissionCapabilityScope (borne supérieure, humaine, liée à la mission)
# ══════════════════════════════════════════════════════════════════════════

_MCS_BOUND_FIELDS = (
    "schema_version", "domain_tag",
    "mission_submission_id", "mission_id",
    "hma_id", "hma_record_hash", "mission_genesis_record_hash",
    "plan_id", "plan_hash",
    "human_authorization_reference",
    "human_capability_grant_id", "human_capability_grant_hash",
    "allowed_lease_classes", "capability_scope",
    "status", "issued_by", "issuer_ref",
    "is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access",
)


def _hma_target_paths(hma: dict):
    return (hma or {}).get("allowed_target_paths")


def _hma_operation_shapes(hma: dict):
    return (hma or {}).get("allowed_operation_shapes")


def _run_hma_verifier(hma, hma_verifier) -> "tuple[bool, Optional[str]]":
    """Exécute le vérificateur d'HMA canonique INJECTÉ par l'appelant.
    GEL STAGE 4 : ce module n'importe ni ne réimplémente la vérification d'HMA."""
    if not callable(hma_verifier):
        return False, "HMA_VERIFIER_REQUIRED"
    if not isinstance(hma, dict):
        return False, "HMA_RECORD_MISSING"
    try:
        res = hma_verifier(hma)
    except Exception as exc:                       # fail-closed
        return False, f"HMA_VERIFIER_RAISED:{type(exc).__name__}"
    if isinstance(res, tuple):
        ok = bool(res[0]); why = (res[1] if len(res) > 1 else None)
    else:
        ok = bool(res); why = None
    if not ok:
        return False, f"HMA_REJECTED:{why}"
    # garde-fous structurels minimaux, indépendants du vérificateur
    if hma.get("issuer") != "HUMAN":
        return False, "HMA_ISSUER_NOT_HUMAN"
    if not str(hma.get("human_mission_authorization_id", "")).startswith("hma-"):
        return False, "HMA_ID_MALFORMED"
    for f in ("hma_record_hash", "human_authorization_reference", "mission_id", "plan_hash",
              "mission_genesis_record_hash", "plan_id"):
        if not (isinstance(hma.get(f), str) and hma.get(f)):
            return False, f"HMA_FIELD_MISSING:{f}"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  0a — HumanCapabilityGrantAuthorization (preuve d'origine humaine)
# ══════════════════════════════════════════════════════════════════════════
#
#  Ferme la distinction : CONTENU_VALIDE  vs  RÉELLEMENT_AUTORISÉ_PAR_L'HUMAIN.
#  `issued_by="HUMAN"` + une chaîne opaque NE constituent PAS une preuve. La
#  preuve = un artefact vérifié via un `human_authorization_verifier` INJECTÉ
#  par l'hôte (frontière externe : confirmation terminale, reçu signé, EAH
#  d'une HumanApproval canonique, …). CG-C2 ne DÉCIDE JAMAIS l'humanité — il
#  délègue à ce vérificateur, recalcule INDÉPENDAMMENT le hash du matériel
#  candidat, et refuse toute création si l'autorisation ne couvre pas ce hash.
#
#  HumanCapabilityGrantAuthorization != ExecutionAuthority != KX. NON_SOVEREIGN.

_CANDIDATE_MATERIAL_FIELDS = (
    "mission_id", "mission_submission_id", "hma_id", "hma_record_hash",
    "human_authorization_reference", "allowed_lease_classes", "capability_scope",
)
_HCGA_BOUND_FIELDS = (
    "schema_version", "domain_tag",
    "mission_id", "mission_submission_id", "hma_id", "hma_record_hash",
    "candidate_material_hash", "human_decision_ref", "approved_by", "status",
    "is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access",
)


def _hcga_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "human_capability_grant_authorizations"


def _candidate_material(*, hma: dict, mission_submission_id: str,
                        allowed_lease_classes, capability_scope: dict) -> dict:
    return {
        "mission_id": hma["mission_id"],
        "mission_submission_id": mission_submission_id,
        "hma_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "human_authorization_reference": hma["human_authorization_reference"],
        "allowed_lease_classes": sorted(set(allowed_lease_classes)),
        "capability_scope": capability_scope,
    }


def _candidate_material_hash(material: dict) -> str:
    return _sha(_canon({k: material.get(k) for k in _CANDIDATE_MATERIAL_FIELDS}))


def _run_human_authorization_verifier(payload, verifier) -> "tuple[bool, Optional[str]]":
    """Exécute le vérificateur d'autorisation humaine INJECTÉ (frontière hôte).
    CG-C2 ne réimplémente ni ne présume l'origine humaine."""
    if not callable(verifier):
        return False, "HUMAN_AUTHORIZATION_VERIFIER_REQUIRED"
    try:
        res = verifier(payload)
    except Exception as exc:
        return False, f"HUMAN_AUTHORIZATION_VERIFIER_RAISED:{type(exc).__name__}"
    if isinstance(res, tuple):
        ok = bool(res[0]); why = (res[1] if len(res) > 1 else None)
    else:
        ok = bool(res); why = None
    return (True, None) if ok else (False, f"HUMAN_AUTHORIZATION_REJECTED:{why}")


def prepare_human_capability_grant_authorization(
    *, hma: dict, hma_verifier,
    mission_submission_id: str,
    allowed_lease_classes,
    capability_scope: Optional[dict],
    human_decision_ref: str,
    human_authorization_verifier,
) -> dict:
    """Construit (SANS persister) une HumanCapabilityGrantAuthorization : la preuve
    que l'humain a autorisé EXACTEMENT ce matériel candidat (mission/HMA + classes
    de bail + portée cognitive). L'origine humaine est établie par le
    `human_authorization_verifier` INJECTÉ, jamais présumée."""
    ok_h, why_h = _run_hma_verifier(hma, hma_verifier)
    if not ok_h:
        return _reject(STATUS_HCGA_REJECTED, f"HMA_INVALID:{why_h}")
    if not (isinstance(mission_submission_id, str) and mission_submission_id.startswith("gsub-")):
        return _reject(STATUS_HCGA_REJECTED, "MISSION_SUBMISSION_ID_INVALID")
    if not (isinstance(human_decision_ref, str) and human_decision_ref.strip()):
        return _reject(STATUS_HCGA_REJECTED, "HUMAN_DECISION_REF_REQUIRED")
    if not (isinstance(allowed_lease_classes, (list, tuple))
            and all(isinstance(c, str) for c in allowed_lease_classes) and allowed_lease_classes):
        return _reject(STATUS_HCGA_REJECTED, "ALLOWED_LEASE_CLASSES_NOT_NONEMPTY_STR_LIST")
    for c in allowed_lease_classes:
        if c not in _LEASE_CLASSES:
            return _reject(STATUS_HCGA_REJECTED, f"UNKNOWN_LEASE_CLASS:{c}")
    scope, why_s = _normalize_scope(capability_scope)
    if scope is None:
        return _reject(STATUS_HCGA_REJECTED, f"CAPABILITY_SCOPE_INVALID:{why_s}")

    material = _candidate_material(hma=hma, mission_submission_id=mission_submission_id,
                                  allowed_lease_classes=allowed_lease_classes,
                                  capability_scope=scope)
    cmh = _candidate_material_hash(material)

    ok_a, why_a = _run_human_authorization_verifier(
        {"candidate_material": material, "candidate_material_hash": cmh,
         "human_decision_ref": human_decision_ref}, human_authorization_verifier)
    if not ok_a:
        return _reject(STATUS_HCGA_REJECTED, f"HCGA_HUMAN_AUTHORIZATION_UNVERIFIED:{why_a}")

    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": HCGA_DOMAIN_TAG,
        "mission_id": hma["mission_id"],
        "mission_submission_id": mission_submission_id,
        "hma_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "candidate_material_hash": cmh,
        "human_decision_ref": human_decision_ref[:400],
        "approved_by": HCG_ISSUER_HUMAN,
        "status": STATUS_HCGA_ACTIVE,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
    }
    rh = _sha(_canon({k: core.get(k) for k in _HCGA_BOUND_FIELDS}))
    core["authorization_record_hash"] = rh
    core["human_capability_grant_authorization_id"] = "hcga-" + rh[:32]
    core["created_at"] = _now()
    core["decision_authority"] = DECISION_AUTHORITY
    return {"status": STATUS_HCGA_ACTIVE, "reason": None, "record": core,
            "grants_tool_access": False}


def build_human_capability_grant_authorization(**kw) -> Optional[dict]:
    return prepare_human_capability_grant_authorization(**kw).get("record")


def verify_human_capability_grant_authorization(
    hcga: Optional[dict], *, expected_candidate_material_hash: Optional[str] = None,
) -> "tuple[bool, Optional[str]]":
    if not isinstance(hcga, dict):
        return False, "HCGA_MISSING"
    if hcga.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if hcga.get("domain_tag") != HCGA_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if hcga.get("approved_by") != HCG_ISSUER_HUMAN:
        return False, f"HCGA_APPROVED_BY_NOT_HUMAN:{hcga.get('approved_by')}"
    for b in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        if hcga.get(b) is not False:
            return False, f"HCGA_CLAIMS_AUTHORITY:{b}"
    for ref, pfx in (("human_capability_grant_authorization_id", "hcga-"),
                     ("hma_id", "hma-"), ("mission_submission_id", "gsub-")):
        if not str(hcga.get(ref, "")).startswith(pfx):
            return False, f"REF_MALFORMED:{ref}"
    for ref in ("mission_id", "hma_record_hash", "candidate_material_hash",
                "human_decision_ref", "authorization_record_hash"):
        if not (isinstance(hcga.get(ref), str) and hcga.get(ref)):
            return False, f"MISSING_REF:{ref}"
    if hcga.get("status") != STATUS_HCGA_ACTIVE:
        return False, "STATUS_INVALID"
    rh = _sha(_canon({k: hcga.get(k) for k in _HCGA_BOUND_FIELDS}))
    if hcga.get("authorization_record_hash") != rh:
        return False, "HCGA_RECORD_HASH_MISMATCH"
    if hcga.get("human_capability_grant_authorization_id") != "hcga-" + rh[:32]:
        return False, "HCGA_ID_NOT_DERIVED"
    if expected_candidate_material_hash is not None and \
       hcga.get("candidate_material_hash") != expected_candidate_material_hash:
        return False, "HCGA_CANDIDATE_MATERIAL_HASH_MISMATCH"
    return True, None


def persist_human_capability_grant_authorization(hcga: dict, store_dir=None) -> dict:
    ok, why = verify_human_capability_grant_authorization(hcga)
    if not ok:
        return {"status": "HCGA_PERSIST_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _hcga_store(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{hcga['human_capability_grant_authorization_id']}.json"
    payload = json.dumps(hcga, indent=2, sort_keys=True) + "\n"
    if p.exists():
        if p.read_text(encoding="utf-8") == payload:
            return {"status": "IDEMPOTENT_ALREADY_EXISTS"}
        return {"status": "HCGA_IMMUTABILITY_VIOLATION", "divergent_hcga_rewrite": "FAIL_CLOSED"}
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(p)
    return {"status": "STORED",
            "human_capability_grant_authorization_id": hcga["human_capability_grant_authorization_id"]}


def load_human_capability_grant_authorization(hcga_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(hcga_id, str) and hcga_id.startswith("hcga-")):
        return None
    p = _hcga_store(store_dir) / f"{hcga_id}.json"
    if not p.is_file():
        return None
    try:
        hcga = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ok, _ = verify_human_capability_grant_authorization(hcga)
    return hcga if ok else None


# ══════════════════════════════════════════════════════════════════════════
#  0b — HumanCapabilityGrant (borne supérieure de capacité COGNITIVE, humaine)
# ══════════════════════════════════════════════════════════════════════════
#
#  N'EST créé QUE si une HumanCapabilityGrantAuthorization VÉRIFIÉE couvre
#  EXACTEMENT le matériel candidat (hash recalculé indépendamment). `issued_by`
#  n'est plus un paramètre : il est forcé "HUMAN" APRÈS la preuve d'origine.

_HCG_BOUND_FIELDS = (
    "schema_version", "domain_tag",
    "mission_id", "mission_submission_id",
    "hma_id", "hma_record_hash", "human_authorization_reference",
    "human_capability_grant_authorization_id", "human_capability_grant_authorization_hash",
    "candidate_material_hash",
    "allowed_lease_classes", "capability_scope",
    "issued_by", "status",
    "is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access",
)


def _hcg_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "human_capability_grants"


def prepare_human_capability_grant(
    *, hma: dict, hma_verifier,
    human_capability_grant_authorization: dict,
    mission_submission_id: str,
    allowed_lease_classes,
    capability_scope: Optional[dict] = None,
) -> dict:
    """Construit (SANS persister) un HumanCapabilityGrant INERTE, ou rejette
    fail-closed. Exige (1) une HMA Stage 4 VÉRIFIÉE ET (2) une
    HumanCapabilityGrantAuthorization VÉRIFIÉE dont `candidate_material_hash`
    correspond EXACTEMENT au matériel demandé (recalcul indépendant). Aucun
    paramètre `issued_by` : l'origine humaine n'est jamais auto-attestée."""
    ok_h, why_h = _run_hma_verifier(hma, hma_verifier)
    if not ok_h:
        return _reject(STATUS_HCG_REJECTED, f"HMA_INVALID:{why_h}")
    if not (isinstance(mission_submission_id, str) and mission_submission_id.startswith("gsub-")):
        return _reject(STATUS_HCG_REJECTED, "MISSION_SUBMISSION_ID_INVALID")
    if not (isinstance(allowed_lease_classes, (list, tuple))
            and all(isinstance(c, str) for c in allowed_lease_classes) and allowed_lease_classes):
        return _reject(STATUS_HCG_REJECTED, "ALLOWED_LEASE_CLASSES_NOT_NONEMPTY_STR_LIST")
    alc = sorted(set(allowed_lease_classes))
    for c in alc:
        if c not in _LEASE_CLASSES:
            return _reject(STATUS_HCG_REJECTED, f"UNKNOWN_LEASE_CLASS:{c}")
    scope, why_s = _normalize_scope(capability_scope)
    if scope is None:
        return _reject(STATUS_HCG_REJECTED, f"CAPABILITY_SCOPE_INVALID:{why_s}")

    hp = _hma_target_paths(hma)
    if isinstance(hp, list) and not (set(scope["allowed_paths"]) <= set(hp)):
        return _reject(STATUS_HCG_REJECTED,
                       f"GRANT_PATHS_EXCEED_HMA_TARGET_PATHS:{sorted(set(scope['allowed_paths']) - set(hp))}")
    ho = _hma_operation_shapes(hma)
    if isinstance(ho, list) and not (set(scope["allowed_operations"]) <= set(ho)):
        return _reject(STATUS_HCG_REJECTED,
                       f"GRANT_OPERATIONS_EXCEED_HMA_OPERATION_SHAPES:{sorted(set(scope['allowed_operations']) - set(ho))}")

    # ── Preuve d'origine humaine : recalcul INDÉPENDANT du hash candidat ──
    material = _candidate_material(hma=hma, mission_submission_id=mission_submission_id,
                                  allowed_lease_classes=alc, capability_scope=scope)
    cmh = _candidate_material_hash(material)
    ok_a, why_a = verify_human_capability_grant_authorization(
        human_capability_grant_authorization, expected_candidate_material_hash=cmh)
    if not ok_a:
        return _reject(STATUS_HCG_REJECTED, f"HCG_HUMAN_AUTHORIZATION_UNVERIFIED:{why_a}")
    a = human_capability_grant_authorization
    if a.get("mission_id") != hma["mission_id"] or \
       a.get("hma_id") != hma["human_mission_authorization_id"] or \
       a.get("hma_record_hash") != hma["hma_record_hash"] or \
       a.get("mission_submission_id") != mission_submission_id:
        return _reject(STATUS_HCG_REJECTED, "HCG_HUMAN_AUTHORIZATION_BINDING_MISMATCH")

    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": HCG_DOMAIN_TAG,
        "mission_id": hma["mission_id"],
        "mission_submission_id": mission_submission_id,
        "hma_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "human_authorization_reference": hma["human_authorization_reference"],
        "human_capability_grant_authorization_id": a["human_capability_grant_authorization_id"],
        "human_capability_grant_authorization_hash": a["authorization_record_hash"],
        "candidate_material_hash": cmh,
        "allowed_lease_classes": alc,
        "capability_scope": scope,
        "issued_by": HCG_ISSUER_HUMAN,
        "status": STATUS_HCG_ACTIVE,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
    }
    rh = _sha(_canon({k: core.get(k) for k in _HCG_BOUND_FIELDS}))
    core["grant_record_hash"] = rh
    core["human_capability_grant_id"] = "hcg-" + rh[:32]
    core["created_at"] = _now()
    core["decision_authority"] = DECISION_AUTHORITY
    return {"status": STATUS_HCG_ACTIVE, "reason": None, "record": core,
            "grants_tool_access": False}


def build_human_capability_grant(**kw) -> Optional[dict]:
    out = prepare_human_capability_grant(**kw)
    return out.get("record")


def verify_human_capability_grant(
    grant: Optional[dict], *, hma: Optional[dict] = None, hma_verifier=None,
    human_capability_grant_authorization: Optional[dict] = None,
) -> "tuple[bool, Optional[str]]":
    """Vérificateur déterministe. Une chaîne arbitraire NE peut PAS satisfaire
    ceci. Si `hma`+`hma_verifier` fournis → revérifie la lignée HMA. Si
    `human_capability_grant_authorization` fourni → revérifie la preuve d'origine
    humaine + le hash du matériel candidat recalculé depuis les champs du grant."""
    if not isinstance(grant, dict):
        return False, "HCG_MISSING"
    if grant.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if grant.get("domain_tag") != HCG_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if grant.get("issued_by") != HCG_ISSUER_HUMAN:
        return False, f"HCG_ISSUER_NOT_HUMAN:{grant.get('issued_by')}"
    for b in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        if grant.get(b) is not False:
            return False, f"HCG_CLAIMS_AUTHORITY:{b}"
    for ref, pfx in (("human_capability_grant_id", "hcg-"), ("hma_id", "hma-"),
                     ("mission_submission_id", "gsub-"),
                     ("human_capability_grant_authorization_id", "hcga-")):
        if not str(grant.get(ref, "")).startswith(pfx):
            return False, f"REF_MALFORMED:{ref}"
    for ref in ("mission_id", "hma_record_hash", "human_authorization_reference",
                "human_capability_grant_authorization_hash", "candidate_material_hash",
                "grant_record_hash"):
        if not (isinstance(grant.get(ref), str) and grant.get(ref)):
            return False, f"MISSING_REF:{ref}"
    alc = grant.get("allowed_lease_classes")
    if not (isinstance(alc, list) and alc and all(c in _LEASE_CLASSES for c in alc)
            and alc == sorted(set(alc))):
        return False, "ALLOWED_LEASE_CLASSES_INVALID"
    if grant.get("status") != STATUS_HCG_ACTIVE:
        return False, "STATUS_INVALID"
    sc, why = _normalize_scope(grant.get("capability_scope"))
    if sc is None or sc != grant.get("capability_scope"):
        return False, f"CAPABILITY_SCOPE_INVALID:{why}"
    rh = _sha(_canon({k: grant.get(k) for k in _HCG_BOUND_FIELDS}))
    if grant.get("grant_record_hash") != rh:
        return False, "GRANT_RECORD_HASH_MISMATCH"
    if grant.get("human_capability_grant_id") != "hcg-" + rh[:32]:
        return False, "HCG_ID_NOT_DERIVED"
    # matériel candidat recalculé depuis les champs mêmes du grant
    self_material = {
        "mission_id": grant.get("mission_id"),
        "mission_submission_id": grant.get("mission_submission_id"),
        "hma_id": grant.get("hma_id"),
        "hma_record_hash": grant.get("hma_record_hash"),
        "human_authorization_reference": grant.get("human_authorization_reference"),
        "allowed_lease_classes": alc,
        "capability_scope": sc,
    }
    if grant.get("candidate_material_hash") != _candidate_material_hash(self_material):
        return False, "CANDIDATE_MATERIAL_HASH_MISMATCH"
    if hma is not None or hma_verifier is not None:
        ok_h, why_h = _run_hma_verifier(hma, hma_verifier)
        if not ok_h:
            return False, f"HMA_INVALID:{why_h}"
        if grant.get("hma_id") != hma.get("human_mission_authorization_id"):
            return False, "HCG_HMA_ID_MISMATCH"
        if grant.get("hma_record_hash") != hma.get("hma_record_hash"):
            return False, "HCG_HMA_HASH_MISMATCH"
        if grant.get("mission_id") != hma.get("mission_id"):
            return False, "HCG_MISSION_ID_MISMATCH"
        if grant.get("human_authorization_reference") != hma.get("human_authorization_reference"):
            return False, "HCG_HUMAN_AUTHORIZATION_REFERENCE_MISMATCH"
    if human_capability_grant_authorization is not None:
        ok_a, why_a = verify_human_capability_grant_authorization(
            human_capability_grant_authorization,
            expected_candidate_material_hash=grant.get("candidate_material_hash"))
        if not ok_a:
            return False, f"HUMAN_AUTHORIZATION_INVALID:{why_a}"
        if human_capability_grant_authorization.get("human_capability_grant_authorization_id") != \
           grant.get("human_capability_grant_authorization_id"):
            return False, "HCG_AUTHORIZATION_ID_MISMATCH"
        if human_capability_grant_authorization.get("authorization_record_hash") != \
           grant.get("human_capability_grant_authorization_hash"):
            return False, "HCG_AUTHORIZATION_HASH_MISMATCH"
    return True, None


def persist_human_capability_grant(grant: dict, store_dir=None) -> dict:
    ok, why = verify_human_capability_grant(grant)
    if not ok:
        return {"status": "HCG_PERSIST_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _hcg_store(store_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "HCG_PERSIST_REJECTED", "reason": f"MKDIR:{exc}"}
    p = d / f"{grant['human_capability_grant_id']}.json"
    payload = json.dumps(grant, indent=2, sort_keys=True) + "\n"
    if p.exists():
        try:
            existing = p.read_text(encoding="utf-8")
        except OSError as exc:
            return {"status": "HCG_PERSIST_REJECTED", "reason": f"READ:{exc}"}
        if existing == payload:
            return {"status": "IDEMPOTENT_ALREADY_EXISTS",
                    "human_capability_grant_id": grant["human_capability_grant_id"]}
        return {"status": "HCG_IMMUTABILITY_VIOLATION",
                "human_capability_grant_id": grant["human_capability_grant_id"],
                "divergent_hcg_rewrite": "FAIL_CLOSED"}
    tmp = p.with_suffix(".json.tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(p)
    except OSError as exc:
        return {"status": "HCG_PERSIST_REJECTED", "reason": f"WRITE:{exc}"}
    return {"status": "STORED", "human_capability_grant_id": grant["human_capability_grant_id"]}


def load_human_capability_grant(hcg_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(hcg_id, str) and hcg_id.startswith("hcg-")):
        return None
    p = _hcg_store(store_dir) / f"{hcg_id}.json"
    if not p.is_file():
        return None
    try:
        grant = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ok, _ = verify_human_capability_grant(grant)
    return grant if ok else None


def prepare_mission_capability_scope(
    *, hma: dict,
    hma_verifier,
    human_capability_grant: dict,
    mission_submission_id: str,
    allowed_lease_classes,
    capability_scope: Optional[dict] = None,
    issued_by: str = ISSUER_GATEWAY_CAPABILITY_DECISION,
    issuer_ref: Optional[str] = None,
) -> dict:
    """Construit (SANS persister) une MissionCapabilityScope INERTE, ou rejette
    fail-closed. Exige (1) une HMA Stage 4 VÉRIFIÉE via `hma_verifier` (racine
    humaine, chemins/opérations) ET (2) un `HumanCapabilityGrant` VÉRIFIÉ (borne
    supérieure des dimensions COGNITIVES : classes de bail, providers, tools,
    read/write/test/git scope). Une chaîne opaque N'EST PLUS acceptée.
    La MCS lie par hash `human_capability_grant_id` + `human_capability_grant_hash`."""
    if issued_by in _FORBIDDEN_ISSUERS or issued_by not in _AUTHORIZED_ISSUERS:
        return _reject(STATUS_MCS_REJECTED, f"ISSUER_NOT_AUTHORIZED:{issued_by}")

    # ── (1) Lignée humaine racine : HMA Stage 4 canonique INJECTÉE ──
    ok_h, why_h = _run_hma_verifier(hma, hma_verifier)
    if not ok_h:
        return _reject(STATUS_MCS_REJECTED, f"HMA_INVALID:{why_h}")
    if hma.get("issuer") != "HUMAN":
        return _reject(STATUS_MCS_REJECTED, "HMA_ISSUER_NOT_HUMAN")

    # ── (2) Octroi humain de capacité cognitive : VÉRIFIÉ + chaîné à la HMA ──
    ok_g, why_g = verify_human_capability_grant(human_capability_grant, hma=hma, hma_verifier=hma_verifier)
    if not ok_g:
        return _reject(STATUS_MCS_REJECTED, f"HUMAN_CAPABILITY_GRANT_INVALID:{why_g}")

    if not (isinstance(mission_submission_id, str) and mission_submission_id.startswith("gsub-")):
        return _reject(STATUS_MCS_REJECTED, "MISSION_SUBMISSION_ID_INVALID")
    if human_capability_grant.get("mission_submission_id") != mission_submission_id:
        return _reject(STATUS_MCS_REJECTED, "GRANT_MISSION_SUBMISSION_MISMATCH")

    if not (isinstance(allowed_lease_classes, (list, tuple))
            and all(isinstance(c, str) for c in allowed_lease_classes)):
        return _reject(STATUS_MCS_REJECTED, "ALLOWED_LEASE_CLASSES_NOT_STR_LIST")
    alc = sorted(set(allowed_lease_classes))
    for c in alc:
        if c not in _LEASE_CLASSES:
            return _reject(STATUS_MCS_REJECTED, f"UNKNOWN_LEASE_CLASS:{c}")
    # §5 : MCS.allowed_lease_classes ⊆ GRANT.allowed_lease_classes
    if not (set(alc) <= set(human_capability_grant["allowed_lease_classes"])):
        return _reject(STATUS_MCS_REJECTED,
                       f"MCS_LEASE_CLASSES_EXCEED_HUMAN_GRANT:{sorted(set(alc) - set(human_capability_grant['allowed_lease_classes']))}")

    scope, why_s = _normalize_scope(capability_scope)
    if scope is None:
        return _reject(STATUS_MCS_REJECTED, f"CAPABILITY_SCOPE_INVALID:{why_s}")

    # ── Bornage par la HMA humaine (chemins / opérations) ──
    hma_paths = _hma_target_paths(hma)
    if isinstance(hma_paths, list) and not (set(scope["allowed_paths"]) <= set(hma_paths)):
        extra = sorted(set(scope["allowed_paths"]) - set(hma_paths))
        return _reject(STATUS_MCS_REJECTED, f"CAPABILITY_PATHS_EXCEED_HMA_TARGET_PATHS:{extra}")
    hma_ops = _hma_operation_shapes(hma)
    if isinstance(hma_ops, list) and not (set(scope["allowed_operations"]) <= set(hma_ops)):
        extra = sorted(set(scope["allowed_operations"]) - set(hma_ops))
        return _reject(STATUS_MCS_REJECTED, f"CAPABILITY_OPERATIONS_EXCEED_HMA_OPERATION_SHAPES:{extra}")

    # ── §5 : MCS.capability_scope ⊆ GRANT.capability_scope ──
    le_g, extra_g = _scope_le(scope, human_capability_grant["capability_scope"])
    if not le_g:
        return _reject(STATUS_MCS_REJECTED, f"MCS_CAPABILITY_SCOPE_EXCEEDS_HUMAN_GRANT:{extra_g}")

    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": MCS_DOMAIN_TAG,
        "mission_submission_id": mission_submission_id,
        "mission_id": hma["mission_id"],
        "hma_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "mission_genesis_record_hash": hma["mission_genesis_record_hash"],
        "plan_id": hma["plan_id"],
        "plan_hash": hma["plan_hash"],
        # copié depuis la HMA VÉRIFIÉE — jamais synthétisé
        "human_authorization_reference": hma["human_authorization_reference"],
        "human_capability_grant_id": human_capability_grant["human_capability_grant_id"],
        "human_capability_grant_hash": human_capability_grant["grant_record_hash"],
        "allowed_lease_classes": alc,
        "capability_scope": scope,
        "status": STATUS_MCS_ACTIVE_INERT,
        "issued_by": issued_by,
        "issuer_ref": issuer_ref,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
    }
    rh = _sha(_canon({k: core.get(k) for k in _MCS_BOUND_FIELDS}))
    core["scope_record_hash"] = rh
    core["mission_capability_scope_id"] = "mcs-" + rh[:32]
    core["created_at"] = _now()
    core["decision_authority"] = DECISION_AUTHORITY
    return {"status": STATUS_MCS_ACTIVE_INERT, "reason": None, "record": core,
            "grants_tool_access": False}


def build_mission_capability_scope(**kw) -> Optional[dict]:
    out = prepare_mission_capability_scope(**kw)
    return out.get("record")


def verify_mission_capability_scope(mcs: Optional[dict]) -> "tuple[bool, Optional[str]]":
    """Vérificateur STRUCTUREL déterministe (ne recharge pas genesis/plan ;
    la lignée HMA est liée par hash via `hma_record_hash` +
    `human_authorization_reference` dans le matériel haché)."""
    if not isinstance(mcs, dict):
        return False, "MCS_MISSING"
    if mcs.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if mcs.get("domain_tag") != MCS_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if mcs.get("issued_by") not in _AUTHORIZED_ISSUERS:
        return False, f"ISSUER_NOT_AUTHORIZED:{mcs.get('issued_by')}"
    for b in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        if mcs.get(b) is not False:
            return False, f"MCS_CLAIMS_AUTHORITY:{b}"
    for ref, pfx in (("mission_capability_scope_id", "mcs-"), ("hma_id", "hma-"),
                     ("mission_submission_id", "gsub-"), ("human_capability_grant_id", "hcg-")):
        v = mcs.get(ref)
        if not (isinstance(v, str) and v.startswith(pfx)):
            return False, f"REF_MALFORMED:{ref}"
    for ref in ("hma_record_hash", "mission_genesis_record_hash", "plan_hash",
                "human_authorization_reference", "human_capability_grant_hash"):
        if not (isinstance(mcs.get(ref), str) and mcs.get(ref)):
            return False, f"MISSING_REF:{ref}"
    alc = mcs.get("allowed_lease_classes")
    if not (isinstance(alc, list) and all(c in _LEASE_CLASSES for c in alc) and alc == sorted(set(alc))):
        return False, "ALLOWED_LEASE_CLASSES_INVALID"
    if mcs.get("status") != STATUS_MCS_ACTIVE_INERT:
        return False, "STATUS_INVALID"
    sc, why = _normalize_scope(mcs.get("capability_scope"))
    if sc is None or sc != mcs.get("capability_scope"):
        return False, f"CAPABILITY_SCOPE_INVALID:{why}"
    rh = _sha(_canon({k: mcs.get(k) for k in _MCS_BOUND_FIELDS}))
    if mcs.get("scope_record_hash") != rh:
        return False, "SCOPE_RECORD_HASH_MISMATCH"
    if mcs.get("mission_capability_scope_id") != "mcs-" + rh[:32]:
        return False, "MCS_ID_NOT_DERIVED"
    return True, None


def verify_mission_capability_scope_with_hma(
    mcs: Optional[dict], *, hma: dict, hma_verifier,
    human_capability_grant: Optional[dict] = None,
    human_capability_grant_authorization: Optional[dict] = None,
) -> "tuple[bool, Optional[str]]":
    """Recheck COMPLET de la lignée : structurel + HMA revérifiée via le
    `hma_verifier` INJECTÉ + (si fourni) HumanCapabilityGrant revérifié
    (+ HumanCapabilityGrantAuthorization) + liaisons exactes mcs↔hma↔grant."""
    ok, why = verify_mission_capability_scope(mcs)
    if not ok:
        return False, f"STRUCTURAL:{why}"
    ok_h, why_h = _run_hma_verifier(hma, hma_verifier)
    if not ok_h:
        return False, f"HMA_INVALID:{why_h}"
    if mcs.get("hma_id") != hma.get("human_mission_authorization_id"):
        return False, "MCS_HMA_ID_MISMATCH"
    if mcs.get("hma_record_hash") != hma.get("hma_record_hash"):
        return False, "MCS_HMA_HASH_MISMATCH"
    if mcs.get("mission_id") != hma.get("mission_id"):
        return False, "MCS_MISSION_ID_MISMATCH"
    if mcs.get("plan_hash") != hma.get("plan_hash"):
        return False, "MCS_PLAN_HASH_MISMATCH"
    if mcs.get("human_authorization_reference") != hma.get("human_authorization_reference"):
        return False, "MCS_HUMAN_AUTHORIZATION_REFERENCE_MISMATCH"
    hp = _hma_target_paths(hma)
    if isinstance(hp, list) and not (set(mcs["capability_scope"]["allowed_paths"]) <= set(hp)):
        return False, "MCS_PATHS_EXCEED_HMA"
    ho = _hma_operation_shapes(hma)
    if isinstance(ho, list) and not (set(mcs["capability_scope"]["allowed_operations"]) <= set(ho)):
        return False, "MCS_OPERATIONS_EXCEED_HMA"
    if human_capability_grant is not None:
        ok_g, why_g = verify_human_capability_grant(
            human_capability_grant, hma=hma, hma_verifier=hma_verifier,
            human_capability_grant_authorization=human_capability_grant_authorization)
        if not ok_g:
            return False, f"HUMAN_CAPABILITY_GRANT_INVALID:{why_g}"
        if mcs.get("human_capability_grant_id") != human_capability_grant["human_capability_grant_id"]:
            return False, "MCS_GRANT_ID_MISMATCH"
        if mcs.get("human_capability_grant_hash") != human_capability_grant["grant_record_hash"]:
            return False, "MCS_GRANT_HASH_MISMATCH"
        if human_capability_grant.get("mission_submission_id") != mcs.get("mission_submission_id"):
            return False, "MCS_GRANT_SUBMISSION_MISMATCH"
        if not (set(mcs["allowed_lease_classes"]) <= set(human_capability_grant["allowed_lease_classes"])):
            return False, "MCS_LEASE_CLASSES_EXCEED_HUMAN_GRANT"
        le_g, extra_g = _scope_le(mcs["capability_scope"], human_capability_grant["capability_scope"])
        if not le_g:
            return False, f"MCS_CAPABILITY_SCOPE_EXCEEDS_HUMAN_GRANT:{extra_g}"
    return True, None


def persist_mission_capability_scope(mcs: dict, store_dir=None) -> dict:
    ok, why = verify_mission_capability_scope(mcs)
    if not ok:
        return {"status": "MCS_PERSIST_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _mcs_store(store_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "MCS_PERSIST_REJECTED", "reason": f"MKDIR:{exc}"}
    p = d / f"{mcs['mission_capability_scope_id']}.json"
    payload = json.dumps(mcs, indent=2, sort_keys=True) + "\n"
    if p.exists():
        try:
            existing = p.read_text(encoding="utf-8")
        except OSError as exc:
            return {"status": "MCS_PERSIST_REJECTED", "reason": f"READ:{exc}"}
        if existing == payload:
            return {"status": "IDEMPOTENT_ALREADY_EXISTS",
                    "mission_capability_scope_id": mcs["mission_capability_scope_id"]}
        return {"status": "MCS_IMMUTABILITY_VIOLATION",
                "mission_capability_scope_id": mcs["mission_capability_scope_id"],
                "divergent_mcs_rewrite": "FAIL_CLOSED"}
    tmp = p.with_suffix(".json.tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(p)
    except OSError as exc:
        return {"status": "MCS_PERSIST_REJECTED", "reason": f"WRITE:{exc}"}
    return {"status": "STORED", "mission_capability_scope_id": mcs["mission_capability_scope_id"]}


def load_mission_capability_scope(mcs_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(mcs_id, str) and mcs_id.startswith("mcs-")):
        return None
    p = _mcs_store(store_dir) / f"{mcs_id}.json"
    if not p.is_file():
        return None
    try:
        mcs = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ok, _ = verify_mission_capability_scope(mcs)
    return mcs if ok else None


# ══════════════════════════════════════════════════════════════════════════
#  2 — LeaseIssuanceDecision (règle déterministe INERTE — PAS KX, PAS exécution)
# ══════════════════════════════════════════════════════════════════════════

_LIDEC_BOUND_FIELDS = (
    "schema_version", "domain_tag",
    "mission_submission_id", "mission_capability_scope_ref", "mission_capability_scope_hash",
    "human_capability_grant_ref", "human_capability_grant_hash",
    "capability_request_id", "route_decision_ref", "route_class",
    "proposed_lease_class", "proposed_lease_scope",
    "outcome", "issued_by", "issuer_ref",
    "is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access",
)


def _lidec(outcome: str, reason, *, msid=None, mcs_ref=None, mcs_hash=None,
           hcg_ref=None, hcg_hash=None,
           cap_id=None, rdec_ref=None, route_class=None, lease_class=None,
           lease_scope=None, issued_by=ISSUER_GATEWAY_CAPABILITY_DECISION,
           issuer_ref=None) -> dict:
    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": LIDEC_DOMAIN_TAG,
        "mission_submission_id": msid,
        "mission_capability_scope_ref": mcs_ref,
        "mission_capability_scope_hash": mcs_hash,
        "human_capability_grant_ref": hcg_ref,
        "human_capability_grant_hash": hcg_hash,
        "capability_request_id": cap_id,
        "route_decision_ref": rdec_ref,
        "route_class": route_class,
        "proposed_lease_class": lease_class,
        "proposed_lease_scope": lease_scope,
        "outcome": outcome,
        "issued_by": issued_by,
        "issuer_ref": issuer_ref,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
    }
    rh = _sha(_canon({k: core.get(k) for k in _LIDEC_BOUND_FIELDS}))
    core["issuance_decision_record_hash"] = rh
    core["lease_issuance_decision_id"] = "lidec-" + rh[:32]
    core["created_at"] = _now()
    core["reason"] = reason
    core["decision_authority"] = DECISION_AUTHORITY
    return core


def evaluate_lease_issuance(
    *, mission_submission: dict,
    capability_request: dict,
    route_decision: dict,
    mission_capability_scope: dict,
    proposed_lease_class: str,
    proposed_lease_scope: Optional[dict] = None,
    mission_status: Optional[str] = None,      # "ACTIVE" | "HOLD" | "CLOSED" | "REVOKED"
    human_capability_grant: Optional[dict] = None,
    human_capability_grant_authorization: Optional[dict] = None,
    mcs_hma: Optional[dict] = None,
    hma_verifier=None,
    issued_by: str = ISSUER_GATEWAY_CAPABILITY_DECISION,
    issuer_ref: Optional[str] = None,
) -> dict:
    """Décision déterministe : est-il permis de CRÉER un bail cognitif INERTE
    sous la MissionCapabilityScope humaine ? Renvoie un `LeaseIssuanceDecision`
    canonique. Un `LEASE_ELIGIBLE_INERT` exige que TOUTE la chaîne humaine vérifie
    (HMA + HumanCapabilityGrant + MCS + CapabilityRequest + RouteDecision) et
    n'accorde AUCUN accès outil."""
    _b: dict = {}
    L = lambda o, r, **kw: _lidec(o, r, issued_by=issued_by, issuer_ref=issuer_ref, **{**_b, **kw})

    if issued_by in _FORBIDDEN_ISSUERS or issued_by not in _AUTHORIZED_ISSUERS:
        return L(LEASE_DENIED_ISSUER, f"issuer:{issued_by}")

    # ── MissionCapabilityScope présente + structurellement valide ──
    ok_m, why_m = verify_mission_capability_scope(mission_capability_scope)
    if not ok_m:
        return L(LEASE_HOLD_MISSION_SCOPE_MISSING, f"mcs_invalid:{why_m}")
    _b["mcs_ref"] = mcs_ref = mission_capability_scope["mission_capability_scope_id"]
    _b["mcs_hash"] = mcs_hash = mission_capability_scope["scope_record_hash"]
    _b["msid"] = msid = mission_capability_scope["mission_submission_id"]

    # ── HumanCapabilityGrant : OBLIGATOIRE + VÉRIFIÉ + chaîné à MCS/HMA (§9) ──
    if human_capability_grant is None:
        return L(LEASE_HOLD_HUMAN_CAPABILITY_GRANT_MISSING, "human_capability_grant_missing")
    ok_g, why_g = verify_human_capability_grant(
        human_capability_grant,
        hma=(mcs_hma if (mcs_hma is not None or hma_verifier is not None) else None),
        hma_verifier=hma_verifier,
        human_capability_grant_authorization=human_capability_grant_authorization)
    if not ok_g:
        return L(LEASE_DENIED_AUTHORITY_GAP, f"human_capability_grant_invalid:{why_g}")
    if mission_capability_scope.get("human_capability_grant_id") != \
       human_capability_grant["human_capability_grant_id"]:
        return L(LEASE_DENIED_AUTHORITY_GAP, "mcs_grant_id_mismatch")
    if mission_capability_scope.get("human_capability_grant_hash") != \
       human_capability_grant["grant_record_hash"]:
        return L(LEASE_DENIED_AUTHORITY_GAP, "mcs_grant_hash_mismatch")
    if human_capability_grant.get("mission_submission_id") != msid:
        return L(LEASE_DENIED_AUTHORITY_GAP, "grant_mission_submission_mismatch")
    _b["hcg_ref"] = human_capability_grant["human_capability_grant_id"]
    _b["hcg_hash"] = human_capability_grant["grant_record_hash"]

    # ── Recheck complet de la lignée humaine si le matériel HMA est fourni ──
    if mcs_hma is not None or hma_verifier is not None:
        ok_l, why_l = verify_mission_capability_scope_with_hma(
            mission_capability_scope, hma=mcs_hma, hma_verifier=hma_verifier,
            human_capability_grant=human_capability_grant,
            human_capability_grant_authorization=human_capability_grant_authorization)
        if not ok_l:
            return L(LEASE_DENIED_AUTHORITY_GAP, f"lineage:{why_l}")

    # ── Soumission de mission CG-B ──
    if not isinstance(mission_submission, dict) or \
       mission_submission.get("domain_tag") != "OBSIDIA_CGB_MISSION_SUBMISSION_V0":
        return L(LEASE_DENIED_REQUEST_MISMATCH, "mission_submission_invalid")
    if mission_submission.get("mission_submission_id") != msid:
        return L(LEASE_DENIED_REQUEST_MISMATCH, "mission_submission_id")

    # ── Cycle de vie de mission fourni par l'appelant ──
    if mission_status in ("HOLD", "CLOSED", "REVOKED"):
        return L(LEASE_DENIED_MISSION_STATE, f"mission_status:{mission_status}")

    # ── CapabilityRequest CG-B (une REQUÊTE, jamais une autorité) ──
    if not isinstance(capability_request, dict) or \
       capability_request.get("domain_tag") != "OBSIDIA_CGB_CAPABILITY_REQUEST_V0":
        return L(LEASE_DENIED_REQUEST_MISMATCH, "capability_request_invalid",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash)
    if capability_request.get("granted") is not False:
        return L(LEASE_DENIED_REQUEST_MISMATCH, "capability_request_not_inert",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash)
    cap_id = capability_request.get("capability_request_id")
    if not (isinstance(cap_id, str) and cap_id.startswith("gcap-")):
        return L(LEASE_DENIED_REQUEST_MISMATCH, "capability_request_id",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash)
    if capability_request.get("mission_submission_id") != msid:
        return L(LEASE_DENIED_REQUEST_MISMATCH, "capability_request_mission",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id)

    # ── RouteDecision ──
    ok_r, why_r = _RD.verify_route_decision(route_decision)
    if not ok_r:
        return L(LEASE_DENIED_ROUTE, f"route_decision_invalid:{why_r}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id)
    rdec_ref = route_decision.get("route_decision_id")
    if (capability_request.get("route_decision") or {}).get("route_decision_id") != rdec_ref:
        return L(LEASE_DENIED_ROUTE, "route_decision_ref_mismatch",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id, rdec_ref=rdec_ref)
    rclass = route_decision.get("route_class")
    if route_decision.get("fail_closed_hold"):
        return L(LEASE_DENIED_ROUTE, "router_fail_closed_hold",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)
    if route_decision.get("human_authority_required") or rclass == _RD.ROUTE_HUMAN_AUTHORITY:
        return L(LEASE_HOLD_HUMAN_AUTHORITY_REQUIRED, "human_authority_required",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)
    if rclass == _RD.ROUTE_UNKNOWN or route_decision.get("unknown"):
        return L(LEASE_DENIED_UNKNOWN, "route_unknown",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)
    if rclass in _NO_LEASE_ROUTES or route_decision.get("gate_verdict") in ("DENY", "HOLD", "CLARIFY"):
        return L(LEASE_DENIED_ROUTE, f"no_lease_route:{rclass}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)

    # ── Mission routée sans HOLD humain en attente ──
    #    (une soumission `AWAITING_HUMAN` a déjà été classée route ci-dessus ;
    #     tout autre statut non routé est fail-closed).
    if mission_submission.get("status") not in ("SUBMITTED_ROUTED_INERT",):
        return L(LEASE_DENIED_MISSION_STATE, f"submission_status:{mission_submission.get('status')}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)

    # ── Classe de bail ↔ route ──
    if proposed_lease_class not in _LEASE_CLASSES:
        return L(LEASE_DENIED_ROUTE, f"unknown_lease_class:{proposed_lease_class}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass)
    if _CLASS_TO_ROUTE.get(proposed_lease_class) != rclass:
        return L(LEASE_DENIED_ROUTE, f"class_route_incompatible:{proposed_lease_class}!={rclass}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass, lease_class=proposed_lease_class)

    # ── Classe de bail dans la borne humaine ──
    if proposed_lease_class not in mission_capability_scope["allowed_lease_classes"]:
        return L(LEASE_DENIED_SCOPE, f"lease_class_not_in_mission_scope:{proposed_lease_class}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass, lease_class=proposed_lease_class)

    # ── Portée proposée <= portée mission (borne supérieure humaine) ──
    prop_scope, why_p = _normalize_scope(proposed_lease_scope)
    if prop_scope is None:
        return L(LEASE_DENIED_SCOPE, f"proposed_lease_scope_invalid:{why_p}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass, lease_class=proposed_lease_class)
    le, extra = _scope_le(prop_scope, mission_capability_scope["capability_scope"])
    if not le:
        return L(LEASE_DENIED_SCOPE, f"proposed_scope_exceeds_mission:{extra}",
                 msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash, cap_id=cap_id,
                 rdec_ref=rdec_ref, route_class=rclass, lease_class=proposed_lease_class,
                 lease_scope=prop_scope)

    return L(_ELIGIBLE, None, msid=msid, mcs_ref=mcs_ref, mcs_hash=mcs_hash,
             cap_id=cap_id, rdec_ref=rdec_ref, route_class=rclass,
             lease_class=proposed_lease_class, lease_scope=prop_scope)


def verify_lease_issuance_decision(lidec: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if not isinstance(lidec, dict):
        return False, "LIDEC_MISSING"
    if lidec.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if lidec.get("domain_tag") != LIDEC_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if lidec.get("issued_by") not in _AUTHORIZED_ISSUERS:
        return False, f"ISSUER_NOT_AUTHORIZED:{lidec.get('issued_by')}"
    for b in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        if lidec.get(b) is not False:
            return False, f"LIDEC_CLAIMS_AUTHORITY:{b}"
    for ref, pfx in (("mission_capability_scope_ref", "mcs-"),
                     ("human_capability_grant_ref", "hcg-")):
        v = lidec.get(ref)
        if v is not None and not (isinstance(v, str) and v.startswith(pfx)):
            return False, f"REF_MALFORMED:{ref}"
    valid_outcomes = (LEASE_ELIGIBLE_INERT, LEASE_DENIED_SCOPE, LEASE_DENIED_ROUTE,
                      LEASE_HOLD_HUMAN_CAPABILITY_GRANT_MISSING,
                      LEASE_DENIED_MISSION_STATE, LEASE_DENIED_REQUEST_MISMATCH,
                      LEASE_DENIED_AUTHORITY_GAP, LEASE_DENIED_UNKNOWN, LEASE_DENIED_ISSUER,
                      LEASE_HOLD_MISSION_SCOPE_MISSING, LEASE_HOLD_HUMAN_AUTHORITY_REQUIRED)
    if lidec.get("outcome") not in valid_outcomes:
        return False, "OUTCOME_INVALID"
    rh = _sha(_canon({k: lidec.get(k) for k in _LIDEC_BOUND_FIELDS}))
    if lidec.get("issuance_decision_record_hash") != rh:
        return False, "LIDEC_RECORD_HASH_MISMATCH"
    if lidec.get("lease_issuance_decision_id") != "lidec-" + rh[:32]:
        return False, "LIDEC_ID_NOT_DERIVED"
    return True, None



def persist_lease_issuance_decision(lidec: dict, store_dir=None) -> dict:
    ok, why = verify_lease_issuance_decision(lidec)
    if not ok:
        return {"status": "LIDEC_PERSIST_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _lidec_store(store_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "LIDEC_PERSIST_REJECTED", "reason": f"MKDIR:{exc}"}
    p = d / f"{lidec['lease_issuance_decision_id']}.json"
    payload = json.dumps(lidec, indent=2, sort_keys=True) + "\n"
    if p.exists():
        try:
            existing = p.read_text(encoding="utf-8")
        except OSError as exc:
            return {"status": "LIDEC_PERSIST_REJECTED", "reason": f"READ:{exc}"}
        if existing == payload:
            return {
                "status": "IDEMPOTENT_ALREADY_EXISTS",
                "lease_issuance_decision_id": lidec["lease_issuance_decision_id"],
            }
        return {
            "status": "LIDEC_IMMUTABILITY_VIOLATION",
            "lease_issuance_decision_id": lidec["lease_issuance_decision_id"],
            "divergent_lidec_rewrite": "FAIL_CLOSED",
        }
    tmp = p.with_suffix(".json.tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(p)
    except OSError as exc:
        return {"status": "LIDEC_PERSIST_REJECTED", "reason": f"WRITE:{exc}"}
    return {
        "status": "STORED",
        "lease_issuance_decision_id": lidec["lease_issuance_decision_id"],
    }


def load_lease_issuance_decision(lidec_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(lidec_id, str) and lidec_id.startswith("lidec-")):
        return None
    p = _lidec_store(store_dir) / f"{lidec_id}.json"
    if not p.is_file():
        return None
    try:
        lidec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ok, _ = verify_lease_issuance_decision(lidec)
    return lidec if ok else None

# ══════════════════════════════════════════════════════════════════════════
#  3 — CLI mince (diagnostic uniquement)
# ══════════════════════════════════════════════════════════════════════════

def _main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="obsidia_mission_capability_scope_v0",
        description="CG-C2 MissionCapabilityScope / LeaseIssuanceDecision — RUNTIME INERTE")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)
    if a.self_check:
        print(json.dumps({
            "MISSION_CAPABILITY_SCOPE_RUNTIME": MISSION_CAPABILITY_SCOPE_RUNTIME,
            "LEASE_ISSUANCE_DECISION_RUNTIME": LEASE_ISSUANCE_DECISION_RUNTIME,
            "HUMAN_CAPABILITY_GRANT_VERIFICATION": HUMAN_CAPABILITY_GRANT_VERIFICATION,
            "HUMAN_CAPABILITY_GRANT_AUTHORIZATION_VERIFICATION": HUMAN_CAPABILITY_GRANT_AUTHORIZATION_VERIFICATION,
            "HUMAN_COGNITIVE_CAPABILITY_GRANT_BINDING": HUMAN_COGNITIVE_CAPABILITY_GRANT_BINDING,
            "HUMAN_CAPABILITY_GRANT_ORIGIN_SELF_ASSERTED": HUMAN_CAPABILITY_GRANT_ORIGIN_SELF_ASSERTED,
            "HUMAN_AUTHORIZATION_VERIFIER_REQUIRED": HUMAN_AUTHORIZATION_VERIFIER_REQUIRED,
            "HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED": HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED,
            "HUMAN_ORIGIN_PROOF_MODEL": HUMAN_ORIGIN_PROOF_MODEL,
            "TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING": TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
            "CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY": CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY,
            "PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING": PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
            "MISSION_CAPABILITY_SCOPE_BINDING": MISSION_CAPABILITY_SCOPE_BINDING,
            "LEASE_ISSUANCE_DECISION_RULE": LEASE_ISSUANCE_DECISION_RULE,
            "LEASE_TO_MISSION_SCOPE_RUNTIME_CHECK": LEASE_TO_MISSION_SCOPE_RUNTIME_CHECK,
            "MISSION_CAPABILITY_SCOPE_IS_EXECUTION_AUTHORITY": MISSION_CAPABILITY_SCOPE_IS_EXECUTION_AUTHORITY,
            "LEASE_ISSUANCE_DECISION_IS_EXECUTION_AUTHORITY": LEASE_ISSUANCE_DECISION_IS_EXECUTION_AUTHORITY,
            "LEASE_ISSUANCE_DECISION_IS_KX_AUTHORITY": LEASE_ISSUANCE_DECISION_IS_KX_AUTHORITY,
            "LEASE_GRANTS_TOOL_ACCESS": LEASE_GRANTS_TOOL_ACCESS,
            "LEASE_ENFORCEMENT_ACTIVE": LEASE_ENFORCEMENT_ACTIVE,
            "HARD_TOOL_GATE_ACTIVE": HARD_TOOL_GATE_ACTIVE,
            "CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED": CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED,
            "DEFAULT_MISSION_CAPABILITY_SCOPE": DEFAULT_MISSION_CAPABILITY_SCOPE,
            "MULTI_OPERATION_GENERALIZATION": MULTI_OPERATION_GENERALIZATION,
        }, indent=2))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
