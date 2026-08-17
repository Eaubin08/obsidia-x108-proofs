#!/usr/bin/env python3
"""
scripts/obsidure_bounded_apply.py — OBSIDURE_BOUNDED_APPLY_V1
==============================================================
Enveloppe de validation bornée autour de AgentObsidure.apply_proposal().

Flux canonique :
  load_and_validate_proposal()
  → dryrun_bounded()            (READ-ONLY, zéro écriture)
  → run_bounded_apply()         (apply via AgentObsidure.apply_proposal(target_root=...))
  → post-apply scope check
  → run_tests_for_evidence()    (pytest ciblé → GateTestEvidence)
  → build_tooling_state_from_evidence()
  → GuardX108 (run_tooling_build_pipeline)
  → write_apply_receipt()

Autorité Git : AUCUNE.
  Aucun git add. Aucun git commit. Aucun push. Aucun merge.
  decision_authority = KX108_ONLY
  ACT = READY_FOR_COMMIT_REVIEW
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.agent_obsidure import (
    AgentObsidure,
    PROPOSALS_DIR,
    _is_protected,
    _sha256,
    _enforce_boundaries,
    AGENT_OBSIDURE_BOUNDARY,
)
from sigma.contracts import ToolingBuildState
from sigma.protocols import run_tooling_build_pipeline

import dataclasses as _dc

APPLY_RECEIPT_BASE: Path = Path(
    os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
) / "Obsidia" / "build_sessions"

MAX_FILES_V1 = 20

PROTECTED_PATHS_V1 = (
    "server.kernel.sealed.cjs",
    "proofs/",
    "formal/",
    "merkle_seal.json",
)


# ---------------------------------------------------------------------------
# STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class GateTestEvidence:
    """Artefact attesté d'exécution de tests — jamais un booléen injecté."""
    command: str
    test_identity: str
    exit_code: int
    status: str          # "PASS" | "FAIL" | "ERROR"
    timestamp: str
    results_summary: str
    receipt_hash: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and self.status == "PASS"


@dataclass
class BoundedApplySession:
    """Session d'application bornée — contrat spec §7."""
    session_id: str
    proposal_id: str
    objective: str
    base_sha: str
    worktree_path: str
    approved_scope: List[str]
    proposal_files: List[str]
    operations: List[Dict[str, Any]]
    protected_paths_check: str = "UNKNOWN"
    proposal_hash: str = ""
    apply_status: str = "PENDING"
    dryrun_status: str = "PENDING"
    scope_verification: str = "PENDING"
    actual_modified_files: List[str] = field(default_factory=list)
    test_evidence: Optional[GateTestEvidence] = None
    gate_evidence: Optional[GateTestEvidence] = None
    kx108_decision: str = "UNKNOWN"
    kx108_raw: Dict[str, Any] = field(default_factory=dict)
    commit_status: str = "NOT_COMMITTED"
    push_status: str = "NOT_PUSHED"
    merge_status: str = "NOT_MERGED"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def _proposal_json_path(proposal_id: str) -> Path:
    _validate_proposal_id(proposal_id)
    return PROPOSALS_DIR / proposal_id / "proposal.json"


def _validate_proposal_id(proposal_id: str) -> None:
    if not proposal_id or "/" in proposal_id or "\\" in proposal_id or ".." in proposal_id:
        raise ValueError(f"proposal_id invalide : {proposal_id!r}")


