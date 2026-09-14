#!/usr/bin/env python3
"""OBSIDIA CG-D — PreToolUse SHADOW classifier / observer, ENTIÈREMENT OBSERVATIONNEL.

Répond à UNE question, sans jamais agir :
  « SI l'enforcement était actif, quel chemin de gouvernance / bail / HOLD /
    condition de refus s'appliquerait à cette requête d'outil de Claude ? »

CG-D NE PEUT PAS : bloquer, autoriser, accorder, muter une autorité, émettre un
bail, rediriger l'exécution, modifier des arguments d'outil, appeler un provider.

  CLAUDE TOOL REQUEST
        ↓ (observation seule)
  NORMALIZE TOOL INTENT  →  MISSION/ROUTE/CAPABILITY LOOKUP (READ-ONLY)
        ↓
  SHADOW CLASSIFICATION  →  SHADOW RECEIPT
        ↓
  LA REQUÊTE D'OUTIL D'ORIGINE CONTINUE INCHANGÉE

Bornes (toutes affirmées, statiques) :
  SHADOW_CAN_DENY_TOOL = SHADOW_CAN_GRANT_TOOL = SHADOW_CAN_MODIFY_TOOL_ARGS = FALSE
  SHADOW_CAN_EXECUTE_TOOL = SHADOW_CAN_ISSUE_LEASE = FALSE
  SHADOW_CAN_CREATE_HUMAN_AUTHORITY = SHADOW_CAN_CALL_PROVIDER_AUTOMATICALLY = FALSE
  HARD_TOOL_GATE_ACTIVE = LEASE_ENFORCEMENT_ACTIVE = FALSE
  CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED = FALSE
  PRE_TOOL_LEASE_LOOKUP_MODE = SHADOW_READ_ONLY

Frontière de confiance (repris de CG-C2, NON fermé ici) :
  TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = NOT_YET_ENFORCED
  PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = OPEN
  CG_D_SHADOW_MAY_PROCEED_WITH_EXTERNAL_TRUST_BOUNDARY_UNWIRED = TRUE
  CG_E_ACTIVE_ENFORCEMENT_REQUIRES_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = TRUE

Le fail-open OBSERVATIONNEL de CG-D (classifier casse -> requête inchangée) N'EST
PAS le `ROUTER_FAIL_OPEN` de CG-B, qui reste CLOSED.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_gateway_route_decision_v0 as _RD           # CG-B (route classes, store resolver)
import obsidia_cognitive_capability_lease_v0 as _CCL      # CG-C (lease verify — READ-ONLY)
import obsidia_mission_capability_scope_v0 as _MCS        # CG-C2 (mcs/hcg verify — READ-ONLY)

SCHEMA_VERSION = 1
SHADOW_DOMAIN_TAG = "OBSIDIA_CGD_PRETOOL_SHADOW_DECISION_V0"
DECISION_AUTHORITY = "KX108_ONLY"

# ── Bornes explicites ─────────────────────────────────────────────────
PRE_TOOL_SHADOW_CLASSIFIER = "IMPLEMENTED_V0"
PRE_TOOL_SHADOW_RECEIPTS = "IMPLEMENTED_V0"
PRE_TOOL_LEASE_LOOKUP_MODE = "SHADOW_READ_ONLY"
PRE_TOOL_LEASE_LOOKUP_CAN_GRANT_ACCESS = False
PRE_TOOL_LEASE_LOOKUP_CAN_CREATE_LEASE = False
PRE_TOOL_LEASE_LOOKUP_CAN_MUTATE_LEASE = False
SHADOW_CAN_DENY_TOOL = False
SHADOW_CAN_GRANT_TOOL = False
SHADOW_CAN_MODIFY_TOOL_ARGS = False
SHADOW_CAN_EXECUTE_TOOL = False
SHADOW_CAN_ISSUE_LEASE = False
SHADOW_CAN_CREATE_HUMAN_AUTHORITY = False
SHADOW_CAN_CALL_PROVIDER_AUTOMATICALLY = False
HARD_TOOL_GATE_ACTIVE = False
LEASE_ENFORCEMENT_ACTIVE = False
CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED = False
CLAUDE_PERMISSION_MODEL_CHANGED = False
RAW_TOOL_ARGUMENTS_PERSISTED = False
MISSING_MISSION_CONTEXT_CAN_DEFAULT_TO_GLOBAL_AUTHORITY = False
TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = "NOT_YET_ENFORCED"
PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = "OPEN"
CG_D_SHADOW_MAY_PROCEED_WITH_EXTERNAL_TRUST_BOUNDARY_UNWIRED = True
CG_E_ACTIVE_ENFORCEMENT_REQUIRES_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING = True
OBSIDURE_PROPOSAL_ONLY = True
OBSIDURE_ENGINEERING_EXECUTION_ACTIVE = False

# ── Livraison hôte : statut VÉRIDIQUE (option C — committé avec host delivery NON prouvée) ──
#  Le classifier, l'entrypoint observateur, les reçus et le lookup de bail lecture seule sont
#  IMPLÉMENTÉS et localement prouvés INERTES (56 tests + canary synthétique + invocation
#  standalone équivalente-hôte). La livraison RÉELLE d'événements PreToolUse par l'hôte Claude
#  à l'observateur N'EST PAS prouvée (3 canaries réels sans reçu dans la session worktree).
SYNTHETIC_SHADOW_OBSERVER_CANARY = "PASS"
STANDALONE_OBSERVER_INVOCATION = "PASS"
REAL_SHADOW_OBSERVER_CANARY = "NOT_PROVEN"
REAL_PRETOOL_HOST_DELIVERY_PROVEN = False
PRE_TOOL_OBSERVATION_COVERAGE = "NOT_PROVEN"
AT_REFERENCE_PRETOOL_COVERAGE = "UNKNOWN"
PRE_TOOL_SHADOW_OBSERVER = "IMPLEMENTED_V0_HOST_DELIVERY_UNPROVEN"
PRECONDITION_CGE_2_REAL_PRETOOL_HOST_DELIVERY = "OPEN"
CG_E_ACTIVE_ENFORCEMENT_REQUIRES_REAL_PRETOOL_HOST_DELIVERY = True
# CG_E_ACTIVE_ENFORCEMENT_ALLOWED ONLY_IF PRECONDITION_CGE_1 == CLOSED AND PRECONDITION_CGE_2 == CLOSED

# ── Familles d'outils normalisées (déterministe ; jamais depuis le prompt) ─
FAM_READ_ONLY_REPO_INSPECTION = "READ_ONLY_REPO_INSPECTION"
FAM_SEARCH = "SEARCH"
FAM_TEST_EXECUTION = "TEST_EXECUTION"
FAM_LEAN_EXECUTION = "LEAN_EXECUTION"
FAM_GIT_READ = "GIT_READ"
FAM_GIT_MUTATION = "GIT_MUTATION"
FAM_FILE_MUTATION = "FILE_MUTATION"
FAM_SHELL_GENERAL = "SHELL_GENERAL"
FAM_AGENT_SPAWN = "AGENT_SPAWN"
FAM_UNKNOWN_TOOL = "UNKNOWN_TOOL"

# ── Cibles de route SHADOW (aucune redirection réelle) ─────────────────
ROUTE_TARGET_STACK_NATIVE = "STACK_NATIVE"
ROUTE_TARGET_COGNITIVE_LEASE = "COGNITIVE_LEASE"
ROUTE_TARGET_HUMAN_AUTHORITY = "HUMAN_AUTHORITY"
ROUTE_TARGET_UNKNOWN = "UNKNOWN"

# ── Vocabulaire de verdict SHADOW (fermé / versionné) ─────────────────
SHADOW_STACK_NATIVE_ROUTE = "SHADOW_STACK_NATIVE_ROUTE"
SHADOW_WOULD_REQUIRE_LANGUAGE_LEASE = "SHADOW_WOULD_REQUIRE_LANGUAGE_LEASE"
SHADOW_WOULD_REQUIRE_REASONING_LEASE = "SHADOW_WOULD_REQUIRE_REASONING_LEASE"
SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE = "SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE"
SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT = "SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT"
SHADOW_LEASE_SCOPE_MISMATCH = "SHADOW_LEASE_SCOPE_MISMATCH"
SHADOW_MISSION_SCOPE_MISMATCH = "SHADOW_MISSION_SCOPE_MISMATCH"
SHADOW_MISSION_CONTEXT_MISSING = "SHADOW_MISSION_CONTEXT_MISSING"
SHADOW_HUMAN_AUTHORITY_REQUIRED = "SHADOW_HUMAN_AUTHORITY_REQUIRED"
SHADOW_UNKNOWN_AUTHORITY = "SHADOW_UNKNOWN_AUTHORITY"
SHADOW_ROUTE_HOLD = "SHADOW_ROUTE_HOLD"
SHADOW_TRUST_ROOT_UNBOUND = "SHADOW_TRUST_ROOT_UNBOUND"
SHADOW_WOULD_ALLOW_IF_TRUST_ROOT_BOUND = "SHADOW_WOULD_ALLOW_IF_TRUST_ROOT_BOUND"
SHADOW_WOULD_DENY_IF_ENFORCED = "SHADOW_WOULD_DENY_IF_ENFORCED"
SHADOW_CLASSIFIER_ERROR = "SHADOW_CLASSIFIER_ERROR"

_ALL_VERDICTS = (
    SHADOW_STACK_NATIVE_ROUTE, SHADOW_WOULD_REQUIRE_LANGUAGE_LEASE,
    SHADOW_WOULD_REQUIRE_REASONING_LEASE, SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE,
    SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT, SHADOW_LEASE_SCOPE_MISMATCH,
    SHADOW_MISSION_SCOPE_MISMATCH, SHADOW_MISSION_CONTEXT_MISSING,
    SHADOW_HUMAN_AUTHORITY_REQUIRED, SHADOW_UNKNOWN_AUTHORITY, SHADOW_ROUTE_HOLD,
    SHADOW_TRUST_ROOT_UNBOUND, SHADOW_WOULD_ALLOW_IF_TRUST_ROOT_BOUND,
    SHADOW_WOULD_DENY_IF_ENFORCED, SHADOW_CLASSIFIER_ERROR,
)

# ── Mapping canonique classe de bail ↔ route (préservé de CG-B/CG-C) ──
_LEASE_CLASS_LANGUAGE = _CCL.LANGUAGE_LEASE
_LEASE_CLASS_REASONING = _CCL.REASONING_LEASE
_LEASE_CLASS_ENGINEERING = _CCL.ENGINEERING_LEASE

_canon = _RD._canon
_sha = _RD._sha256_hex
_now = _RD._now


def _store_dir(store_dir=None) -> Path:
    if store_dir is not None:
        return Path(store_dir)
    env = os.environ.get("OBSIDIA_PRETOOL_SHADOW_STORE_DIR")
    return Path(env) if env else (_SCRIPTS.parent / "audit" / "pretool_shadow")


# ══════════════════════════════════════════════════════════════════════════
#  1 — Normalisation d'intention d'outil (déterministe, bornée, sans prompt)
# ══════════════════════════════════════════════════════════════════════════

_TOOL_READ = {"Read"}
_TOOL_SEARCH = {"Grep", "Glob"}
_TOOL_MUTATE = {"Edit", "Write", "NotebookEdit"}
_TOOL_AGENT = {"Task", "Agent"}

# familles Bash reconnues DÉTERMINISTES uniquement
_BASH_READ_CMDS = ("ls", "cat", "head", "tail", "wc", "pwd", "echo", "which",
                   "find", "grep", "rg", "date", "env", "printenv", "stat", "file", "tree")
_BASH_GIT_READ = ("status", "diff", "log", "show", "branch", "remote", "rev-parse",
                  "describe", "blame", "cat-file", "ls-files", "shortlog", "for-each-ref")
_BASH_GIT_MUTATION = ("add", "commit", "reset", "checkout", "switch", "restore",
                      "push", "pull", "fetch", "merge", "rebase", "cherry-pick",
                      "stash", "tag", "clean", "rm", "mv", "apply", "am", "revert",
                      "worktree", "config", "init", "clone", "gc", "prune")
_BASH_FILE_MUTATION = ("rm", "mv", "cp", "mkdir", "rmdir", "touch", "chmod", "chown",
                       "ln", "truncate", "dd", "tee", "sed -i", "install")


def _basename_of(path) -> Optional[str]:
    if not isinstance(path, str) or not path.strip():
        return None
    p = path.replace("\\", "/").rstrip("/")
    return p.rsplit("/", 1)[-1] or None


def _bounded_path_id(path) -> Optional[str]:
    """Identifiant de chemin BORNÉ : dossier immédiat + nom. Jamais le contenu."""
    if not isinstance(path, str) or not path.strip():
        return None
    p = path.replace("\\", "/").strip().rstrip("/")
    parts = [x for x in p.split("/") if x not in ("", ".")]
    if not parts:
        return None
    return "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]


def _classify_bash(command: str) -> "tuple[str, str, dict]":
    """Classification CONSERVATRICE d'une commande shell. Renvoie
    (famille, sous-famille-commande, métadonnées bornées)."""
    if not isinstance(command, str) or not command.strip():
        return FAM_UNKNOWN_TOOL, "empty", {}
    raw = command.strip()
    low = raw.lower()
    head = low.split()
    first = head[0] if head else ""
    meta = {"command_family": first}

    # pytest / python -m pytest
    if first in ("pytest",) or low.startswith("python -m pytest") or low.startswith("py -m pytest"):
        return FAM_TEST_EXECUTION, "pytest", meta
    # lake build (Lean)
    if first == "lake" or low.startswith("lake "):
        return FAM_LEAN_EXECUTION, "lake", meta
    # git
    if first == "git" and len(head) >= 2:
        sub = head[1]
        meta["git_subcommand"] = sub
        if sub in _BASH_GIT_READ:
            return FAM_GIT_READ, f"git {sub}", meta
        if sub in _BASH_GIT_MUTATION:
            return FAM_GIT_MUTATION, f"git {sub}", meta
        return FAM_SHELL_GENERAL, f"git {sub}", meta
    # mutations fichier explicites
    if first in _BASH_FILE_MUTATION or " sed -i" in low or low.startswith("sed -i"):
        return FAM_FILE_MUTATION, first, meta
    # redirection d'écriture (> / >>) hors here-doc évident
    if (">" in raw and "2>" not in raw.replace("2>&1", "")) or ">>" in raw:
        return FAM_FILE_MUTATION, "redirect_write", meta
    # lecture pure reconnue
    if first in _BASH_READ_CMDS:
        return FAM_READ_ONLY_REPO_INSPECTION, first, meta
    return FAM_SHELL_GENERAL, first, meta


def normalize_tool_intent(tool_name: str, tool_input: Optional[dict]) -> dict:
    """Déterministe. N'utilise JAMAIS le contenu du prompt comme autorité.
    Ne persiste JAMAIS d'arguments bruts."""
    ti = tool_input if isinstance(tool_input, dict) else {}
    out = {
        "tool_name": tool_name if isinstance(tool_name, str) else "",
        "normalized_tool_family": FAM_UNKNOWN_TOOL,
        "normalized_operation": "unknown",
        "requested_paths": [],
        "requested_command_family": None,
        "bash_meta": {},
    }
    if tool_name in _TOOL_READ:
        out["normalized_tool_family"] = FAM_READ_ONLY_REPO_INSPECTION
        out["normalized_operation"] = "read_file"
        pid = _bounded_path_id(ti.get("file_path") or ti.get("path"))
        if pid:
            out["requested_paths"] = [pid]
    elif tool_name in _TOOL_SEARCH:
        out["normalized_tool_family"] = FAM_SEARCH
        out["normalized_operation"] = "search"
        pid = _bounded_path_id(ti.get("path"))
        if pid:
            out["requested_paths"] = [pid]
    elif tool_name in _TOOL_MUTATE:
        out["normalized_tool_family"] = FAM_FILE_MUTATION
        out["normalized_operation"] = ("write_file" if tool_name == "Write" else "edit_file")
        pid = _bounded_path_id(ti.get("file_path") or ti.get("notebook_path") or ti.get("path"))
        if pid:
            out["requested_paths"] = [pid]
    elif tool_name in _TOOL_AGENT:
        out["normalized_tool_family"] = FAM_AGENT_SPAWN
        out["normalized_operation"] = "spawn_subagent"
        st = ti.get("subagent_type")
        if isinstance(st, str) and st:
            out["bash_meta"] = {"subagent_type": st[:64]}
    elif tool_name == "Bash":
        fam, cmdfam, meta = _classify_bash(str(ti.get("command", "")))
        out["normalized_tool_family"] = fam
        out["normalized_operation"] = cmdfam
        out["requested_command_family"] = meta.get("command_family")
        out["bash_meta"] = meta
    else:
        out["normalized_tool_family"] = FAM_UNKNOWN_TOOL
        out["normalized_operation"] = "unknown_tool"
    return out


