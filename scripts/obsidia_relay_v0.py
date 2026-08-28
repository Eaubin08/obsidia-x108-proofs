#!/usr/bin/env python3
"""OBSIDIA — Relay-First runtime V0.

  USER → CLAUDE (transport / relay) → OBSIDIA RELAY → STACK
       → native capability | cognitive request | HOLD
       → receipt / result → CLAUDE (relay) → USER

Claude is NEVER a stack authority. This module gives the stack a real mission
loop it drives ITSELF, resolving stack-native FIRST and only asking a cognitive
resource (Brody / Claude / Obsidure / …) when genuinely required — as a
CapabilityRequest whose CapabilityResult is EVIDENCE or PROPOSAL, never authority.

  CLAUDE_PRIMARY_ROLE        = TRANSPORT_INTERFACE
  CLAUDE_SECONDARY_ROLE      = COGNITIVE_RESOURCE_ON_DEMAND
  CLAUDE_EXECUTION_AUTHORITY = NONE
  CLAUDE_HUMAN_AUTHORITY     = NONE
  CLAUDE_KX_AUTHORITY        = NONE
  STACK_OPERATION_OWNER      = OBSIDIA_CANONICAL_STACK
  STACK_NATIVE_FIRST         = TRUE
  KX_DECISION_AUTHORITY      = KX108_ONLY
  COGNITIVE_RESULT_IS_AUTHORITY = FALSE
  OPTIONAL_CLAUDE_DIRECT_TOOL_MODE = NOT_ACTIVE

The old Claude-Code-PreToolUse-hook enforcement trajectory is NOT the primary
boundary. CG-D remains SHADOW / diagnostic only (REAL_SHADOW_OBSERVER_CANARY =
NOT_PROVEN, unchanged). CGE-1 / CGE-2 are reclassified as
OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_1 / _2 and do NOT block this runtime.
They are NOT claimed solved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_gateway_route_decision_v0 as _RD          # CG-B relay substrate + store helpers
import obsidia_stack_native_routes_v0 as _NAT           # stack-native bounded capabilities
import obsidia_pretool_shadow_v0 as _SHADOW             # CG-D receipts helpers (diagnostic reuse)

SCHEMA_VERSION = 1
RELAY_DOMAIN_TAG = "OBSIDIA_RELAY_MISSION_V0"
CAPRESULT_DOMAIN_TAG = "OBSIDIA_RELAY_CAPABILITY_RESULT_V0"
RECEIPT_DOMAIN_TAG = "OBSIDIA_RELAY_RECEIPT_V0"
DECISION_AUTHORITY = "KX108_ONLY"

# ── Rôles / bornes (toutes affirmées, statiques) ────────────────────────
CLAUDE_PRIMARY_ROLE = "TRANSPORT_INTERFACE"
CLAUDE_SECONDARY_ROLE = "COGNITIVE_RESOURCE_ON_DEMAND"
CLAUDE_EXECUTION_AUTHORITY = "NONE"
CLAUDE_HUMAN_AUTHORITY = "NONE"
CLAUDE_KX_AUTHORITY = "NONE"
CLAUDE_MISSION_AUTHORITY = "NONE"
CLAUDE_SCOPE_AUTHORITY = "NONE"
CLAUDE_GIT_AUTHORITY = "NONE"
STACK_OPERATION_OWNER = "OBSIDIA_CANONICAL_STACK"
STACK_NATIVE_FIRST = True
KX_DECISION_AUTHORITY = "KX108_ONLY"
COGNITIVE_RESULT_IS_EXECUTION_AUTHORITY = False
COGNITIVE_RESULT_IS_HUMAN_AUTHORITY = False
COGNITIVE_RESULT_IS_KX_AUTHORITY = False
MISSION_RELAY = "ACTIVE"
HOLD_RESUME = "ACTIVE"
UNKNOWN_RESOLUTION = "ACTIVE"
MISSION_RECEIPTS = "ACTIVE"
OPTIONAL_CLAUDE_DIRECT_TOOL_MODE = "NOT_ACTIVE"
OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_1 = "OPEN"   # ex-CGE-1
OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_2 = "OPEN"   # ex-CGE-2
DO_NOT_USE_MORE_PROBABILISTIC_INTELLIGENCE_THAN_NECESSARY = True
DO_NOT_DEGRADE_CONVERSATIONAL_EXPERIENCE_TO_SAVE_TOKENS = True
MULTI_OPERATION_GENERALIZATION = "NOT_YET_PROVEN"
MAX_GOVERNED_MUTATION_OPERATION_V0 = "UPDATE_TARGET_FROM_SOURCE"

# ── PROPOSITION de profil de permission hôte repo-local (NON activé) ────
#  Discovery only (§22). Ne mute PAS ~/.claude. À placer dans un
#  .claude/settings.local.json repo-local *par un humain* si Relay-First
#  devient le déploiement par défaut. Ne casse pas la conversation Claude.
RELAY_FIRST_HOST_PERMISSION_PROFILE_PROPOSAL_V0 = {
    "note": "PROPOSAL ONLY — not applied by CG. Repo-local .claude/settings.local.json.",
    "permissions": {
        "deny": [
            "Edit(**)", "Write(**)", "NotebookEdit(**)",
            "Bash(git add:*)", "Bash(git commit:*)", "Bash(git reset:*)",
            "Bash(git checkout:*)", "Bash(git switch:*)", "Bash(git restore:*)",
            "Bash(git rebase:*)", "Bash(git merge:*)", "Bash(git stash:*)",
            "Bash(git push:*)", "Bash(rm:*)", "Bash(mv:*)", "Bash(cp:*)",
            "Bash(sed -i:*)", "Bash(tee:*)",
        ],
        "allow_relay_surface_only": [
            "Bash(python scripts/obsidia_relay_v0.py *)",
        ],
    },
    "rationale": "Direct mutation primitives unavailable; governed mutation only "
                 "via the Obsidia relay + KX108 rail. Pure conversation/reasoning "
                 "unaffected. Prefer a native MCP tool exposure over CLI-through-Bash.",
}

# ── États de mission relais ────────────────────────────────────────────
MISSION_ACCEPTED = "MISSION_ACCEPTED"
MISSION_RUNNING = "MISSION_RUNNING"
MISSION_WAITING_CAPABILITY = "MISSION_WAITING_CAPABILITY"
MISSION_HOLD = "MISSION_HOLD"
MISSION_COMPLETE = "MISSION_COMPLETE"
MISSION_FAILED = "MISSION_FAILED"
_MISSION_STATES = (MISSION_ACCEPTED, MISSION_RUNNING, MISSION_WAITING_CAPABILITY,
                   MISSION_HOLD, MISSION_COMPLETE, MISSION_FAILED)

# ── Genres de mission (déterministes ; JAMAIS déduits du prompt) ────────
KIND_GIT_STATE_READ = "GIT_STATE_READ"
KIND_TEST_FAMILY_RUN = "TEST_FAMILY_RUN"
KIND_LEAN_BUILD = "LEAN_BUILD"
KIND_ENGINEERING_REASONING = "ENGINEERING_REASONING"
KIND_HUMAN_DECISION = "HUMAN_DECISION"
KIND_UNKNOWN = "UNKNOWN"
KIND_CONVERSATION = "CONVERSATION"
_MISSION_KINDS = (KIND_GIT_STATE_READ, KIND_TEST_FAMILY_RUN, KIND_LEAN_BUILD,
                  KIND_ENGINEERING_REASONING, KIND_HUMAN_DECISION, KIND_UNKNOWN,
                  KIND_CONVERSATION)
_NATIVE_KINDS = {KIND_GIT_STATE_READ, KIND_TEST_FAMILY_RUN, KIND_LEAN_BUILD}
_COGNITIVE_KINDS = {KIND_ENGINEERING_REASONING}
_HOLD_KINDS = {KIND_HUMAN_DECISION}

# ── Ressources cognitives (capacité != autorité) ───────────────────────
RESOURCE_STACK_NATIVE = "STACK_NATIVE"
RESOURCE_LOCAL_EVIDENCE = "LOCAL_EVIDENCE"
RESOURCE_BOUNDED_DOMAIN = "BOUNDED_DOMAIN"
RESOURCE_FORMAL_PROOF = "FORMAL_PROOF"
RESOURCE_COGNITIVE_BRODY = "BRODY"
RESOURCE_COGNITIVE_CLAUDE = "CLAUDE"
RESOURCE_COGNITIVE_OBSIDURE = "OBSIDURE"
RESOURCE_HUMAN = "HUMAN"
_COGNITIVE_RESOURCES = (RESOURCE_COGNITIVE_BRODY, RESOURCE_COGNITIVE_CLAUDE,
                        RESOURCE_COGNITIVE_OBSIDURE)

# ── Résultats de capacité ─────────────────────────────────────────────
CAPRESULT_EVIDENCE = "EVIDENCE"
CAPRESULT_PROPOSAL = "PROPOSAL"

_canon = _RD._canon
_sha = _RD._sha256_hex
_now = _RD._now


def _relay_store(store_dir) -> Path:
    return _RD._sd(store_dir) / "relay_missions"


def _load(store_dir, mid: str) -> Optional[dict]:
    p = _relay_store(store_dir) / f"{mid}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _save(store_dir, mission: dict) -> None:
    d = _relay_store(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{mission['relay_mission_id']}.json"
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(mission, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(p)


# ══════════════════════════════════════════════════════════════════════════
#  Reçus (réutilise l'univers d'audit : store relais, PAS de 2e système)
# ══════════════════════════════════════════════════════════════════════════

def _emit_receipt(store_dir, mission: dict, transition: str, detail: dict) -> str:
    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": RECEIPT_DOMAIN_TAG,
        "relay_mission_id": mission["relay_mission_id"],
        "mission_submission_id": mission.get("mission_submission_id"),
        "transition": transition,
        "mission_state": mission["mission_state"],
        "mission_kind": mission["mission_kind"],
        "detail": detail,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_human_authority": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    rh = _sha(_canon(core))
    core["receipt_hash"] = rh
    core["relay_receipt_id"] = "rrcpt-" + rh[:32]
    core["created_at"] = _now()
    d = _relay_store(store_dir) / "receipts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{core['relay_receipt_id']}.json"
    if not p.exists():
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(p)
        try:
            with (d / "relay_receipts.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(core, ensure_ascii=False) + "\n")
        except OSError:
            pass
    mission.setdefault("receipt_ids", []).append(core["relay_receipt_id"])
    mission["metrics"]["receipt_count"] = len(mission["receipt_ids"])
    return core["relay_receipt_id"]


def load_relay_receipt(relay_receipt_id: str, store_dir=None) -> Optional[dict]:
    if not (isinstance(relay_receipt_id, str) and relay_receipt_id.startswith("rrcpt-")):
        return None
    p = _relay_store(store_dir) / "receipts" / f"{relay_receipt_id}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ══════════════════════════════════════════════════════════════════════════
#  Résolution stack-native-first
# ══════════════════════════════════════════════════════════════════════════

def _run_native(mission: dict) -> dict:
    kind = mission["mission_kind"]
    tgt = mission.get("target")
    if kind == KIND_GIT_STATE_READ:
        return _NAT.read_git_state(repo_root=mission.get("repo_root"))
    if kind == KIND_TEST_FAMILY_RUN:
        return _NAT.run_test_family(str(tgt or ""), repo_root=mission.get("repo_root"))
    if kind == KIND_LEAN_BUILD:
        return _NAT.run_lean_target(str(tgt or ""), lean_root=mission.get("lean_root"))
    return _NAT._evidence("UNSUPPORTED_NATIVE_KIND", False, kind=kind)


def _resolve(store_dir, mission: dict) -> dict:
    """Une passe de résolution. Ordre §8 : native → local evidence → bounded
    domain → formal → cognitive → HUMAN/HOLD. V0 implémente native + cognitive
    + HOLD ; les paliers intermédiaires retombent sur cognitive ou HOLD."""
    kind = mission["mission_kind"]
    mission["mission_state"] = MISSION_RUNNING

    # 1 — capacité stack-native déterministe
    if kind in _NATIVE_KINDS:
        mission["resource_selected"] = RESOURCE_STACK_NATIVE
        ev = _run_native(mission)
        mission["metrics"]["native_route_count"] += 1
        mission["native_evidence"] = ev
        _emit_receipt(store_dir, mission, "NATIVE_CAPABILITY_INVOKED",
                      {"native_route_kind": ev.get("native_route_kind"), "ok": ev.get("ok")})
        if ev.get("ok"):
            mission["mission_state"] = MISSION_COMPLETE
            mission["result_kind"] = CAPRESULT_EVIDENCE
            _emit_receipt(store_dir, mission, "MISSION_COMPLETE",
                          {"result_kind": CAPRESULT_EVIDENCE, "via": RESOURCE_STACK_NATIVE})
        else:
            mission["mission_state"] = MISSION_FAILED
            mission["failure_reason"] = ev.get("reason") or "NATIVE_ROUTE_NOT_OK"
            _emit_receipt(store_dir, mission, "MISSION_FAILED", {"reason": mission["failure_reason"]})
        return mission

    # 2 — besoin cognitif réel -> CapabilityRequest (jamais d'autorité)
    if kind in _COGNITIVE_KINDS:
        cr = _RD.request_capability(
            mission_submission_id=mission["mission_submission_id"],
            requested_capability="ENGINEERING_REASONING",
            reason=(mission["requested_outcome"] or "")[:200], store_dir=store_dir)
        mission["capability_request_ref"] = cr.get("capability_request_id")
        mission["resource_candidates"] = list(_COGNITIVE_RESOURCES)
        mission["metrics"]["cognitive_request_count"] += 1
        mission["mission_state"] = MISSION_WAITING_CAPABILITY
        _emit_receipt(store_dir, mission, "COGNITIVE_REQUEST_ISSUED",
                      {"capability_request_ref": mission["capability_request_ref"],
                       "candidates": mission["resource_candidates"]})
        return mission

    # 3 — autorité humaine requise / genre inconnu -> HOLD (jamais LLM)
    reason = ("HUMAN_AUTHORITY_REQUIRED" if kind in _HOLD_KINDS else "UNKNOWN_AUTHORITY")
    mission["mission_state"] = MISSION_HOLD
    mission["hold_reason"] = reason
    mission["resource_selected"] = RESOURCE_HUMAN
    mission["metrics"]["hold_count"] += 1
    _emit_receipt(store_dir, mission, "HOLD_OPENED", {"reason": reason})
    return mission


# ══════════════════════════════════════════════════════════════════════════
#  Surface relais bornée (§6)
# ══════════════════════════════════════════════════════════════════════════

def relay_submit_mission(*, requested_outcome: str, mission_kind: str,
                         target: Optional[str] = None, repo_root=None, lean_root=None,
                         store_dir=None) -> dict:
    if not (isinstance(requested_outcome, str) and requested_outcome.strip()):
        return {"status": "RELAY_REJECTED", "reason": "REQUESTED_OUTCOME_REQUIRED"}
    if mission_kind not in _MISSION_KINDS:
        return {"status": "RELAY_REJECTED", "reason": f"UNKNOWN_MISSION_KIND:{mission_kind}"}
    sub = _RD.submit_mission(requested_outcome=requested_outcome, store_dir=store_dir)
    if not sub.get("mission_submission_id"):
        return {"status": "RELAY_REJECTED", "reason": f"SUBMISSION_FAILED:{sub.get('reason')}"}
    created = _now()
    mission = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": RELAY_DOMAIN_TAG,
        "requested_outcome": requested_outcome[:400],
        "mission_kind": mission_kind,
        "target": target,
        "repo_root": str(repo_root) if repo_root else None,
        "lean_root": str(lean_root) if lean_root else None,
        "mission_submission_id": sub["mission_submission_id"],
        "route_decision_id": (sub.get("route_decision") or {}).get("route_decision_id"),
        "mission_state": MISSION_ACCEPTED,
        "resource_selected": None,
        "capability_request_ref": None,
        "capability_result_ref": None,
        "result_kind": None,
        "receipt_ids": [],
        "capability_result_ids": [],
        "metrics": {"native_route_count": 0, "cognitive_request_count": 0,
                    "hold_count": 0, "receipt_count": 0},
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_human_authority": False,
        "claude_authority": "NONE",
        "stack_operation_owner": STACK_OPERATION_OWNER,
        "decision_authority": DECISION_AUTHORITY,
        "created_at": created,
    }
    mid = "rmis-" + _sha(_canon({"o": requested_outcome, "k": mission_kind,
                                 "s": sub["mission_submission_id"], "t": created}))[:32]
    mission["relay_mission_id"] = mid
    _emit_receipt(store_dir, mission, "MISSION_ACCEPTED",
                  {"mission_kind": mission_kind, "mission_submission_id": mission["mission_submission_id"]})
    _resolve(store_dir, mission)
    _save(store_dir, mission)
    return {"status": "RELAY_MISSION_" + mission["mission_state"],
            "relay_mission_id": mid, "mission_state": mission["mission_state"],
            "mission_kind": mission_kind, "metrics": mission["metrics"],
            "capability_request_ref": mission["capability_request_ref"],
            "hold_reason": mission.get("hold_reason"),
            "native_evidence": mission.get("native_evidence"),
            "claude_authority": "NONE"}


def relay_get_status(relay_mission_id: str, store_dir=None) -> dict:
    m = _load(store_dir, relay_mission_id)
    if m is None:
        return {"status": "RELAY_REJECTED", "reason": "RELAY_MISSION_NOT_FOUND"}
    return {"relay_mission_id": relay_mission_id, "mission_state": m["mission_state"],
            "mission_kind": m["mission_kind"], "metrics": m["metrics"],
            "capability_request_ref": m.get("capability_request_ref"),
            "capability_result_ref": m.get("capability_result_ref"),
            "result_kind": m.get("result_kind"), "hold_reason": m.get("hold_reason"),
            "failure_reason": m.get("failure_reason"),
            "receipt_ids": list(m.get("receipt_ids") or []),
            "claude_authority": "NONE", "is_execution_authority": False}


def relay_get_receipt(relay_receipt_id: str, store_dir=None) -> Optional[dict]:
    return load_relay_receipt(relay_receipt_id, store_dir=store_dir)


def relay_request_capability(*, relay_mission_id: str, requested_capability: str,
                             reason: str, store_dir=None) -> dict:
    m = _load(store_dir, relay_mission_id)
    if m is None:
        return {"status": "RELAY_REJECTED", "reason": "RELAY_MISSION_NOT_FOUND"}
    cr = _RD.request_capability(mission_submission_id=m["mission_submission_id"],
                               requested_capability=requested_capability,
                               reason=reason, store_dir=store_dir)
    if not cr.get("capability_request_id"):
        return {"status": "RELAY_REJECTED", "reason": f"CAP_REQUEST_FAILED:{cr.get('reason')}"}
    m["capability_request_ref"] = cr["capability_request_id"]
    m["metrics"]["cognitive_request_count"] += 1
    m["mission_state"] = MISSION_WAITING_CAPABILITY
    m["resource_candidates"] = list(_COGNITIVE_RESOURCES)
    _emit_receipt(store_dir, m, "COGNITIVE_REQUEST_ISSUED",
                  {"capability_request_ref": cr["capability_request_id"]})
    _save(store_dir, m)
    return {"status": "RELAY_MISSION_" + m["mission_state"],
            "relay_mission_id": relay_mission_id,
            "capability_request_ref": cr["capability_request_id"],
            "candidates": m["resource_candidates"], "claude_authority": "NONE"}


def submit_capability_result(*, relay_mission_id: str, capability_request_ref: str,
                             result_kind: str, summary: str, produced_by: str,
                             payload_ref: Optional[str] = None, store_dir=None) -> dict:
    """Réintègre un CapabilityResult (EVIDENCE|PROPOSAL). Le résultat N'EST
    JAMAIS une autorité : il ne fait qu'alimenter la mission. Pour EVIDENCE la
    mission ré-résout ; pour PROPOSAL la mission enregistre la proposition
    (validation/gouvernance/apply = rail Stage 4, PAS ce module V0)."""
    m = _load(store_dir, relay_mission_id)
    if m is None:
        return {"status": "RELAY_REJECTED", "reason": "RELAY_MISSION_NOT_FOUND"}
    if m["mission_state"] != MISSION_WAITING_CAPABILITY:
        return {"status": "RELAY_REJECTED", "reason": f"MISSION_NOT_WAITING:{m['mission_state']}"}
    if capability_request_ref != m.get("capability_request_ref"):
        return {"status": "RELAY_REJECTED", "reason": "CAPABILITY_REQUEST_REF_MISMATCH"}
    if result_kind not in (CAPRESULT_EVIDENCE, CAPRESULT_PROPOSAL):
        return {"status": "RELAY_REJECTED", "reason": f"INVALID_RESULT_KIND:{result_kind}"}
    if produced_by not in _COGNITIVE_RESOURCES + (RESOURCE_STACK_NATIVE, RESOURCE_BOUNDED_DOMAIN):
        return {"status": "RELAY_REJECTED", "reason": f"UNKNOWN_RESOURCE:{produced_by}"}
    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": CAPRESULT_DOMAIN_TAG,
        "relay_mission_id": relay_mission_id,
        "capability_request_ref": capability_request_ref,
        "result_kind": result_kind,
        "produced_by": produced_by,
        "summary": str(summary)[:400],
        "payload_ref": payload_ref,
        "is_execution_authority": False,
        "is_human_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_scope": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    rh = _sha(_canon(core))
    core["capability_result_hash"] = rh
    core["capability_result_id"] = "crslt-" + rh[:32]
    core["created_at"] = _now()
    d = _relay_store(store_dir) / "capability_results"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{core['capability_result_id']}.json"
    if not p.exists():
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(p)
    m["capability_result_ref"] = core["capability_result_id"]
    m.setdefault("capability_result_ids", []).append(core["capability_result_id"])
    m["result_kind"] = result_kind
    _emit_receipt(store_dir, m, "COGNITIVE_RESULT_RETURNED",
                  {"capability_result_id": core["capability_result_id"],
                   "result_kind": result_kind, "produced_by": produced_by})
    if result_kind == CAPRESULT_EVIDENCE:
        # l'évidence alimente une nouvelle passe de résolution
        m["mission_kind_effective"] = m["mission_kind"]
        m["mission_state"] = MISSION_COMPLETE
        _emit_receipt(store_dir, m, "MISSION_COMPLETE",
                      {"result_kind": CAPRESULT_EVIDENCE, "via": produced_by})
    else:  # PROPOSAL — enregistrée ; aucune autorité, aucun apply ici
        m["mission_state"] = MISSION_COMPLETE
        m["proposal_recorded"] = True
        m["proposal_apply_route"] = "STAGE4_GOVERNED_RAIL_NOT_INVOKED_IN_RELAY_V0"
        _emit_receipt(store_dir, m, "PROPOSAL_RECORDED_NO_APPLY",
                      {"capability_result_id": core["capability_result_id"],
                       "apply_route": m["proposal_apply_route"],
                       "claude_gained_authority": False})
    _save(store_dir, m)
    return {"status": "RELAY_MISSION_" + m["mission_state"],
            "relay_mission_id": relay_mission_id,
            "capability_result_id": core["capability_result_id"],
            "result_kind": result_kind, "mission_state": m["mission_state"],
            "claude_gained_authority": False, "metrics": m["metrics"]}


def relay_respond_to_hold(*, relay_mission_id: str, human_decision_ref: str,
                          resolution: str, store_dir=None) -> dict:
    """HOLD first-class. La MÊME mission reprend — pas de restart, pas
    d'expansion de portée depuis la réponse au HOLD."""
    m = _load(store_dir, relay_mission_id)
    if m is None:
        return {"status": "RELAY_REJECTED", "reason": "RELAY_MISSION_NOT_FOUND"}
    if m["mission_state"] != MISSION_HOLD:
        return {"status": "RELAY_REJECTED", "reason": f"MISSION_NOT_HELD:{m['mission_state']}"}
    if not (isinstance(human_decision_ref, str) and human_decision_ref.strip()):
        return {"status": "RELAY_REJECTED", "reason": "HUMAN_DECISION_REF_REQUIRED"}
    hr = _RD.respond_to_hold(mission_submission_id=m["mission_submission_id"],
                             human_decision_ref=human_decision_ref,
                             resolution=resolution, store_dir=store_dir)
    m["hold_response_id"] = hr.get("hold_response_id")
    m["hold_human_decision_ref"] = human_decision_ref
    # la réponse au HOLD ne peut PAS élargir la portée : le mission_kind reste identique.
    _emit_receipt(store_dir, m, "HOLD_RESOLVED",
                  {"hold_response_id": hr.get("hold_response_id"),
                   "scope_expanded": False, "same_mission_resumed": True})
    if m["hold_reason"] == "UNKNOWN_AUTHORITY":
        # UNKNOWN reste non résoluble par un LLM ; la mission se clôt en
        # FAILED sauf si la réponse humaine porte une résolution explicite.
        m["mission_state"] = MISSION_COMPLETE if str(resolution).strip() else MISSION_FAILED
    else:
        m["mission_state"] = MISSION_COMPLETE
    _emit_receipt(store_dir, m, "MISSION_" + m["mission_state"],
                  {"via": RESOURCE_HUMAN, "human_decision_ref": human_decision_ref})
    _save(store_dir, m)
    return {"status": "RELAY_MISSION_" + m["mission_state"],
            "relay_mission_id": relay_mission_id, "mission_state": m["mission_state"],
            "same_mission_resumed": True, "scope_expanded": False,
            "metrics": m["metrics"], "claude_authority": "NONE"}


