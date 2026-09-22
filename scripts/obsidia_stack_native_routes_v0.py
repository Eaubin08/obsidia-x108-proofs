#!/usr/bin/env python3
"""OBSIDIA — Stack-native bounded capability routes V0 (Relay-First).

Deterministic, READ-ONLY-or-BOUNDED capabilities the Obsidia stack owns and can
resolve WITHOUT any probabilistic model. Every route:
  - takes ONLY an authorized/allowlisted target (never arbitrary shell / args),
  - produces EVIDENCE (never authority),
  - performs NO repository mutation, NO git mutation, NO KX decision.

  read_git_state()          -> GAP-CG-3 : READ-ONLY git disposition facts.
  run_test_family(target)   -> GAP-CG-1 : bounded pytest on an exact allowlisted target.
  run_lean_target(module)   -> GAP-CG-2 : bounded `lake build` on an allowlisted module.

Invariants (all asserted, static):
  ROUTE_IS_EXECUTION_AUTHORITY = FALSE
  ROUTE_IS_KX_AUTHORITY        = FALSE
  ROUTE_MUTATES_REPO           = FALSE
  ROUTE_ACCEPTS_ARBITRARY_SHELL = FALSE
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS.parent

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

ROUTE_IS_EXECUTION_AUTHORITY = False
ROUTE_IS_KX_AUTHORITY = False
ROUTE_MUTATES_REPO = False
ROUTE_ACCEPTS_ARBITRARY_SHELL = False

# ── Registres NOMMÉS — familles enregistrées, jamais une cible libre ──
#  Le modèle fournit un family_id / target_id ; JAMAIS un chemin/module brut.
TEST_FAMILY_REGISTRY = {
    "GOVERNANCE_CG_SUITE": (
        "tests/cli/test_gateway_route_decision_cgb_v0.py",
        "tests/cli/test_cognitive_capability_lease_cgc_v0.py",
        "tests/cli/test_mission_capability_scope_cgc2_v0.py",
        "tests/cli/test_pretool_shadow_cgd_v0.py",
    ),
    "RELAY_FIRST_SUITE": (
        "tests/cli/test_relay_first_v0.py",
        "tests/cli/test_capability_graph_v0.py",
    ),
    "STAGE4_AUTHORITY_GUARD": (
        "tests/cli/test_mission_authority_v0.py",
    ),
}
LEAN_TARGET_REGISTRY = {
    "MISSION_AUTHORITY": "Obsidia.MissionAuthority",
    "OBSIDIA_AGGREGATE": "Obsidia",
}

# Rétro-compat : liste plate dérivée des registres (aucune cible hors registre).
_AUTHORIZED_TEST_TARGETS = tuple(sorted({t for fam in TEST_FAMILY_REGISTRY.values() for t in fam}))
_AUTHORIZED_LEAN_TARGETS = tuple(sorted(set(LEAN_TARGET_REGISTRY.values())))

# READ-ONLY git subcommands only (mirror of settings.json allow-list intent).
_GIT_READ_ONLY = {
    "head": ["rev-parse", "HEAD"],
    "branch": ["branch", "--show-current"],
    "porcelain": ["status", "--porcelain"],
    "head_subject": ["log", "-1", "--format=%s"],
    "name_status": ["diff", "--name-status", "HEAD"],
    "staged_names": ["diff", "--cached", "--name-only"],
}


def _git(repo: Path, args: "list[str]", timeout: float = 20.0) -> "tuple[int, str]":
    try:
        r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                           text=True, timeout=timeout)  # list-form, no shell
        return r.returncode, (r.stdout or "")
    except Exception as exc:
        return 255, f"__GIT_ERROR__:{type(exc).__name__}"


def _evidence(kind: str, ok: bool, **fields) -> dict:
    core = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": "OBSIDIA_STACK_NATIVE_ROUTE_EVIDENCE_V0",
        "native_route_kind": kind,
        "ok": bool(ok),
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_human_authority": False,
        "is_sovereign": False,
        "mutated_repo": False,
        "decision_authority": DECISION_AUTHORITY,
        **fields,
    }
    return core


# ══════════════════════════════════════════════════════════════════════════
#  GAP-CG-3 — read_git_state (READ-ONLY)
# ══════════════════════════════════════════════════════════════════════════

def read_git_state(*, repo_root=None) -> dict:
    repo = Path(repo_root) if repo_root else _REPO_ROOT
    rc_h, head = _git(repo, _GIT_READ_ONLY["head"])
    if rc_h != 0:
        return _evidence("GIT_STATE_READ", False, reason="NOT_A_GIT_REPO_OR_GIT_UNAVAILABLE")
    _, branch = _git(repo, _GIT_READ_ONLY["branch"])
    _, porcelain = _git(repo, _GIT_READ_ONLY["porcelain"])
    _, subject = _git(repo, _GIT_READ_ONLY["head_subject"])
    _, name_status = _git(repo, _GIT_READ_ONLY["name_status"])
    _, staged = _git(repo, _GIT_READ_ONLY["staged_names"])

    changed, untracked = [], []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        code, _, path = line[:2], line[2:3], line[3:].strip()
        (untracked if code == "??" else changed).append(path)
    return _evidence(
        "GIT_STATE_READ", True,
        head=head.strip(),
        head_subject=subject.strip()[:200],
        branch=branch.strip(),
        working_tree_clean=(porcelain.strip() == ""),
        changed_paths=sorted(set(changed))[:200],
        untracked_paths=sorted(set(untracked))[:200],
        staged_paths=sorted(set(p for p in staged.splitlines() if p.strip()))[:200],
        diff_name_status_head=name_status.strip().splitlines()[:200],
    )


# ══════════════════════════════════════════════════════════════════════════
#  GAP-CG-1 — run_test_family (bounded, allowlisted)
# ══════════════════════════════════════════════════════════════════════════

def authorized_test_targets() -> tuple:
    return _AUTHORIZED_TEST_TARGETS


def test_family_ids() -> tuple:
    return tuple(TEST_FAMILY_REGISTRY.keys())


def _pytest_targets(targets: "list[str]", *, repo_root=None, timeout: float,
                    label: str) -> dict:
    repo = Path(repo_root) if repo_root else _REPO_ROOT
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", *targets, "-q",
                            "-p", "no:cacheprovider"],
                           cwd=str(repo), capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return _evidence("TEST_FAMILY_RUN", False, label=label,
                         reason=f"PYTEST_ERROR:{type(exc).__name__}")
    tail = "\n".join((r.stdout or "").strip().splitlines()[-6:])
    return _evidence("TEST_FAMILY_RUN", r.returncode == 0, label=label,
                     targets=list(targets), exit_code=r.returncode, result_tail=tail)


def run_test_family(target: str, *, repo_root=None, timeout: float = 600.0) -> dict:
    """Rétro-compat : une cible EXACTE (issue d'un registre)."""
    if target not in _AUTHORIZED_TEST_TARGETS:
        return _evidence("TEST_FAMILY_RUN", False,
                         reason=f"TARGET_NOT_AUTHORIZED:{target}",
                         authorized=list(_AUTHORIZED_TEST_TARGETS))
    ev = _pytest_targets([target], repo_root=repo_root, timeout=timeout, label=target)
    ev["target"] = target
    return ev


def run_test_family_by_id(test_family_id: str, *, repo_root=None,
                          timeout: float = 900.0) -> dict:
    """GAP-CG-1 : famille NOMMÉE enregistrée uniquement."""
    fam = TEST_FAMILY_REGISTRY.get(test_family_id)
    if fam is None:
        return _evidence("TEST_FAMILY_RUN", False,
                         reason=f"TEST_FAMILY_ID_NOT_REGISTERED:{test_family_id}",
                         registered=list(TEST_FAMILY_REGISTRY))
    ev = _pytest_targets(list(fam), repo_root=repo_root, timeout=timeout,
                         label=test_family_id)
    ev["test_family_id"] = test_family_id
    return ev


# ══════════════════════════════════════════════════════════════════════════
#  GAP-CG-2 — run_lean_target (bounded, allowlisted)
# ══════════════════════════════════════════════════════════════════════════

def authorized_lean_targets() -> tuple:
    return _AUTHORIZED_LEAN_TARGETS


def lean_target_ids() -> tuple:
    return tuple(LEAN_TARGET_REGISTRY.keys())


def run_lean_by_id(lean_target_id: str, *, lean_root=None, timeout: float = 900.0) -> dict:
    """GAP-CG-2 : cible Lean NOMMÉE enregistrée uniquement."""
    module = LEAN_TARGET_REGISTRY.get(lean_target_id)
    if module is None:
        return _evidence("LEAN_BUILD", False,
                         reason=f"LEAN_TARGET_ID_NOT_REGISTERED:{lean_target_id}",
                         registered=list(LEAN_TARGET_REGISTRY))
    ev = run_lean_target(module, lean_root=lean_root, timeout=timeout)
    ev["lean_target_id"] = lean_target_id
    return ev


def run_lean_target(module: str, *, lean_root=None, timeout: float = 900.0) -> dict:
    if module not in _AUTHORIZED_LEAN_TARGETS:
        return _evidence("LEAN_BUILD", False,
                         reason=f"MODULE_NOT_AUTHORIZED:{module}",
                         authorized=list(_AUTHORIZED_LEAN_TARGETS))
    root = Path(lean_root) if lean_root else (_REPO_ROOT / "proofs" / "lean")
    if not root.is_dir():
        return _evidence("LEAN_BUILD", False, module=module, reason="LEAN_ROOT_ABSENT")
    try:
        r = subprocess.run(["lake", "build", module], cwd=str(root),
                           capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return _evidence("LEAN_BUILD", False, module=module,
                         reason=f"LAKE_ERROR:{type(exc).__name__}")
    tail = "\n".join((r.stdout or "").strip().splitlines()[-4:])
    return _evidence("LEAN_BUILD", r.returncode == 0, module=module,
                     exit_code=r.returncode, result_tail=tail)


# ── Table de dispatch bornée (aucune exécution depuis une chaîne libre) ──

# ======================================================================
# JARVIS V0.3 ? PINNED OPENJARVIS SHADOW RUNTIME
# ======================================================================

def run_openjarvis_runtime_handshake(
    expected_commit: str,
    *,
    source_root=None,
) -> dict:
    """Bounded READ_ONLY identity/runtime handshake.

    The caller cannot select an arbitrary Python checkout.
    Both source_root and expected_commit must exactly match the
    operator-provided OBSIDIA_OPENJARVIS_* configuration.

    No agent, tool, scheduler, memory or authority is activated.
    """

    import obsidia_openjarvis_adapter_v0 as _OJ

    requested_commit = str(
        expected_commit or ""
    ).strip().lower()

    configured_source = os.environ.get(
        "OBSIDIA_OPENJARVIS_SOURCE",
        "",
    ).strip()

    configured_commit = os.environ.get(
        "OBSIDIA_OPENJARVIS_COMMIT",
        "",
    ).strip().lower()

    if not configured_source or not configured_commit:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_RUNTIME_NOT_CONFIGURED",
        )

    if (
        len(configured_commit) != 40
        or any(
            c not in "0123456789abcdef"
            for c in configured_commit
        )
    ):
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_CONFIGURED_COMMIT_INVALID",
        )

    if requested_commit != configured_commit:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_COMMIT_NOT_AUTHORIZED",
            requested_commit=requested_commit,
            configured_commit=configured_commit,
        )

    if not source_root:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_SOURCE_REQUIRED",
        )

    requested_source = Path(
        source_root
    ).resolve(strict=False)

    authorized_source = Path(
        configured_source
    ).resolve(strict=False)

    if requested_source != authorized_source:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_SOURCE_NOT_AUTHORIZED",
            requested_source=str(requested_source),
            authorized_source=str(authorized_source),
        )

    pre_rc, pre_head = _git(
        authorized_source,
        ["rev-parse", "HEAD"],
    )

    pre_status_rc, pre_status = _git(
        authorized_source,
        ["status", "--porcelain"],
    )

    if pre_rc != 0 or pre_status_rc != 0:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_SOURCE_GIT_STATE_UNAVAILABLE",
        )

    adapter = _OJ.OpenJarvisShadowAdapter(
        source_root=str(authorized_source),
        expected_commit=configured_commit,
    )

    result = adapter.execute(
        capability_id="OPENJARVIS_RUNTIME_HANDSHAKE",
        payload={},
    )

    post_rc, post_head = _git(
        authorized_source,
        ["rev-parse", "HEAD"],
    )

    post_status_rc, post_status = _git(
        authorized_source,
        ["status", "--porcelain"],
    )

    if post_rc != 0 or post_status_rc != 0:
        return _evidence(
            "OPENJARVIS_RUNTIME_HANDSHAKE",
            False,
            reason="OPENJARVIS_POST_STATE_UNAVAILABLE",
        )

    mutated_measured = (
        pre_head.strip() != post_head.strip()
        or pre_status != post_status
    )

    adapter_ok = (
        result.get("status")
        == "OPENJARVIS_SHADOW_HANDSHAKE_OK"
    )

    ok = adapter_ok and not mutated_measured

    return _evidence(
        "OPENJARVIS_RUNTIME_HANDSHAKE",
        ok,

        reason=(
            None
            if ok
            else (
                "OPENJARVIS_EXTERNAL_STATE_MUTATED"
                if mutated_measured
                else result.get("status")
            )
        ),

        adapter_id=result.get("adapter_id"),
        openjarvis_status=result.get("status"),

        expected_commit=configured_commit,
        actual_commit=result.get("actual_commit"),

        source_root=str(authorized_source),
        source_dirty=result.get("source_dirty"),

        missing_required_surfaces=list(
            result.get("missing_required_surfaces") or []
        ),

        agent_execution_enabled=bool(
            result.get("agent_execution_enabled")
        ),

        tool_execution_enabled=bool(
            result.get("tool_execution_enabled")
        ),

        scheduler_enabled=bool(
            result.get("scheduler_enabled")
        ),

        memory_enabled=bool(
            result.get("memory_enabled")
        ),

        memory_written=bool(
            result.get("memory_written")
        ),

        scope_expanded=bool(
            result.get("scope_expanded")
        ),

        mutated_repo=mutated_measured,

        external_runtime_authority="NONE",
    )