# ══════════════════════════════════════════════════════════════════════════
#  2 — Recherche de contexte READ-ONLY (jamais de fabrication de refs)
# ══════════════════════════════════════════════════════════════════════════

def _shadow_lease_lookup(refs: Optional[dict], *, lease_store_dir=None) -> dict:
    """Recherche STRICTEMENT LECTURE SEULE d'un bail existant + de sa chaîne, à
    des fins de CLASSIFICATION uniquement. N'accorde rien, ne crée rien, ne mute
    rien. Renvoie un dict descriptif (jamais un booléen d'autorisation)."""
    res = {
        "lease_id": None, "lease_found": False, "lease_structurally_valid": None,
        "lease_class": None, "mission_capability_scope_ref": None,
        "human_capability_grant_ref": None, "context_verdict": None,
        "lookup_mode": PRE_TOOL_LEASE_LOOKUP_MODE,
        "can_grant_access": PRE_TOOL_LEASE_LOOKUP_CAN_GRANT_ACCESS,
    }
    refs = refs or {}
    lease_id = refs.get("lease_id")
    if not (isinstance(lease_id, str) and lease_id.startswith("cclease-")):
        return res
    res["lease_id"] = lease_id
    try:
        lease = _CCL.load_capability_lease(lease_id, store_dir=lease_store_dir)
    except Exception:
        lease = None
    if lease is None:
        return res
    res["lease_found"] = True
    try:
        ok, _why = _CCL.verify_capability_lease(lease)
    except Exception:
        ok = False
    res["lease_structurally_valid"] = bool(ok)
    res["lease_class"] = lease.get("lease_class")
    res["mission_capability_scope_ref"] = lease.get("mission_capability_scope_ref")
    # NB : la chaîne contextuelle complète (mcs/hcg/lidec) n'est PAS
    # rechargée ici sans refs explicites — pas de fabrication.
    return res