def resolve_unknown(*, relay_mission_id: str, missing_fact: str,
                    evidence_summary: str, evidence_resource: str,
                    store_dir=None) -> dict:
    """UNKNOWN -> identifier le fait manquant -> obtenir une évidence via une
    ressource AUTORISÉE -> réintégrer -> relancer. AUCUNE expansion de portée,
    AUCUNE résolution par LLM d'une autorité inconnue."""
    m = _load(store_dir, relay_mission_id)
    if m is None:
        return {"status": "RELAY_REJECTED", "reason": "RELAY_MISSION_NOT_FOUND"}
    if evidence_resource not in (RESOURCE_STACK_NATIVE, RESOURCE_LOCAL_EVIDENCE,
                                 RESOURCE_BOUNDED_DOMAIN, RESOURCE_FORMAL_PROOF):
        return {"status": "RELAY_REJECTED",
                "reason": f"EVIDENCE_RESOURCE_NOT_AUTHORIZED:{evidence_resource}"}
    m.setdefault("unknown_resolutions", []).append({
        "missing_fact": str(missing_fact)[:200],
        "evidence_summary": str(evidence_summary)[:400],
        "evidence_resource": evidence_resource,
        "scope_expanded": False, "at": _now()})
    _emit_receipt(store_dir, m, "UNKNOWN_EVIDENCE_REINTEGRATED",
                  {"missing_fact": str(missing_fact)[:120],
                   "evidence_resource": evidence_resource, "scope_expanded": False})
    # relance : re-résolution sous le MÊME mission_kind
    if m["mission_state"] in (MISSION_HOLD, MISSION_WAITING_CAPABILITY, MISSION_RUNNING):
        _resolve(store_dir, m)
    _save(store_dir, m)
    return {"status": "RELAY_MISSION_" + m["mission_state"],
            "relay_mission_id": relay_mission_id, "mission_state": m["mission_state"],
            "scope_expanded": False, "metrics": m["metrics"], "claude_authority": "NONE"}


