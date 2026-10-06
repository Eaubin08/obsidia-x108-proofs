#!/usr/bin/env python3
"""OBSIDIA — Runtime Capability Graph V0 (Relay-First).

One canonical, read-only description of every capability the Relay-First runtime
can route a mission requirement to:

  mission requirement → capability lookup → native route | cognitive resource
                        | formal resource | governed-rail | HOLD.

Capability != authority. Every entry is a DESCRIPTION; it grants nothing.
No second mission system, no second gateway — this is a lookup table the
existing relay (obsidia_relay_v0) and native routes (obsidia_stack_native_routes_v0)
consult.

  CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY = FALSE
  CAPABILITY_GRAPH_IS_KX_AUTHORITY        = FALSE
  KX_DECISION_AUTHORITY                   = KX108_ONLY
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_stack_native_routes_v0 as _NAT

SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CAPABILITY_GRAPH_V0"
DECISION_AUTHORITY = "KX108_ONLY"

CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY = False
CAPABILITY_GRAPH_IS_KX_AUTHORITY = False
KX_DECISION_AUTHORITY = "KX108_ONLY"

# ── owners / authority classes / modes (vocabulaire fermé) ────────────
OWNER_OBSIDIA_STACK = "OBSIDIA_STACK"
OWNER_OPENJARVIS_RUNTIME = "OPENJARVIS_RUNTIME"
OWNER_STAGE4_RAIL = "OBSIDIA_STACK/STAGE4_RAIL"
OWNER_COGNITIVE_RESOURCE = "COGNITIVE_RESOURCE"
OWNER_FORMAL = "OBSIDIA_STACK/FORMAL"
OWNER_HUMAN = "HUMAN"

AUTHORITY_NONE = "NONE"
AUTHORITY_KX108_ONLY = "KX108_ONLY"
AUTHORITY_HUMAN = "HUMAN"

MODE_DETERMINISTIC_READ_ONLY = "DETERMINISTIC_READ_ONLY"
MODE_DETERMINISTIC_BOUNDED = "DETERMINISTIC_BOUNDED"
MODE_GOVERNED_RAIL = "GOVERNED_RAIL"
MODE_COGNITIVE = "COGNITIVE"
MODE_HUMAN_HOLD = "HUMAN_HOLD"

RW_READ = "READ"
RW_WRITE_GOVERNED = "WRITE_GOVERNED"
RW_NONE = "NONE"

ROUTE_NATIVE = "STACK_NATIVE_ROUTE"
ROUTE_COGNITIVE_REQUEST = "COGNITIVE_CAPABILITY_REQUEST"
ROUTE_STAGE4_GOVERNED = "STAGE4_GOVERNED_RAIL"
ROUTE_HOLD = "HOLD"


def _cap(capability_id, *, family, owner, mode, authority_class, rw, route,
         input_shape, availability, proof_status, notes="") -> dict:
    return {
        "capability_id": capability_id,
        "family": family,
        "owner": owner,
        "mode": mode,
        "authority_class": authority_class,
        "read_write": rw,
        "route": route,
        "accepted_input_shape": input_shape,
        "availability": availability,
        "proof_test_status": proof_status,
        "is_execution_authority": (authority_class == AUTHORITY_KX108_ONLY and False),
        "grants_authority": False,
        "notes": notes,
    }


# ── Le graphe canonique ───────────────────────────────────────────────
_GRAPH: "dict[str, dict]" = {
    "GIT_STATE_READ": _cap(
        "GIT_STATE_READ", family="GIT", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"repo_root": "optional path"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_stack_native_routes_v0.read_git_state — read-only git facts."),
    "OPENJARVIS_RUNTIME_HANDSHAKE": _cap(
        "OPENJARVIS_RUNTIME_HANDSHAKE",
        family="EXTERNAL_RUNTIME",
        owner=OWNER_OPENJARVIS_RUNTIME,
        mode=MODE_DETERMINISTIC_READ_ONLY,
        authority_class=AUTHORITY_NONE,
        rw=RW_READ,
        route=ROUTE_NATIVE,
        input_shape={
            "repo_root": "configured OpenJarvis source only",
            "target": "configured exact OpenJarvis SHA only",
        },
        availability="SHADOW_HANDSHAKE_ONLY",
        proof_status="V02_SHADOW_HANDSHAKE_PROVED",
        notes=(
            "Pinned external runtime identity and surface discovery only. "
            "No OpenJarvis agent, tool, scheduler, memory or authority."
        ),
    ),
    "OPENJARVIS_SIMPLE_AGENT_SHADOW": _cap(
        "OPENJARVIS_SIMPLE_AGENT_SHADOW",
        family="EXTERNAL_RUNTIME_AGENT_SHADOW",
        owner=OWNER_OPENJARVIS_RUNTIME,
        mode=MODE_DETERMINISTIC_BOUNDED,
        authority_class=AUTHORITY_NONE,
        rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={
            "repo_root": "configured OpenJarvis source only",
            "target": "input text, max 2000 chars",
        },
        availability="SHADOW_DETERMINISTIC_ENGINE_ONLY",
        proof_status="V04_REAL_AGENT_CODE_NO_REAL_MODEL",
        notes=(
            "Executes real OpenJarvis SimpleAgent code with an "
            "Obsidia deterministic engine. No real model, tools, memory, "
            "scheduler, network, external effect or authority."
        ),
    ),
    "OBSIDIA_NATIVE_SELF_BUILD_PHASE1": _cap(
        "OBSIDIA_NATIVE_SELF_BUILD_PHASE1",
        family="SELF_BUILD",
        owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_BOUNDED,
        authority_class=AUTHORITY_NONE,
        rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={
            "repo_root": "explicit repository root",
            "target": "exact tracked tooling target",
            "requested_outcome": (
                "bounded native solve objective "
                "with NATIVE_SOLVE_JSON"
            ),
        },
        availability="AVAILABLE",
        proof_status=(
            "BRODY_OBSIDURE_PHASE1_PLAN_PROPOSED_NO_REPO_MUTATION"
        ),
        notes=(
            "Native Brody -> Obsidure -> candidate.patch -> "
            "Obsidia Build Phase1 only. "
            "Artifacts are external to the repository. "
            "No Phase2/apply/commit/push/merge. "
            "Human approval token is not exposed through Relay."
        ),
    ),
    "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW": _cap(
        "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW",
        family="EXTERNAL_RUNTIME_AGENT_SHADOW",
        owner=OWNER_OPENJARVIS_RUNTIME,
        mode=MODE_DETERMINISTIC_BOUNDED,
        authority_class=AUTHORITY_NONE,
        rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={
            "repo_root": "clean Obsidia engineering repository",
            "target": "one explicit self-build target",
            "requested_outcome": "bounded native solve objective",
        },
        availability="SHADOW_ORCHESTRATOR_SINGLE_OBSIDIA_TOOL",
        proof_status=(
            "REAL_OPENJARVIS_ORCHESTRATOR_SINGLE_TOOL_NO_REAL_MODEL"
        ),
        notes=(
            "Runs real OpenJarvis OrchestratorAgent with one tool only: "
            "obsidia_self_build_phase1. "
            "The tool calls the canonical Obsidia Relay, which routes to "
            "Brody -> Obsidure -> candidate.patch -> PLAN_PROPOSED. "
            "No real model, shell, file_write, git_commit, scheduler, "
            "OpenJarvis memory or direct repository mutation."
        ),
    ),
    "TEST_FAMILY_RUN": _cap(
        "TEST_FAMILY_RUN", family="TEST", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_BOUNDED, authority_class=AUTHORITY_NONE, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"test_family_id": "one of TEST_FAMILY_REGISTRY keys"},
        availability="AVAILABLE", proof_status="CLOSED_STACK_NATIVE_BOUNDED",
        notes="Named registered families only; model supplies a family_id, never a raw path."),
    "LEAN_BUILD": _cap(
        "LEAN_BUILD", family="FORMAL", owner=OWNER_FORMAL,
        mode=MODE_DETERMINISTIC_BOUNDED, authority_class=AUTHORITY_NONE, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"lean_target_id": "one of LEAN_TARGET_REGISTRY keys"},
        availability="AVAILABLE", proof_status="CLOSED_STACK_NATIVE_BOUNDED",
        notes="Named registered Lean targets only; no arbitrary module string."),
    "ENGINEERING_REASONING": _cap(
        "ENGINEERING_REASONING", family="COGNITION", owner=OWNER_COGNITIVE_RESOURCE,
        mode=MODE_COGNITIVE, authority_class=AUTHORITY_NONE, rw=RW_NONE,
        route=ROUTE_COGNITIVE_REQUEST,
        input_shape={"requested_capability": "str", "reason": "str"},
        availability="AVAILABLE",
        proof_status="RESULT_IS_EVIDENCE_OR_PROPOSAL_NEVER_AUTHORITY",
        notes="Brody / Claude / Obsidure candidates. CapabilityResult never applies itself."),
    "GOVERNED_UPDATE_TARGET_FROM_SOURCE": _cap(
        "GOVERNED_UPDATE_TARGET_FROM_SOURCE", family="GOVERNED_APPLY",
        owner=OWNER_STAGE4_RAIL, mode=MODE_GOVERNED_RAIL,
        authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"execution_envelope": "TERMINAL_COMMAND_ENVELOPE_V1",
                     "child_execution": "dict", "test_contract": "dict",
                     "source": "GIT_BLOB"},
        availability="PARTIAL_STAGE4_RAIL_RELAY_ORCHESTRATED_HOLD_FOR_HUMAN_EAH",
        proof_status="OPEN_GENERIC_AUTONOMOUS_APPLY",
        notes=("obsidia_governed_execution_driver_v0.prepare_governed_execution -> "
               "HOLD_FOR_HUMAN_EAH -> execute_governed_remediation. The relay ORCHESTRATES "
               "the HOLD; it does NOT construct the ExecutionEnvelope/TestContract nor mint "
               "the EAH/HMA. Operation is UPDATE_TARGET_FROM_SOURCE ONLY — no CREATE/DELETE/"
               "MOVE/RENAME (Stage 5). KX108_PRE/POST stay sovereign.")),
    "HUMAN_AUTHORITY": _cap(
        "HUMAN_AUTHORITY", family="HUMAN", owner=OWNER_HUMAN,
        mode=MODE_HUMAN_HOLD, authority_class=AUTHORITY_HUMAN, rw=RW_NONE,
        route=ROUTE_HOLD, input_shape={"human_decision_ref": "str", "resolution": "str"},
        availability="AVAILABLE", proof_status="HOLD_RESUME_ACTIVE",
        notes="Stack HOLDs, relay transports, human answers, same mission resumes. "
              "The stack never synthesizes human authorization."),
    "UNKNOWN_AUTHORITY": _cap(
        "UNKNOWN_AUTHORITY", family="UNKNOWN", owner=OWNER_HUMAN,
        mode=MODE_HUMAN_HOLD, authority_class=AUTHORITY_HUMAN, rw=RW_NONE,
        route=ROUTE_HOLD, input_shape={}, availability="AVAILABLE",
        proof_status="ROUTED_TO_HOLD_NEVER_A_MODEL",
        notes="Evidence may narrow an unknown FACT (never via a model); unknown AUTHORITY "
              "always routes to HUMAN/HOLD. Evidence cannot expand authorized scope."),
    "CONVERSATION": _cap(
        "CONVERSATION", family="CONVERSATION", owner=OWNER_COGNITIVE_RESOURCE,
        mode=MODE_COGNITIVE, authority_class=AUTHORITY_NONE, rw=RW_NONE,
        route=ROUTE_COGNITIVE_REQUEST, input_shape={"text": "str"},
        availability="AVAILABLE", proof_status="NON_MUTATING",
        notes="Pure conversation/reasoning. No repository effect."),
    # ── PC Capabilities V0 (OpenJarvis-bound, read-only) ─────────────────
    "PC_READ_FILE": _cap(
        "PC_READ_FILE", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"path": "workspace-relative path"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.read_file — workspace-bound, secret-filtered."),
    "PC_LIST_DIR": _cap(
        "PC_LIST_DIR", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"path": "workspace-relative directory"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.list_dir — max 200 entries, skip dirs filtered."),
    "PC_SEARCH_PROJECT": _cap(
        "PC_SEARCH_PROJECT", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"pattern": "regex", "file_glob": "glob"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.search_project — ripgrep-style, workspace-bound."),
    "PC_GIT_STATUS": _cap(
        "PC_GIT_STATUS", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.git_status — wraps native read_git_state."),
    "PC_GIT_DIFF": _cap(
        "PC_GIT_DIFF", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"file_path": "optional", "staged": "bool"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.git_diff — workspace-bound, max 65536 bytes."),
    "PC_RUN_TEST_READONLY": _cap(
        "PC_RUN_TEST_READONLY", family="PC_TEST", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_BOUNDED, authority_class=AUTHORITY_NONE, rw=RW_NONE,
        route=ROUTE_NATIVE, input_shape={"test_family_id": "PC_TEST_FAMILY_REGISTRY key"},
        availability="AVAILABLE", proof_status="CLOSED_STACK_NATIVE_BOUNDED",
        notes="obsidia_pc_capabilities_v0.run_test_readonly — named families only, no raw paths."),
    "PC_PROCESS_STATUS": _cap(
        "PC_PROCESS_STATUS", family="PC_READ_ONLY", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_DETERMINISTIC_READ_ONLY, authority_class=AUTHORITY_NONE, rw=RW_READ,
        route=ROUTE_NATIVE, input_shape={"name_filter": "optional str"},
        availability="AVAILABLE", proof_status="CLOSED_READ_ONLY",
        notes="obsidia_pc_capabilities_v0.process_status — psutil or os fallback, max 50."),
    "PC_GOVERNED_PREPARE": _cap(
        "PC_GOVERNED_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"source_git_commit": "str", "target_path": "workspace-relative",
                     "execution_worktree_path": "operator-trusted path"},
        availability="AVAILABLE", proof_status="J5_PROVEN_PREPARE_ONLY",
        notes="pc_governed_prepare: PREPARE only, no mutation, reveals EAH. KX108_ONLY."),
    "PC_GOVERNED_EXECUTE": _cap(
        "PC_GOVERNED_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_GOVERNED_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_PROVEN_E2E_REAL_MUTATION",
        notes="pc_governed_execute: explicit human EAH required. J5->KX108_PRE->governed apply. KX108_ONLY."),
    # -- V2 capabilities (CREATE_FILE, MOVE_FILE, APPLY_PATCH, CREATE_DIR, WINDOW_FOCUS) --
    "PC_V2_CREATE_FILE_PREPARE": _cap(
        "PC_V2_CREATE_FILE_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"target_path": "workspace-relative", "content": "bytes",
                     "execution_worktree_path": "operator-trusted path"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 CREATE_FILE PREPARE: target must be absent. KX108_ONLY."),
    "PC_V2_CREATE_FILE_EXECUTE": _cap(
        "PC_V2_CREATE_FILE_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_CREATE_FILE_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 CREATE_FILE EXECUTE: EAH+human approval+KX108 required. KX108_ONLY."),
    "PC_V2_MOVE_FILE_PREPARE": _cap(
        "PC_V2_MOVE_FILE_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"source_path": "workspace-relative", "dest_path": "workspace-relative",
                     "execution_worktree_path": "operator-trusted path"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 MOVE_FILE PREPARE: source must exist, dest must be absent. KX108_ONLY."),
    "PC_V2_MOVE_FILE_EXECUTE": _cap(
        "PC_V2_MOVE_FILE_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_MOVE_FILE_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 MOVE_FILE EXECUTE: EAH+human approval+KX108 required. KX108_ONLY."),
    "PC_V2_APPLY_PATCH_PREPARE": _cap(
        "PC_V2_APPLY_PATCH_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"patch_content": "unified diff str",
                     "execution_worktree_path": "operator-trusted path"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 APPLY_PATCH PREPARE: unified diff, no binary, multi-file bounded. KX108_ONLY."),
    "PC_V2_APPLY_PATCH_EXECUTE": _cap(
        "PC_V2_APPLY_PATCH_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_APPLY_PATCH_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 APPLY_PATCH EXECUTE: EAH+human approval+KX108+git apply. KX108_ONLY."),
    "PC_V2_CREATE_DIR_PREPARE": _cap(
        "PC_V2_CREATE_DIR_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"dir_path": "workspace-relative",
                     "execution_worktree_path": "operator-trusted path"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 CREATE_DIR PREPARE: parent must exist, target must be absent. KX108_ONLY."),
    "PC_V2_CREATE_DIR_EXECUTE": _cap(
        "PC_V2_CREATE_DIR_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_CREATE_DIR_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 CREATE_DIR EXECUTE: EAH+human approval+KX108 required. KX108_ONLY."),
    "PC_V2_WINDOW_FOCUS_PREPARE": _cap(
        "PC_V2_WINDOW_FOCUS_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"title": "str — window title search string"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 WINDOW_FOCUS PREPARE: resolves hwnd+title, no mutation. KX108_ONLY."),
    "PC_V2_WINDOW_FOCUS_EXECUTE": _cap(
        "PC_V2_WINDOW_FOCUS_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_WINDOW_FOCUS_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 WINDOW_FOCUS EXECUTE: EAH+human approval+KX108+exact hwnd. KX108_ONLY."),
    "PC_V2_APP_OPEN_PREPARE": _cap(
        "PC_V2_APP_OPEN_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"app": "str - application name or alias"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 APP_OPEN PREPARE: resolve inventory+pre-state anchor, no process launch. KX108_ONLY."),
    "PC_V2_APP_OPEN_EXECUTE": _cap(
        "PC_V2_APP_OPEN_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_APP_OPEN_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 APP_OPEN EXECUTE: EAH+human approval+KX108+inventory drift check+PID verify. KX108_ONLY."),
    "PC_V2_UIA_SET_TEXT_PREPARE": _cap(
        "PC_V2_UIA_SET_TEXT_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"window_hwnd": "int", "target_identity": "JarJar G2-0 stable UIA identity "
                     "(window_hwnd, process_id, runtime_id + drift guards)", "target_value": "str"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 UIA SET_TEXT PREPARE: exact stable UIA identity, password/readonly rejected, "
              "pre_value_sha256 in PSA V1 (no target value), EAH binds identity + target hash. KX108_ONLY."),
    "PC_V2_UIA_SET_TEXT_EXECUTE": _cap(
        "PC_V2_UIA_SET_TEXT_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_UIA_SET_TEXT_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 UIA SET_TEXT EXECUTE: reacquire exact identity, PSA drift check, set_text_by_identity, "
              "same-identity readback hash == target hash -> STRONG; hashes only in receipts. KX108_ONLY."),
    "PC_V2_UIA_SET_CHECKED_PREPARE": _cap(
        "PC_V2_UIA_SET_CHECKED_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"window_title": "str", "control_name": "str", "target_checked": "bool"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 UIA SET_CHECKED PREPARE: resolve exact CheckBox, read pre toggle state, build PSA. KX108_ONLY."),
    "PC_V2_UIA_SET_CHECKED_EXECUTE": _cap(
        "PC_V2_UIA_SET_CHECKED_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_UIA_SET_CHECKED_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 UIA SET_CHECKED EXECUTE: PSA drift check, TogglePattern target-state, post-read verified -> STRONG. KX108_ONLY."),
    "PC_V2_UIA_SELECT_RADIO_PREPARE": _cap(
        "PC_V2_UIA_SELECT_RADIO_PREPARE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_NONE,
        route=ROUTE_NATIVE,
        input_shape={"window_hwnd": "int", "target_identity": "dict"},
        availability="AVAILABLE", proof_status="J5_PREPARE_ONLY",
        notes="V2 UIA SELECT_RADIO PREPARE: resolve RadioButton by exact identity, read pre is_selected, build PSA. KX108_ONLY."),
    "PC_V2_UIA_SELECT_RADIO_EXECUTE": _cap(
        "PC_V2_UIA_SELECT_RADIO_EXECUTE", family="PC_GOVERNED_WRITE", owner=OWNER_OBSIDIA_STACK,
        mode=MODE_GOVERNED_RAIL, authority_class=AUTHORITY_KX108_ONLY, rw=RW_WRITE_GOVERNED,
        route=ROUTE_STAGE4_GOVERNED,
        input_shape={"prepared_result": "PC_V2_UIA_SELECT_RADIO_PREPARE output",
                     "human_authorized_eah": "exact EAH from PREPARE"},
        availability="AVAILABLE", proof_status="J5_E2E_GOVERNED",
        notes="V2 UIA SELECT_RADIO EXECUTE: PSA drift check, SelectionItemPattern select, post-read verified -> STRONG. KX108_ONLY."),
}

_CAPABILITY_IDS = tuple(_GRAPH.keys())


def capability_ids() -> tuple:
    return _CAPABILITY_IDS


def get_capability(capability_id: str) -> Optional[dict]:
    c = _GRAPH.get(capability_id)
    return dict(c) if c else None


def graph_snapshot() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "capabilities": {k: dict(v) for k, v in _GRAPH.items()},
    }


# ── Résolution : besoin de mission -> capacité -> route (PUR) ──────────
_KIND_TO_CAPABILITY = {
    "GIT_STATE_READ": "GIT_STATE_READ",
    "OPENJARVIS_RUNTIME_HANDSHAKE": "OPENJARVIS_RUNTIME_HANDSHAKE",
    "OPENJARVIS_SIMPLE_AGENT_SHADOW": "OPENJARVIS_SIMPLE_AGENT_SHADOW",
    "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW": "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW",
    "OBSIDIA_NATIVE_SELF_BUILD_PHASE1": "OBSIDIA_NATIVE_SELF_BUILD_PHASE1",
    "TEST_FAMILY_RUN": "TEST_FAMILY_RUN",
    "LEAN_BUILD": "LEAN_BUILD",
    "ENGINEERING_REASONING": "ENGINEERING_REASONING",
    "GOVERNED_UPDATE_TARGET_FROM_SOURCE": "GOVERNED_UPDATE_TARGET_FROM_SOURCE",
    "HUMAN_DECISION": "HUMAN_AUTHORITY",
    "UNKNOWN": "UNKNOWN_AUTHORITY",
    "CONVERSATION": "CONVERSATION",
    "PC_READ_FILE": "PC_READ_FILE",
    "PC_LIST_DIR": "PC_LIST_DIR",
    "PC_SEARCH_PROJECT": "PC_SEARCH_PROJECT",
    "PC_GIT_STATUS": "PC_GIT_STATUS",
    "PC_GIT_DIFF": "PC_GIT_DIFF",
    "PC_RUN_TEST_READONLY": "PC_RUN_TEST_READONLY",
    "PC_PROCESS_STATUS": "PC_PROCESS_STATUS",
    "PC_GOVERNED_PREPARE": "PC_GOVERNED_PREPARE",
    "PC_GOVERNED_EXECUTE": "PC_GOVERNED_EXECUTE",
    "PC_V2_CREATE_FILE_PREPARE": "PC_V2_CREATE_FILE_PREPARE",
    "PC_V2_CREATE_FILE_EXECUTE": "PC_V2_CREATE_FILE_EXECUTE",
    "PC_V2_MOVE_FILE_PREPARE": "PC_V2_MOVE_FILE_PREPARE",
    "PC_V2_MOVE_FILE_EXECUTE": "PC_V2_MOVE_FILE_EXECUTE",
    "PC_V2_APPLY_PATCH_PREPARE": "PC_V2_APPLY_PATCH_PREPARE",
    "PC_V2_APPLY_PATCH_EXECUTE": "PC_V2_APPLY_PATCH_EXECUTE",
    "PC_V2_CREATE_DIR_PREPARE": "PC_V2_CREATE_DIR_PREPARE",
    "PC_V2_CREATE_DIR_EXECUTE": "PC_V2_CREATE_DIR_EXECUTE",
    "PC_V2_WINDOW_FOCUS_PREPARE": "PC_V2_WINDOW_FOCUS_PREPARE",
    "PC_V2_WINDOW_FOCUS_EXECUTE": "PC_V2_WINDOW_FOCUS_EXECUTE",
}


def resolve_capability_for_kind(mission_kind: str) -> dict:
    """Renvoie {capability_id, route, owner, authority_class, mode, availability}
    ou un descripteur STACK_NATIVE_CAPABILITY_GAP. Ne route JAMAIS un UNKNOWN
    vers un modèle ; ne fabrique aucune autorité."""
    cap_id = _KIND_TO_CAPABILITY.get(mission_kind)
    if cap_id is None:
        return {"capability_id": None, "route": ROUTE_HOLD,
                "gap": "STACK_NATIVE_CAPABILITY_GAP",
                "reason": f"NO_CAPABILITY_FOR_KIND:{mission_kind}",
                "authority_class": AUTHORITY_HUMAN}
    c = _GRAPH[cap_id]
    return {"capability_id": cap_id, "route": c["route"], "owner": c["owner"],
            "authority_class": c["authority_class"], "mode": c["mode"],
            "availability": c["availability"], "family": c["family"],
            "grants_authority": False}


def _main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="obsidia_capability_graph_v0")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--dump", action="store_true")
    a = ap.parse_args(argv)
    if a.dump:
        print(json.dumps(graph_snapshot(), indent=2)); return 0
    if a.self_check:
        print(json.dumps({
            "CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY": CAPABILITY_GRAPH_IS_EXECUTION_AUTHORITY,
            "CAPABILITY_GRAPH_IS_KX_AUTHORITY": CAPABILITY_GRAPH_IS_KX_AUTHORITY,
            "KX_DECISION_AUTHORITY": KX_DECISION_AUTHORITY,
            "capability_ids": list(_CAPABILITY_IDS),
            "owners": sorted({c["owner"] for c in _GRAPH.values()}),
            "routes": sorted({c["route"] for c in _GRAPH.values()}),
        }, indent=2))
        return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