# ══════════════════════════════════════════════════════════════════════════
#  3 — Classification SHADOW (aucun effet)
# ══════════════════════════════════════════════════════════════════════════

_FAMILY_TO_ROUTE_TARGET = {
    FAM_READ_ONLY_REPO_INSPECTION: ROUTE_TARGET_STACK_NATIVE,
    FAM_SEARCH: ROUTE_TARGET_STACK_NATIVE,
    FAM_TEST_EXECUTION: ROUTE_TARGET_STACK_NATIVE,
    FAM_LEAN_EXECUTION: ROUTE_TARGET_STACK_NATIVE,
    FAM_GIT_READ: ROUTE_TARGET_STACK_NATIVE,
    FAM_GIT_MUTATION: ROUTE_TARGET_HUMAN_AUTHORITY,
    FAM_FILE_MUTATION: ROUTE_TARGET_STACK_NATIVE,   # gouverné par C2 / governed-apply
    FAM_AGENT_SPAWN: ROUTE_TARGET_COGNITIVE_LEASE,
    FAM_SHELL_GENERAL: ROUTE_TARGET_UNKNOWN,
    FAM_UNKNOWN_TOOL: ROUTE_TARGET_UNKNOWN,
}


def _shadow_classify(norm: dict, lease: dict, mission_context_known: bool) -> "tuple[str, list, str]":
    """Renvoie (shadow_verdict, reason_codes, shadow_route_target). PUR."""
    fam = norm["normalized_tool_family"]
    route_target = _FAMILY_TO_ROUTE_TARGET.get(fam, ROUTE_TARGET_UNKNOWN)
    reasons = [f"family:{fam}", f"operation:{norm['normalized_operation']}"]

    # 1. familles stack-native pures : aucun bail cognitif requis.
    if fam in (FAM_READ_ONLY_REPO_INSPECTION, FAM_SEARCH, FAM_TEST_EXECUTION,
               FAM_LEAN_EXECUTION, FAM_GIT_READ):
        return SHADOW_STACK_NATIVE_ROUTE, reasons + ["stack_native_no_lease"], route_target

    # 2. mutation Git : disposition humaine explicite sous la gouvernance actuelle.
    if fam == FAM_GIT_MUTATION:
        return SHADOW_HUMAN_AUTHORITY_REQUIRED, reasons + ["git_mutation_human_disposition"], route_target

    # 3. shell non reconnu / outil inconnu : autorité inconnue (conservateur).
    if fam in (FAM_SHELL_GENERAL, FAM_UNKNOWN_TOOL):
        return SHADOW_UNKNOWN_AUTHORITY, reasons + ["unrecognized_surface_conservative"], route_target

    # 4. mutation fichier / spawn d'agent : ingénierie directe par Claude.
    if fam in (FAM_FILE_MUTATION, FAM_AGENT_SPAWN):
        base = reasons + ["direct_claude_engineering",
                          f"lease_class_required:{_LEASE_CLASS_ENGINEERING}"]
        if not mission_context_known:
            return SHADOW_MISSION_CONTEXT_MISSING, base + ["no_active_mission_context"], route_target
        if lease.get("lease_found") and lease.get("lease_structurally_valid"):
            # §7 : bail présent + structurellement valide, MAIS racine de confiance
            # hôte NON câblée -> jamais ACTIVE_ALLOW.
            return SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT, base + [
                "lease_structurally_valid_inert",
                "trust_root_unbound",
                f"trusted_human_authorization_host_binding:{TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING}",
            ], route_target
        if lease.get("lease_id") and not lease.get("lease_found"):
            return SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE, base + ["referenced_lease_absent"], route_target
        return SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE, base + ["no_lease_present"], route_target

    return SHADOW_UNKNOWN_AUTHORITY, reasons + ["unmapped_family"], route_target