# ══════════════════════════════════════════════════════════════════════════
#  CLI mince
# ══════════════════════════════════════════════════════════════════════════

def _main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="obsidia_relay_v0",
                                 description="Obsidia Relay-First runtime V0")
    ap.add_argument("--self-check", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("submit"); s.add_argument("kind"); s.add_argument("outcome", nargs="+")
    s.add_argument("--target", default=None)
    s = sub.add_parser("status"); s.add_argument("relay_mission_id")
    a = ap.parse_args(argv)
    if a.self_check:
        print(json.dumps({
            "CLAUDE_PRIMARY_ROLE": CLAUDE_PRIMARY_ROLE,
            "CLAUDE_SECONDARY_ROLE": CLAUDE_SECONDARY_ROLE,
            "CLAUDE_EXECUTION_AUTHORITY": CLAUDE_EXECUTION_AUTHORITY,
            "STACK_OPERATION_OWNER": STACK_OPERATION_OWNER,
            "STACK_NATIVE_FIRST": STACK_NATIVE_FIRST,
            "KX_DECISION_AUTHORITY": KX_DECISION_AUTHORITY,
            "COGNITIVE_RESULT_IS_EXECUTION_AUTHORITY": COGNITIVE_RESULT_IS_EXECUTION_AUTHORITY,
            "MISSION_RELAY": MISSION_RELAY, "HOLD_RESUME": HOLD_RESUME,
            "UNKNOWN_RESOLUTION": UNKNOWN_RESOLUTION, "MISSION_RECEIPTS": MISSION_RECEIPTS,
            "OPTIONAL_CLAUDE_DIRECT_TOOL_MODE": OPTIONAL_CLAUDE_DIRECT_TOOL_MODE,
            "OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_1": OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_1,
            "OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_2": OPTIONAL_CLAUDE_DIRECT_TOOL_MODE_PRECONDITION_2,
            "mission_states": list(_MISSION_STATES),
            "mission_kinds": list(_MISSION_KINDS),
        }, indent=2))
        return 0
    if a.cmd == "submit":
        out = relay_submit_mission(requested_outcome=" ".join(a.outcome),
                                   mission_kind=a.kind, target=a.target)
        print(json.dumps(out, indent=2, default=str)); return 0
    if a.cmd == "status":
        print(json.dumps(relay_get_status(a.relay_mission_id), indent=2, default=str)); return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