# ======================================================================
# JARVIS V0.4 ? real OpenJarvis SimpleAgent, deterministic SHADOW engine
# ======================================================================

def run_openjarvis_simple_agent_shadow(
    input_text: str,
    *,
    source_root=None,
) -> dict:
    """Run the real OpenJarvis SimpleAgent without a real model or tools."""

    import obsidia_openjarvis_adapter_v0 as _OJ

    configured_source = os.environ.get(
        "OBSIDIA_OPENJARVIS_SOURCE",
        "",
    ).strip()

    configured_commit = os.environ.get(
        "OBSIDIA_OPENJARVIS_COMMIT",
        "",
    ).strip().lower()

    if not configured_source or not configured_commit:
        return _evidence(
            "OPENJARVIS_SIMPLE_AGENT_SHADOW",
            False,
            reason="OPENJARVIS_RUNTIME_NOT_CONFIGURED",
        )

    if not source_root:
        return _evidence(
            "OPENJARVIS_SIMPLE_AGENT_SHADOW",
            False,
            reason="OPENJARVIS_SOURCE_REQUIRED",
        )

    requested_source = Path(
        source_root
    ).resolve(strict=False)

    authorized_source = Path(
        configured_source
    ).resolve(strict=False)

    if requested_source != authorized_source:
        return _evidence(
            "OPENJARVIS_SIMPLE_AGENT_SHADOW",
            False,
            reason="OPENJARVIS_SOURCE_NOT_AUTHORIZED",
        )

    pre_rc, pre_head = _git(
        authorized_source,
        ["rev-parse", "HEAD"],
    )

    pre_status_rc, pre_status = _git(
        authorized_source,
        ["status", "--porcelain"],
    )

    if pre_rc != 0 or pre_status_rc != 0:
        return _evidence(
            "OPENJARVIS_SIMPLE_AGENT_SHADOW",
            False,
            reason="OPENJARVIS_SOURCE_GIT_STATE_UNAVAILABLE",
        )

    adapter = _OJ.OpenJarvisSimpleAgentShadowAdapter(
        source_root=str(authorized_source),
        expected_commit=configured_commit,
    )

    result = adapter.execute(
        capability_id="OPENJARVIS_SIMPLE_AGENT_SHADOW",
        payload={
            "input_text": input_text,
        },
    )

    post_rc, post_head = _git(
        authorized_source,
        ["rev-parse", "HEAD"],
    )

    post_status_rc, post_status = _git(
        authorized_source,
        ["status", "--porcelain"],
    )

    if post_rc != 0 or post_status_rc != 0:
        return _evidence(
            "OPENJARVIS_SIMPLE_AGENT_SHADOW",
            False,
            reason="OPENJARVIS_POST_STATE_UNAVAILABLE",
        )

    mutated_measured = (
        pre_head.strip() != post_head.strip()
        or pre_status != post_status
    )

    ok = (
        result.get("status")
        == "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK"
        and not mutated_measured
    )

    return _evidence(
        "OPENJARVIS_SIMPLE_AGENT_SHADOW",
        ok,

        reason=(
            None
            if ok
            else (
                "OPENJARVIS_EXTERNAL_STATE_MUTATED"
                if mutated_measured
                else result.get("status")
            )
        ),

        adapter_id=result.get("adapter_id"),

        openjarvis_status=result.get("status"),

        expected_commit=configured_commit,
        actual_commit=result.get("actual_commit"),

        agent_class=result.get("agent_class"),
        agent_id=result.get("agent_id"),

        engine=result.get("engine"),
        engine_calls=result.get("engine_calls"),

        turns=result.get("turns"),
        tool_results=result.get("tool_results"),

        content=result.get("content"),
        input_sha256=result.get("input_sha256"),

        real_openjarvis_agent_code=bool(
            result.get("real_openjarvis_agent_code")
        ),

        real_model_enabled=bool(
            result.get("real_model_enabled")
        ),

        agent_execution_enabled=bool(
            result.get("agent_execution_enabled")
        ),

        tool_execution_enabled=bool(
            result.get("tool_execution_enabled")
        ),

        memory_enabled=bool(
            result.get("memory_enabled")
        ),

        scheduler_enabled=bool(
            result.get("scheduler_enabled")
        ),

        network_enabled=bool(
            result.get("network_enabled")
        ),

        memory_written=bool(
            result.get("memory_written")
        ),

        scope_expanded=bool(
            result.get("scope_expanded")
        ),

        mutated_repo=mutated_measured,

        external_runtime_authority="NONE",
    )