def _build_shadow_decision(norm: dict, lease: dict, refs: Optional[dict],
                           verdict: str, reasons: list, route_target: str) -> dict:
    refs = refs or {}
    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": SHADOW_DOMAIN_TAG,
        "tool_name": norm["tool_name"],
        "normalized_tool_family": norm["normalized_tool_family"],
        "normalized_operation": norm["normalized_operation"],
        "requested_paths": list(norm.get("requested_paths") or []),
        "requested_command_family": norm.get("requested_command_family"),
        "mission_submission_id": refs.get("mission_submission_id")
            if isinstance(refs.get("mission_submission_id"), str)
            and str(refs.get("mission_submission_id")).startswith("gsub-") else None,
        "route_decision_ref": refs.get("route_decision_ref")
            if isinstance(refs.get("route_decision_ref"), str)
            and str(refs.get("route_decision_ref")).startswith("rdec-") else None,
        "capability_request_ref": refs.get("capability_request_ref")
            if isinstance(refs.get("capability_request_ref"), str)
            and str(refs.get("capability_request_ref")).startswith("gcap-") else None,
        "lease_id": lease.get("lease_id"),
        "lease_found": lease.get("lease_found"),
        "lease_structurally_valid": lease.get("lease_structurally_valid"),
        "lease_class_required": (_LEASE_CLASS_ENGINEERING
                                 if norm["normalized_tool_family"] in (FAM_FILE_MUTATION, FAM_AGENT_SPAWN)
                                 else None),
        "mission_capability_scope_ref": lease.get("mission_capability_scope_ref"),
        "shadow_route_target": route_target,
        "shadow_verdict": verdict,
        "reason_codes": list(reasons),
        "trust_boundary_state": TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
        "pre_tool_lease_lookup_mode": PRE_TOOL_LEASE_LOOKUP_MODE,
        "grants_tool_access": False,
        "enforcement_active": False,
        "actual_enforcement": False,
        "actual_denial": False,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_human_authority": False,
        "is_sovereign": False,
    }
    rh = _sha(_canon(core))
    core["record_hash"] = rh
    core["shadow_decision_id"] = "psd-" + rh[:32]
    core["observed_at"] = _now()
    core["decision_authority"] = DECISION_AUTHORITY
    return core