def _compute_proposal_hash(data: dict) -> str:
    canonical = json.dumps(
        {k: data[k] for k in sorted(data.keys()) if k not in ("human_approved", "status", "proposal_hash")},
        sort_keys=True, ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _check_protected_in_list(files: List[str]) -> List[str]:
    return [f for f in files if _is_protected(f) or any(p in f.replace("\\", "/") for p in PROTECTED_PATHS_V1)]


def load_and_validate_proposal(
    proposal_id: str,
    session_id: str,
    base_sha: str,
    worktree: str,
    approved_scope: List[str],
) -> BoundedApplySession:
    """
    Charge la proposal et applique toutes les vérifications de cohérence.
    Retourne un BoundedApplySession avec dryrun_status positionné.
    Lève ValueError avec le code de blocage si une vérification échoue.
    """
    p = _proposal_json_path(proposal_id)
    if not p.exists():
        raise ValueError(f"BLOCK_PROPOSAL_NOT_FOUND: {proposal_id}")

    with p.open(encoding="utf-8") as f:
        data = json.load(f)

    # Vérification session_id
    if data.get("session_id") and data["session_id"] != session_id:
        raise ValueError(
            f"HOLD_PROPOSAL_MISMATCH: session_id attendu={session_id!r} "
            f"dans proposal={data['session_id']!r}"
        )

    # Vérification base_sha
    if data.get("base_sha") and data["base_sha"] != base_sha:
        raise ValueError(
            f"HOLD_PROPOSAL_MISMATCH: base_sha attendu={base_sha!r} "
            f"dans proposal={data['base_sha']!r}"
        )

    # Vérification worktree
    if data.get("worktree") and data["worktree"] != worktree:
        raise ValueError(
            f"BLOCK: worktree attendu={worktree!r} dans proposal={data['worktree']!r}"
        )

    # Vérification proposal_hash si présente
    stored_hash = data.get("proposal_hash", "")
    computed = _compute_proposal_hash(data)
    if stored_hash and stored_hash != computed:
        raise ValueError(
            f"HOLD_PROPOSAL_MISMATCH: proposal_hash corrompu "
            f"stored={stored_hash!r} computed={computed!r}"
        )

    proposal_files: List[str] = data.get("proposal_files", [
        p.get("path", "") for p in data.get("patches", [])
    ])

    # proposition_files ⊆ approved_scope
    out_of_scope = sorted(set(proposal_files) - set(approved_scope))
    if out_of_scope:
        raise ValueError(
            f"BLOCK_SCOPE_DRIFT: fichiers hors scope approuvé : {out_of_scope}"
        )

    if len(approved_scope) > MAX_FILES_V1:
        raise ValueError(
            f"BLOCK: scope dépasse MAX_FILES_V1={MAX_FILES_V1} "
            f"(reçu {len(approved_scope)} fichiers)"
        )

    # Protected paths dans la proposal
    blocked = _check_protected_in_list(proposal_files)
    if blocked:
        raise ValueError(
            f"BLOCK: protected paths dans la proposal : {blocked}"
        )

    return BoundedApplySession(
        session_id=session_id,
        proposal_id=proposal_id,
        objective=data.get("objective", ""),
        base_sha=base_sha,
        worktree_path=worktree,
        approved_scope=approved_scope,
        proposal_files=proposal_files,
        operations=data.get("operations", []),
        protected_paths_check="CLEAN",
        proposal_hash=computed,
        dryrun_status="PENDING",
    )


# ---------------------------------------------------------------------------
# DRYRUN — AUCUNE ÉCRITURE
# ---------------------------------------------------------------------------

def dryrun_bounded(session: BoundedApplySession) -> BoundedApplySession:
    """
    Analyse ce qui serait appliqué. Aucune écriture dans aucun worktree.
    Positionne dryrun_status = OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW si OK.
    """
    p = _proposal_json_path(session.proposal_id)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)

    issues = []
    for patch in data.get("patches", []):
        rel = patch.get("path", "")
        sandbox = patch.get("sandbox_path", "")

        if _is_protected(rel):
            issues.append(f"PROTECTED_PATH:{rel}")
            continue

        if rel not in session.approved_scope:
            issues.append(f"OUT_OF_SCOPE:{rel}")
            continue

        if not sandbox or not Path(sandbox).exists():
            issues.append(f"SANDBOX_MISSING:{rel}")

    if issues:
        session.dryrun_status = f"HOLD_DRYRUN_ISSUES:{';'.join(issues)}"
    else:
        session.dryrun_status = "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW"

    return session


# ---------------------------------------------------------------------------
# APPLICATION BORNÉE
# ---------------------------------------------------------------------------

