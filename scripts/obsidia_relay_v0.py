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
import obsidia_capability_graph_v0 as _CG               # runtime capability graph (lookup only)
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
#  Statut : PROPOSITION — NON appliquée par ce checkpoint. Application =
#  décision humaine (worktree cold start / MCP tool exposure). `~/.claude*`
#  jamais muté. CLAUDE_DIRECT_REPO_MUTATION_DEFAULT reste NOT_PROVEN tant que
#  l'humain n'a pas appliqué + vérifié via le modèle de permission effectif.
CLAUDE_DIRECT_REPO_MUTATION_DEFAULT = "NOT_PROVEN"
CLAUDE_DIRECT_GIT_MUTATION_DEFAULT = "NOT_PROVEN"
CLAUDE_ARBITRARY_ENGINEERING_BASH_DEFAULT = "NOT_PROVEN"
RELAY_FIRST_HOST_PERMISSION_PROFILE_PROPOSAL_V0 = {
    "note": "PROPOSAL ONLY — not applied. Add to repo-local .claude/settings.json "
            "(tracked) OR .claude/settings.local.json (gitignored) by a human, then "
            "verify via the effective host permission model (a fresh session).",
    "apply_to": ".claude/settings.json (project-local, tracked) — merge into existing permissions.deny",
    "permissions": {
        "deny": [
            "Edit(**)", "Write(**)", "NotebookEdit(**)",
            "Bash(git add:*)", "Bash(git commit:*)", "Bash(git reset:*)",
            "Bash(git checkout:*)", "Bash(git switch:*)", "Bash(git restore:*)",
            "Bash(git rebase:*)", "Bash(git merge:*)", "Bash(git stash:*)",
            "Bash(git push:*)", "Bash(git cherry-pick:*)", "Bash(git revert:*)",
            "Bash(git apply:*)", "Bash(git worktree:*)", "Bash(git config:*)",
            "Bash(rm:*)", "Bash(mv:*)", "Bash(cp:*)", "Bash(mkdir:*)",
            "Bash(sed -i:*)", "Bash(tee:*)", "Bash(dd:*)", "Bash(truncate:*)",
            "Bash(chmod:*)", "Bash(ln:*)",
        ],
        "allow": [
            "Read", "Glob", "Grep", "Task",
            "Bash(python scripts/obsidia_relay_v0.py:*)",
            "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
            "Bash(git show:*)", "Bash(git branch:*)", "Bash(git rev-parse:*)",
        ],
    },
    "preserves": "pure conversation / reasoning / analysis / code proposals (no tool call).",
    "rationale": "Direct mutation primitives unavailable by default; governed mutation "
                 "only via the Obsidia relay + Stage 4 rail + KX108. Prefer a native "
                 "MCP tool exposure over CLI-through-Bash for the relay surface.",
    "verification_steps": [
        "cold-start a fresh Claude Code session on this worktree (not --resume)",
        "attempt Edit/Write on a scratch file -> must be DENIED by the host",
        "attempt `git add`/`git commit` -> must be DENIED",
        "Read / Grep / Glob / relay CLI -> AVAILABLE",
        "then set CLAUDE_DIRECT_REPO_MUTATION_DEFAULT = DENIED",
    ],
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
KIND_OPENJARVIS_RUNTIME_HANDSHAKE = "OPENJARVIS_RUNTIME_HANDSHAKE"
KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW = "OPENJARVIS_SIMPLE_AGENT_SHADOW"
KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1 = "OBSIDIA_NATIVE_SELF_BUILD_PHASE1"
KIND_TEST_FAMILY_RUN = "TEST_FAMILY_RUN"
KIND_LEAN_BUILD = "LEAN_BUILD"
KIND_ENGINEERING_REASONING = "ENGINEERING_REASONING"
KIND_GOVERNED_UPDATE = "GOVERNED_UPDATE_TARGET_FROM_SOURCE"
KIND_HUMAN_DECISION = "HUMAN_DECISION"
KIND_UNKNOWN = "UNKNOWN"
KIND_CONVERSATION = "CONVERSATION"
_MISSION_KINDS = (KIND_GIT_STATE_READ, KIND_OPENJARVIS_RUNTIME_HANDSHAKE,
                  KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW,
                  KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1,
                  KIND_TEST_FAMILY_RUN, KIND_LEAN_BUILD,
                  KIND_ENGINEERING_REASONING, KIND_GOVERNED_UPDATE,
                  KIND_HUMAN_DECISION, KIND_UNKNOWN, KIND_CONVERSATION)
_NATIVE_KINDS = {KIND_GIT_STATE_READ, KIND_OPENJARVIS_RUNTIME_HANDSHAKE,
                 KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW,
                  KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1,
                 KIND_TEST_FAMILY_RUN, KIND_LEAN_BUILD}
_COGNITIVE_KINDS = {KIND_ENGINEERING_REASONING}
_GOVERNED_KINDS = {KIND_GOVERNED_UPDATE}
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


def verify_relay_mission(
    mission: Optional[dict], *, store_dir=None,
    expected_relay_mission_id: Optional[str] = None,
) -> "tuple[bool, Optional[str]]":
    """V?rifie READ-ONLY une RelayMission V0 et ses liaisons CG-B persist?es.

    Aucun droit, aucune ex?cution, aucune autorit?. Le relay_mission_id historique
    n'est reconstructible que lorsque requested_outcome n'a pas ?t? tronqu? ?
    400 caract?res ; au-del?, la v?rification repose sur les cross-bindings
    persist?s MissionSubmission / RouteDecision / CapabilityRequest.
    """
    if not isinstance(mission, dict):
        return False, "RELAY_MISSION_MISSING"
    if mission.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if mission.get("domain_tag") != RELAY_DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"
    if mission.get("mission_kind") not in _MISSION_KINDS:
        return False, "MISSION_KIND_INVALID"
    if mission.get("mission_state") not in _MISSION_STATES:
        return False, "MISSION_STATE_INVALID"

    mid = mission.get("relay_mission_id")
    msid = mission.get("mission_submission_id")
    rdid = mission.get("route_decision_id")
    created = mission.get("created_at")
    outcome = mission.get("requested_outcome")

    if not (isinstance(mid, str) and mid.startswith("rmis-")):
        return False, "RELAY_MISSION_ID_MALFORMED"
    if expected_relay_mission_id is not None and mid != expected_relay_mission_id:
        return False, "RELAY_MISSION_ID_LOOKUP_MISMATCH"
    if not (isinstance(msid, str) and msid.startswith("gsub-")):
        return False, "MISSION_SUBMISSION_ID_MALFORMED"
    if not (isinstance(rdid, str) and rdid.startswith("rdec-")):
        return False, "ROUTE_DECISION_ID_MALFORMED"
    if not (isinstance(created, str) and created):
        return False, "CREATED_AT_MISSING"
    if not (isinstance(outcome, str) and outcome.strip()):
        return False, "REQUESTED_OUTCOME_MISSING"

    # Historique Relay V0 : l'ID a ?t? calcul? sur l'outcome COMPLET alors que
    # le record persiste seulement [:400]. Pour <400, identit? reconstructible.
    # Pour ==400, aucune fausse preuve : on s'appuie sur les cross-bindings CG-B.
    if len(outcome) < 400:
        expected_mid = "rmis-" + _sha(_canon({
            "o": outcome,
            "k": mission["mission_kind"],
            "s": msid,
            "t": created,
        }))[:32]
        if mid != expected_mid:
            return False, "RELAY_MISSION_ID_NOT_DERIVED"

    for b in ("is_execution_authority", "is_kx_authority", "is_human_authority"):
        if mission.get(b) is not False:
            return False, f"RELAY_MISSION_CLAIMS_AUTHORITY:{b}"
    if mission.get("claude_authority") != "NONE":
        return False, "CLAUDE_AUTHORITY_NOT_NONE"
    if mission.get("stack_operation_owner") != STACK_OPERATION_OWNER:
        return False, "STACK_OPERATION_OWNER_MISMATCH"
    if mission.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_MISMATCH"

    # Cross-binding Relay -> MissionSubmission -> RouteDecision.
    sub = _RD.load_mission_submission(msid, store_dir=store_dir)
    if not isinstance(sub, dict):
        return False, "MISSION_SUBMISSION_NOT_FOUND"
    if (
        sub.get("schema_version") != _RD.SCHEMA_VERSION
        or sub.get("domain_tag") != "OBSIDIA_CGB_MISSION_SUBMISSION_V0"
    ):
        return False, "MISSION_SUBMISSION_INVALID"
    if sub.get("is_execution_authority") is not False or sub.get("cg_b_inert") is not True:
        return False, "MISSION_SUBMISSION_NOT_INERT"
    if sub.get("mission_submission_id") != msid:
        return False, "MISSION_SUBMISSION_ID_MISMATCH"
    if sub.get("requested_outcome") != outcome:
        return False, "MISSION_SUBMISSION_OUTCOME_MISMATCH"
    sub_rd = sub.get("route_decision")
    ok_rd, why_rd = _RD.verify_route_decision(sub_rd)
    if not ok_rd:
        return False, f"MISSION_ROUTE_DECISION_INVALID:{why_rd}"
    if sub_rd.get("route_decision_id") != rdid:
        return False, "MISSION_ROUTE_DECISION_MISMATCH"

    cref = mission.get("capability_request_ref")
    if cref is not None and not (isinstance(cref, str) and cref.startswith("gcap-")):
        return False, "CAPABILITY_REQUEST_REF_MALFORMED"
    if mission["mission_state"] == MISSION_WAITING_CAPABILITY and cref is None:
        return False, "WAITING_CAPABILITY_WITHOUT_REQUEST"

    if cref is not None:
        cr = _RD.load_capability_request(cref, store_dir=store_dir)
        if not isinstance(cr, dict):
            return False, "CAPABILITY_REQUEST_NOT_FOUND"
        if (
            cr.get("schema_version") != _RD.SCHEMA_VERSION
            or cr.get("domain_tag") != "OBSIDIA_CGB_CAPABILITY_REQUEST_V0"
        ):
            return False, "CAPABILITY_REQUEST_INVALID"
        if cr.get("mission_submission_id") != msid:
            return False, "CAPABILITY_REQUEST_MISSION_MISMATCH"
        if (
            cr.get("granted") is not False
            or cr.get("grants_tool_access") is not False
            or cr.get("cg_b_inert") is not True
        ):
            return False, "CAPABILITY_REQUEST_NOT_INERT"
        cr_rd = cr.get("route_decision")
        ok_crd, why_crd = _RD.verify_route_decision(cr_rd)
        if not ok_crd:
            return False, f"CAPABILITY_ROUTE_DECISION_INVALID:{why_crd}"
        cr_core = {k: v for k, v in cr.items() if k != "capability_request_id"}
        expected_cr = "gcap-" + _RD._sha256_hex(_RD._canon(cr_core))[:32]
        if cref != expected_cr or cr.get("capability_request_id") != expected_cr:
            return False, "CAPABILITY_REQUEST_ID_NOT_DERIVED"

    cres = mission.get("capability_result_ref")
    if cres is not None and not (isinstance(cres, str) and cres.startswith("crslt-")):
        return False, "CAPABILITY_RESULT_REF_MALFORMED"

    metrics = mission.get("metrics")
    if not isinstance(metrics, dict):
        return False, "METRICS_MISSING"
    for name in ("native_route_count", "cognitive_request_count", "hold_count", "receipt_count"):
        v = metrics.get(name)
        if not (isinstance(v, int) and not isinstance(v, bool) and v >= 0):
            return False, f"METRIC_INVALID:{name}"

    for field, prefix in (("receipt_ids", "rrcpt-"), ("capability_result_ids", "crslt-")):
        values = mission.get(field)
        if not isinstance(values, list):
            return False, f"{field.upper()}_INVALID"
        if any(not (isinstance(v, str) and v.startswith(prefix)) for v in values):
            return False, f"{field.upper()}_MALFORMED"

    return True, None


def load_relay_mission(relay_mission_id: str, store_dir=None) -> Optional[dict]:
    """Recharge publiquement une RelayMission READ-ONLY, fail-closed."""
    if not (isinstance(relay_mission_id, str) and relay_mission_id.startswith("rmis-")):
        return None
    mission = _load(store_dir, relay_mission_id)
    ok, _ = verify_relay_mission(
        mission,
        store_dir=store_dir,
        expected_relay_mission_id=relay_mission_id,
    )
    return mission if ok else None


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
    tgt = mission.get("target")   # test_family_id | lean_target_id (NOMMÉ, jamais un chemin brut)
    if kind == KIND_GIT_STATE_READ:
        return _NAT.read_git_state(repo_root=mission.get("repo_root"))
    if kind == KIND_OPENJARVIS_RUNTIME_HANDSHAKE:
        return _NAT.run_openjarvis_runtime_handshake(
            str(tgt or ""),
            source_root=mission.get("repo_root"),
        )
    if kind == KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW:
        return _NAT.run_openjarvis_simple_agent_shadow(
            str(tgt or ""),
            source_root=mission.get("repo_root"),
        )
    if kind == KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1:
        relay_id = str(
            mission.get("relay_mission_id")
            or ""
        )

        session_id = (
            "jsb-"
            + relay_id.replace(
                "rmis-",
                "",
            )[:20]
        )

        return _NAT.run_obsidia_native_self_build_phase1(
            objective=(
                mission.get("requested_outcome")
                or ""
            ),
            target_path=str(
                tgt
                or ""
            ),
            repo_root=mission.get(
                "repo_root"
            ),
            session_id=session_id,
        )

    if kind == KIND_TEST_FAMILY_RUN:
        return _NAT.run_test_family_by_id(str(tgt or ""), repo_root=mission.get("repo_root"))
    if kind == KIND_LEAN_BUILD:
        return _NAT.run_lean_by_id(str(tgt or ""), lean_root=mission.get("lean_root"))
    return _NAT._evidence("UNSUPPORTED_NATIVE_KIND", False, kind=kind)


def _resolve(store_dir, mission: dict) -> dict:
    """Une passe de résolution. Ordre §8 : native → local evidence → bounded
    domain → formal → cognitive → HUMAN/HOLD. V0 implémente native + cognitive
    + HOLD ; les paliers intermédiaires retombent sur cognitive ou HOLD."""
    kind = mission["mission_kind"]
    mission["mission_state"] = MISSION_RUNNING

    # 0 — consultation du graphe de capacités (lookup, jamais une autorité)
    cap = _CG.resolve_capability_for_kind(kind)
    mission["capability_resolution"] = cap
    _emit_receipt(store_dir, mission, "CAPABILITY_RESOLVED",
                  {"capability_id": cap.get("capability_id"), "route": cap.get("route"),
                   "owner": cap.get("owner"), "grants_authority": False})
    if cap.get("gap"):
        mission["mission_state"] = MISSION_HOLD
        mission["hold_reason"] = cap["gap"]
        mission["resource_selected"] = RESOURCE_HUMAN
        mission["metrics"]["hold_count"] += 1
        _emit_receipt(store_dir, mission, "HOLD_OPENED",
                      {"reason": cap["gap"], "detail": cap.get("reason")})
        return mission

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

    # 2bis — apply gouverné (Stage 4 rail) : le relais ORCHESTRE un HOLD pour
    #  l'autorisation humaine de l'EAH exact ; il NE construit PAS l'enveloppe,
    #  NE forge PAS l'EAH/HMA, NE touche PAS KX108_PRE/POST. UPDATE_TARGET_FROM_SOURCE
    #  UNIQUEMENT (pas de CREATE/DELETE/MOVE/RENAME — Stage 5).
    if kind in _GOVERNED_KINDS:
        mission["mission_state"] = MISSION_HOLD
        mission["hold_reason"] = "HUMAN_EAH_AUTHORIZATION_REQUIRED"
        mission["resource_selected"] = RESOURCE_HUMAN
        mission["governed_apply_route"] = "STAGE4_GOVERNED_RAIL"
        mission["governed_apply_operation"] = MAX_GOVERNED_MUTATION_OPERATION_V0
        mission["governed_apply_relay_builds_envelope"] = False
        mission["metrics"]["hold_count"] += 1
        _emit_receipt(store_dir, mission, "HOLD_OPENED",
                      {"reason": "HUMAN_EAH_AUTHORIZATION_REQUIRED",
                       "governed_apply_route": "STAGE4_GOVERNED_RAIL",
                       "operation": MAX_GOVERNED_MUTATION_OPERATION_V0,
                       "relay_constructs_envelope": False,
                       "relay_mints_eah_or_hma": False})
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


def relay_capability_graph() -> dict:
    """Snapshot READ-ONLY du graphe de capacités canonique (lookup, jamais autorité)."""
    return _CG.graph_snapshot()


def relay_resolve_capability(mission_kind: str) -> dict:
    return _CG.resolve_capability_for_kind(mission_kind)


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
            "CLAUDE_DIRECT_REPO_MUTATION_DEFAULT": CLAUDE_DIRECT_REPO_MUTATION_DEFAULT,
            "CLAUDE_DIRECT_GIT_MUTATION_DEFAULT": CLAUDE_DIRECT_GIT_MUTATION_DEFAULT,
            "CLAUDE_ARBITRARY_ENGINEERING_BASH_DEFAULT": CLAUDE_ARBITRARY_ENGINEERING_BASH_DEFAULT,
            "CAPABILITY_GRAPH": "ACTIVE",
            "capability_ids": list(_CG.capability_ids()),
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