def classify_pretool_event(payload: Optional[dict], *, refs: Optional[dict] = None,
                           lease_store_dir=None) -> dict:
    """Point d'entrée PUR (aucune écriture). Renvoie un PreToolShadowDecisionV0.
    Ne lève JAMAIS : toute erreur -> verdict SHADOW_CLASSIFIER_ERROR."""
    try:
        p = payload if isinstance(payload, dict) else {}
        tool_name = p.get("tool_name", "")
        tool_input = p.get("tool_input") if isinstance(p.get("tool_input"), dict) else {}
        norm = normalize_tool_intent(tool_name, tool_input)
        # refs explicites uniquement (jamais inventées depuis le payload)
        eff_refs = dict(refs or {})
        for k in ("mission_submission_id", "route_decision_ref",
                  "capability_request_ref", "lease_id"):
            v = p.get(k) or (p.get("tool_input") or {}).get(k)
            if isinstance(v, str) and v and k not in eff_refs:
                eff_refs[k] = v
        lease = _shadow_lease_lookup(eff_refs, lease_store_dir=lease_store_dir)
        _msid = eff_refs.get("mission_submission_id")
        mission_known = isinstance(_msid, str) and _msid.startswith("gsub-")
        verdict, reasons, route_target = _shadow_classify(norm, lease, mission_known)
        return _build_shadow_decision(norm, lease, eff_refs, verdict, reasons, route_target)
    except Exception as exc:                       # fail-open OBSERVATIONNEL
        core = {
            "schema_version": SCHEMA_VERSION, "domain_tag": SHADOW_DOMAIN_TAG,
            "tool_name": (payload or {}).get("tool_name", "") if isinstance(payload, dict) else "",
            "normalized_tool_family": FAM_UNKNOWN_TOOL, "normalized_operation": "unknown",
            "requested_paths": [], "requested_command_family": None,
            "mission_submission_id": None, "route_decision_ref": None,
            "capability_request_ref": None, "lease_id": None, "lease_found": False,
            "lease_structurally_valid": None, "lease_class_required": None,
            "mission_capability_scope_ref": None, "shadow_route_target": ROUTE_TARGET_UNKNOWN,
            "shadow_verdict": SHADOW_CLASSIFIER_ERROR,
            "reason_codes": [f"classifier_exception:{type(exc).__name__}"],
            "trust_boundary_state": TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
            "pre_tool_lease_lookup_mode": PRE_TOOL_LEASE_LOOKUP_MODE,
            "grants_tool_access": False, "enforcement_active": False,
            "actual_enforcement": False, "actual_denial": False,
            "is_execution_authority": False, "is_kx_authority": False,
            "is_human_authority": False, "is_sovereign": False,
        }
        rh = _sha(_canon(core))
        core["record_hash"] = rh
        core["shadow_decision_id"] = "psd-" + rh[:32]
        core["observed_at"] = _now()
        core["decision_authority"] = DECISION_AUTHORITY
        return core