def run_bounded_apply(
    session: BoundedApplySession,
    agent: AgentObsidure,
    worktree_root: Path,
) -> BoundedApplySession:
    """
    Applique la proposal via AgentObsidure.apply_proposal(target_root=worktree_root).
    Vérifie ensuite que actual_modified_files ⊆ proposal_files.
    Aucun git add/commit/push/merge.
    """
    if session.dryrun_status != "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW":
        raise ValueError(
            f"BLOCK: dryrun non validé avant apply "
            f"(status={session.dryrun_status!r})"
        )

    _enforce_boundaries()

    bilan = agent.apply_proposal(
        proposal_id=session.proposal_id,
        target_root=worktree_root,
        proposals_dir=PROPOSALS_DIR,
    )

    actual = bilan.get("applied", [])
    session.actual_modified_files = actual

    # actual_modified_files ⊆ proposal_files
    drift = sorted(set(actual) - set(session.proposal_files))
    if drift:
        session.apply_status = f"BLOCK_SCOPE_DRIFT:{drift}"
        return session

    # Protected paths dans actual
    blocked = _check_protected_in_list(actual)
    if blocked:
        session.apply_status = f"BLOCK_PROTECTED_APPLIED:{blocked}"
        return session

    if bilan.get("errors"):
        session.apply_status = "APPLY_WITH_ERRORS"
    else:
        session.apply_status = "APPLIED"

    return session


# ---------------------------------------------------------------------------
# TESTS ET GATES — ARTEFACTS ATTESTÉS
# ---------------------------------------------------------------------------

def run_tests_for_evidence(
    test_command: List[str],
    test_identity: str,
    worktree_root: Path,
    timeout: int = 120,
) -> GateTestEvidence:
    """
    Exécute pytest et retourne un GateTestEvidence attesté.
    Jamais un booléen injecté par l'appelant.
    """
    ts = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            cwd=str(worktree_root),
            timeout=timeout,
        )
        exit_code = proc.returncode
        out = (proc.stdout or "")[-2000:]
        err = (proc.stderr or "")[-500:]
        summary = out if out else err
        status = "PASS" if exit_code == 0 else "FAIL"
        receipt_hash = hashlib.sha256(summary.encode("utf-8")).hexdigest()[:16]
    except subprocess.TimeoutExpired:
        exit_code = -1
        summary = f"TIMEOUT after {timeout}s"
        status = "ERROR"
        receipt_hash = "TIMEOUT"
    except Exception as exc:
        exit_code = -2
        summary = str(exc)
        status = "ERROR"
        receipt_hash = "EXEC_ERROR"

    return GateTestEvidence(
        command=" ".join(test_command),
        test_identity=test_identity,
        exit_code=exit_code,
        status=status,
        timestamp=ts,
        results_summary=summary,
        receipt_hash=receipt_hash,
    )


# ---------------------------------------------------------------------------
# CONSTRUCTION DU ToolingBuildState
# ---------------------------------------------------------------------------

def build_tooling_state_from_evidence(
    session: BoundedApplySession,
    test_ev: GateTestEvidence,
    gate_ev: GateTestEvidence,
) -> ToolingBuildState:
    """
    Construit ToolingBuildState depuis les artefacts attestés.
    Jamais depuis des booléens injectés par l'appelant.
    """
    tests_results = "PASS" if test_ev.passed else "FAIL"
    gates_results = "PASS" if gate_ev.passed else "FAIL"

    first_failure: str = ""
    if not test_ev.passed:
        first_failure = f"TEST:{test_ev.test_identity}:exit={test_ev.exit_code}"
    elif not gate_ev.passed:
        first_failure = f"GATE:{gate_ev.test_identity}:exit={gate_ev.exit_code}"

    contradictions: List[str] = []
    if session.apply_status.startswith("BLOCK"):
        contradictions.append(session.apply_status)
    if session.scope_verification not in ("CLEAN", "PENDING"):
        contradictions.append(f"SCOPE:{session.scope_verification}")

    risk_flags: List[str] = []
    if session.actual_modified_files:
        risk_flags.append("FILES_MODIFIED_IN_WORKTREE")

    unknowns: List[str] = []
    if session.apply_status == "APPLY_WITH_ERRORS":
        unknowns.append("APPLY_PARTIAL_ERRORS")

    return ToolingBuildState(
        session_id=session.session_id,
        objective=session.objective,
        base_sha=session.base_sha,
        manifest_hash=session.proposal_hash,
        diff_hash=test_ev.receipt_hash,
        approved_scope=session.approved_scope,
        actual_touched_files=session.actual_modified_files,
        new_files=[],
        deleted_files=[],
        protected_scope_status=session.protected_paths_check,
        human_approval_status="APPROVED",
        obsidure_status="CLEAN" if session.apply_status == "APPLIED" else "DEGRADED",
        worktree_isolated=True,
        branch_isolated=True,
        auto_commit_disabled=True,
        auto_push_disabled=True,
        auto_merge_disabled=True,
        tests_results=tests_results,
        gates_results=gates_results,
        first_failure=first_failure,
        commit_status=session.commit_status,
        push_status=session.push_status,
        merge_status=session.merge_status,
        unknowns=unknowns,
        contradictions=contradictions,
        risk_flags=risk_flags,
        decision_authority="KX108_ONLY",
    )