NATIVE_CAPABILITIES = {
    "GIT_STATE_READ": ("read_git_state", read_git_state),
    "OPENJARVIS_RUNTIME_HANDSHAKE": (
        "run_openjarvis_runtime_handshake",
        run_openjarvis_runtime_handshake,
    ),
    "OPENJARVIS_SIMPLE_AGENT_SHADOW": (
        "run_openjarvis_simple_agent_shadow",
        run_openjarvis_simple_agent_shadow,
    ),
    "TEST_FAMILY_RUN": ("run_test_family_by_id", run_test_family_by_id),
    "LEAN_BUILD": ("run_lean_by_id", run_lean_by_id),
}


def _main(argv) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(prog="obsidia_stack_native_routes_v0")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)
    if a.self_check:
        print(json.dumps({
            "ROUTE_IS_EXECUTION_AUTHORITY": ROUTE_IS_EXECUTION_AUTHORITY,
            "ROUTE_IS_KX_AUTHORITY": ROUTE_IS_KX_AUTHORITY,
            "ROUTE_MUTATES_REPO": ROUTE_MUTATES_REPO,
            "ROUTE_ACCEPTS_ARBITRARY_SHELL": ROUTE_ACCEPTS_ARBITRARY_SHELL,
            "native_capabilities": list(NATIVE_CAPABILITIES),
            "test_family_ids": list(TEST_FAMILY_REGISTRY),
            "lean_target_ids": list(LEAN_TARGET_REGISTRY),
            "authorized_test_targets": list(_AUTHORIZED_TEST_TARGETS),
            "authorized_lean_targets": list(_AUTHORIZED_LEAN_TARGETS),
        }, indent=2))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