def verify_shadow_decision(d: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if not isinstance(d, dict):
        return False, "SHADOW_DECISION_MISSING"
    if d.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if d.get("domain_tag") != SHADOW_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if d.get("shadow_verdict") not in _ALL_VERDICTS:
        return False, "SHADOW_VERDICT_INVALID"
    for b in ("grants_tool_access", "enforcement_active", "actual_enforcement",
              "actual_denial", "is_execution_authority", "is_kx_authority",
              "is_human_authority", "is_sovereign"):
        if d.get(b) is not False:
            return False, f"SHADOW_CLAIMS_AUTHORITY:{b}"
    body = {k: v for k, v in d.items()
            if k not in ("record_hash", "shadow_decision_id", "observed_at", "decision_authority")}
    if d.get("record_hash") != _sha(_canon(body)):
        return False, "SHADOW_RECORD_HASH_MISMATCH"
    if d.get("shadow_decision_id") != "psd-" + d["record_hash"][:32]:
        return False, "SHADOW_ID_NOT_DERIVED"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  4 — Reçu SHADOW (append-only ; arguments bruts JAMAIS persistés)
# ══════════════════════════════════════════════════════════════════════════

def persist_shadow_receipt(decision: dict, store_dir=None) -> dict:
    """Écrit un reçu SHADOW auditables : record + ligne JSONL append-only.
    N'écrit JAMAIS dans audit/world_action_bus.jsonl. Ne persiste QUE des
    champs normalisés (pas d'arguments bruts, pas de contenu, pas de prompt)."""
    ok, why = verify_shadow_decision(decision)
    if not ok:
        return {"status": "SHADOW_RECEIPT_REJECTED", "reason": f"STRUCTURAL:{why}"}
    d = _store_dir(store_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"status": "SHADOW_RECEIPT_REJECTED", "reason": f"MKDIR:{exc}"}
    receipt = {
        "shadow_decision_id": decision["shadow_decision_id"],
        "observed_at": decision["observed_at"],
        "tool_name": decision["tool_name"],
        "normalized_tool_family": decision["normalized_tool_family"],
        "normalized_operation": decision["normalized_operation"],
        "requested_paths": decision["requested_paths"],
        "requested_command_family": decision["requested_command_family"],
        "mission_submission_id": decision["mission_submission_id"],
        "shadow_route_target": decision["shadow_route_target"],
        "lease_id": decision["lease_id"],
        "lease_class_required": decision["lease_class_required"],
        "lease_found": decision["lease_found"],
        "lease_structurally_valid": decision["lease_structurally_valid"],
        "shadow_verdict": decision["shadow_verdict"],
        "reason_codes": decision["reason_codes"],
        "trust_boundary_state": decision["trust_boundary_state"],
        "record_hash": decision["record_hash"],
        "actual_enforcement": False,
        "actual_denial": False,
        "raw_tool_arguments_persisted": False,
    }
    p = d / f"{decision['shadow_decision_id']}.json"
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if p.exists():
        try:
            if p.read_text(encoding="utf-8") == payload:
                return {"status": "IDEMPOTENT_ALREADY_EXISTS",
                        "shadow_decision_id": decision["shadow_decision_id"]}
        except OSError:
            pass
        return {"status": "SHADOW_RECEIPT_IMMUTABILITY_VIOLATION",
                "divergent_shadow_receipt": "FAIL_CLOSED"}
    try:
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(p)
        with (d / "shadow_receipts.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    except OSError as exc:
        return {"status": "SHADOW_RECEIPT_REJECTED", "reason": f"WRITE:{exc}"}
    return {"status": "SHADOW_RECEIPT_RECORDED",
            "shadow_decision_id": decision["shadow_decision_id"]}


def load_shadow_receipt(shadow_decision_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(shadow_decision_id, str) and shadow_decision_id.startswith("psd-")):
        return None
    p = _store_dir(store_dir) / f"{shadow_decision_id}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ══════════════════════════════════════════════════════════════════════════
#  5 — Observateur (pur pass-through ; incapable de bloquer)
# ══════════════════════════════════════════════════════════════════════════

def observe_pretool_event(payload: Optional[dict], *, store_dir=None,
                          lease_store_dir=None, persist: bool = True) -> dict:
    """Classe + (optionnellement) écrit un reçu. NE RETOURNE JAMAIS de décision
    de permission. L'appelant (hook) N'ÉMET RIEN vers l'hôte et sort 0."""
    decision = classify_pretool_event(payload, lease_store_dir=lease_store_dir)
    receipt_status = None
    if persist:
        try:
            receipt_status = persist_shadow_receipt(decision, store_dir=store_dir).get("status")
        except Exception:
            receipt_status = "SHADOW_RECEIPT_SKIPPED_FAIL_OPEN"
    return {"shadow_decision": decision, "receipt_status": receipt_status,
            "hook_final_effect": "PASS_THROUGH",
            "actual_denial": False, "actual_enforcement": False}


# ══════════════════════════════════════════════════════════════════════════
#  6 — CLI mince (diagnostic / usage par le hook observateur)
# ══════════════════════════════════════════════════════════════════════════

def _main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="obsidia_pretool_shadow_v0",
        description="CG-D PreToolUse SHADOW classifier — OBSERVATIONNEL, aucun effet")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--observe-stdin", action="store_true",
                    help="lit un payload PreToolUse JSON sur stdin, écrit un reçu, sort 0")
    ap.add_argument("--no-persist", action="store_true")
    a = ap.parse_args(argv)
    if a.self_check:
        print(json.dumps({
            "PRE_TOOL_SHADOW_CLASSIFIER": PRE_TOOL_SHADOW_CLASSIFIER,
            "PRE_TOOL_SHADOW_RECEIPTS": PRE_TOOL_SHADOW_RECEIPTS,
            "PRE_TOOL_LEASE_LOOKUP_MODE": PRE_TOOL_LEASE_LOOKUP_MODE,
            "PRE_TOOL_LEASE_LOOKUP_CAN_GRANT_ACCESS": PRE_TOOL_LEASE_LOOKUP_CAN_GRANT_ACCESS,
            "SHADOW_CAN_DENY_TOOL": SHADOW_CAN_DENY_TOOL,
            "SHADOW_CAN_GRANT_TOOL": SHADOW_CAN_GRANT_TOOL,
            "SHADOW_CAN_ISSUE_LEASE": SHADOW_CAN_ISSUE_LEASE,
            "HARD_TOOL_GATE_ACTIVE": HARD_TOOL_GATE_ACTIVE,
            "LEASE_ENFORCEMENT_ACTIVE": LEASE_ENFORCEMENT_ACTIVE,
            "CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED": CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED,
            "CLAUDE_PERMISSION_MODEL_CHANGED": CLAUDE_PERMISSION_MODEL_CHANGED,
            "RAW_TOOL_ARGUMENTS_PERSISTED": RAW_TOOL_ARGUMENTS_PERSISTED,
            "TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING": TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
            "PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING":
                PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING,
            "PRE_TOOL_SHADOW_OBSERVER": PRE_TOOL_SHADOW_OBSERVER,
            "SYNTHETIC_SHADOW_OBSERVER_CANARY": SYNTHETIC_SHADOW_OBSERVER_CANARY,
            "STANDALONE_OBSERVER_INVOCATION": STANDALONE_OBSERVER_INVOCATION,
            "REAL_SHADOW_OBSERVER_CANARY": REAL_SHADOW_OBSERVER_CANARY,
            "REAL_PRETOOL_HOST_DELIVERY_PROVEN": REAL_PRETOOL_HOST_DELIVERY_PROVEN,
            "PRE_TOOL_OBSERVATION_COVERAGE": PRE_TOOL_OBSERVATION_COVERAGE,
            "AT_REFERENCE_PRETOOL_COVERAGE": AT_REFERENCE_PRETOOL_COVERAGE,
            "PRECONDITION_CGE_2_REAL_PRETOOL_HOST_DELIVERY":
                PRECONDITION_CGE_2_REAL_PRETOOL_HOST_DELIVERY,
            "shadow_verdict_domain": list(_ALL_VERDICTS),
        }, indent=2))
        return 0
    if a.observe_stdin:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            return 0                               # fail-open : rien, sortie 0
        try:
            observe_pretool_event(payload, persist=not a.no_persist)
        except Exception:
            pass                                   # fail-open observationnel
        return 0                                    # JAMAIS de sortie de permission
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