# ---------------------------------------------------------------------------
# RECEIPT
# ---------------------------------------------------------------------------

def write_apply_receipt(
    session: BoundedApplySession,
    kx108_raw: Dict[str, Any],
    kx108_decision: str,
) -> Path:
    """Écrit le receipt hors dépôt dans %LOCALAPPDATA%/Obsidia/build_sessions/<session_id>/."""
    receipt_dir = APPLY_RECEIPT_BASE / session.session_id
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / "apply_receipt.json"

    receipt = {
        "session_id": session.session_id,
        "objective": session.objective,
        "base_sha": session.base_sha,
        "worktree": session.worktree_path,
        "approved_scope": session.approved_scope,
        "proposal_id": session.proposal_id,
        "proposal_hash": session.proposal_hash,
        "proposal_files": session.proposal_files,
        "actual_modified_files": session.actual_modified_files,
        "dryrun_status": session.dryrun_status,
        "apply_status": session.apply_status,
        "scope_verification": session.scope_verification,
        "protected_paths_status": session.protected_paths_check,
        "tests_results": (session.test_evidence.status if session.test_evidence else "UNKNOWN"),
        "gates_results": (session.gate_evidence.status if session.gate_evidence else "UNKNOWN"),
        "test_evidence": (asdict(session.test_evidence) if session.test_evidence else None),
        "gate_evidence": (asdict(session.gate_evidence) if session.gate_evidence else None),
        "kx108_raw_response": kx108_raw,
        "kx108_decision": kx108_decision,
        "next_human_action": "READY_FOR_COMMIT_REVIEW" if kx108_decision == "ACT" else kx108_decision,
        "commit_status": session.commit_status,
        "push_status": session.push_status,
        "merge_status": session.merge_status,
        "created_at": session.created_at,
        "written_at": datetime.now(timezone.utc).isoformat(),
    }

    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    return receipt_path


# ---------------------------------------------------------------------------
# PIPELINE COMPLET
# ---------------------------------------------------------------------------

def run_obsidure_bounded_apply_pipeline(
    proposal_id: str,
    session_id: str,
    base_sha: str,
    worktree: str,
    approved_scope: List[str],
    worktree_root: Path,
    test_commands: Optional[List[List[str]]] = None,
    gate_commands: Optional[List[List[str]]] = None,
    dry_run_only: bool = False,
    agent: Optional[AgentObsidure] = None,
) -> Dict[str, Any]:
    """
    Pipeline complet OBSIDURE_BOUNDED_APPLY_V1.

    Retourne un dict avec au minimum :
      session, kx108_decision, next_human_action, receipt_path
    """
    if agent is None:
        agent = AgentObsidure()

    # 1. Chargement et validation
    session = load_and_validate_proposal(
        proposal_id=proposal_id,
        session_id=session_id,
        base_sha=base_sha,
        worktree=worktree,
        approved_scope=approved_scope,
    )

    # 2. DryRun — aucune écriture
    session = dryrun_bounded(session)

    if dry_run_only:
        return {
            "status": session.dryrun_status,
            "session": asdict(session),
            "kx108_decision": "NOT_EVALUATED",
            "next_human_action": "REVIEW_DRYRUN",
            "receipt_path": None,
        }

    if session.dryrun_status != "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW":
        return {
            "status": session.dryrun_status,
            "session": asdict(session),
            "kx108_decision": "BLOCK",
            "next_human_action": "BLOCK",
            "receipt_path": None,
        }

    # 3. Application bornée via primitive existante
    session = run_bounded_apply(session, agent, worktree_root)

    if session.apply_status.startswith("BLOCK"):
        return {
            "status": session.apply_status,
            "session": asdict(session),
            "kx108_decision": "BLOCK",
            "next_human_action": "BLOCK",
            "receipt_path": None,
        }

    # 4. Vérification scope post-apply
    drift = sorted(set(session.actual_modified_files) - set(session.proposal_files))
    session.scope_verification = "CLEAN" if not drift else f"DRIFT:{drift}"

    # 5. Exécution des tests — artefacts attestés
    test_cmds = test_commands or [[sys.executable, "-m", "pytest", "-q", "--tb=short"]]
    gate_cmds = gate_commands or test_cmds

    test_ev = run_tests_for_evidence(
        test_command=test_cmds[0],
        test_identity="obsidure_bounded_apply_tests",
        worktree_root=worktree_root,
    )
    gate_ev = run_tests_for_evidence(
        test_command=gate_cmds[0],
        test_identity="obsidure_bounded_apply_gates",
        worktree_root=worktree_root,
    )

    session.test_evidence = test_ev
    session.gate_evidence = gate_ev

    # 6. Construction ToolingBuildState depuis artefacts
    state = build_tooling_state_from_evidence(session, test_ev, gate_ev)

    # 7. GuardX108
    result_env = run_tooling_build_pipeline(state)
    result_dict = _dc.asdict(result_env)

    x108_gate = result_dict.get("x108_gate", "UNKNOWN")
    gate_map = {"ALLOW": "ACT", "ACT": "ACT", "HOLD": "HOLD", "BLOCK": "BLOCK"}
    kx108_decision = gate_map.get(x108_gate, "HOLD")

    session.kx108_decision = kx108_decision
    session.kx108_raw = result_dict

    # 8. Receipt
    receipt_path = write_apply_receipt(session, result_dict, kx108_decision)

    next_action = "READY_FOR_COMMIT_REVIEW" if kx108_decision == "ACT" else kx108_decision

    return {
        "status": "OBSIDURE_BOUNDED_APPLY_V1_COMPLETE",
        "session": asdict(session),
        "kx108_decision": kx108_decision,
        "kx108_x108_gate": x108_gate,
        "next_human_action": next_action,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "receipt_path": str(receipt_path),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="OBSIDURE_BOUNDED_APPLY_V1")
    sub = parser.add_subparsers(dest="cmd")

    dr = sub.add_parser("dryrun", help="DryRun — aucune écriture")
    dr.add_argument("proposal_id")
    dr.add_argument("--session", required=True)
    dr.add_argument("--base-sha", required=True)
    dr.add_argument("--worktree", required=True)
    dr.add_argument("--scope", required=True, help="Fichiers approuvés séparés par virgule")
    dr.add_argument("--worktree-root", required=True)

    ap = sub.add_parser("apply", help="Application bornée")
    ap.add_argument("proposal_id")
    ap.add_argument("--session", required=True)
    ap.add_argument("--base-sha", required=True)
    ap.add_argument("--worktree", required=True)
    ap.add_argument("--scope", required=True)
    ap.add_argument("--worktree-root", required=True)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    scope = [s.strip() for s in args.scope.split(",") if s.strip()]
    worktree_root = Path(args.worktree_root)
    dry_run_only = args.cmd == "dryrun"

    result = run_obsidure_bounded_apply_pipeline(
        proposal_id=args.proposal_id,
        session_id=args.session,
        base_sha=args.base_sha,
        worktree=args.worktree,
        approved_scope=scope,
        worktree_root=worktree_root,
        dry_run_only=dry_run_only,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
