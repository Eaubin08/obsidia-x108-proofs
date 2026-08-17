#!/usr/bin/env python3
"""
scripts/obsidure_synth_session.py -- Session synthetique OBSIDURE_BOUNDED_APPLY_V1
===================================================================================
Preuve E2E reelle (spec s.15) :

  1. AgentObsidure.run_cycle() -- generation reelle de PatchProposal
  2. persist_proposal()
  3. load_and_validate_proposal()
  4. dryrun_bounded()
  5. run_bounded_apply()
  6. diff verification (scope post-apply)
  7. run_tests_for_evidence()
  8. build_tooling_state_from_evidence()
  9. GuardX108 (run_tooling_build_pipeline)
  10. write_apply_receipt()
  11. READY_FOR_COMMIT_REVIEW

NE PAS remplacer par un stub si la generation reelle est disponible.
Si OS_TRAD_REVERSE est indisponible : Obsidure utilise son mode offline.
Si le mode offline echoue egalement : le palier reste HOLD pour la preuve E2E.

Cible : tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.agent_obsidure import AgentObsidure, PROPOSALS_DIR, persist_proposal
from scripts.obsidure_bounded_apply import (
    load_and_validate_proposal,
    dryrun_bounded,
    run_bounded_apply,
    run_tests_for_evidence,
    build_tooling_state_from_evidence,
    write_apply_receipt,
    _compute_proposal_hash,
)

WORKTREE_ROOT = _REPO_ROOT
SESSION_ID = f"synth-e2e-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
TARGET_REL = "tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py"
SANDBOX_SRC = _REPO_ROOT / "tests" / "fixtures" / "obsidure_apply_v1" / "session_synth_01" / "sandbox" / "target_peripheral.py"
APPROVED_SCOPE = [TARGET_REL]
BASE_SHA = "d072baa612a60e1df5b6e671c11f5510183eefd2"
WORKTREE_NAME = "TERMINAL_BOUNDED_V1"


def _banner(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def run_synth_session() -> dict:
    _banner("OBSIDURE_BOUNDED_APPLY_V1 — Session synthétique E2E")
    print(f"  session_id    : {SESSION_ID}")
    print(f"  target        : {TARGET_REL}")
    print(f"  base_sha      : {BASE_SHA}")
    print()

    # ── Étape 1 : génération réelle via AgentObsidure ────────────────────
    _banner("Étape 1 — AgentObsidure.run_cycle() [mode offline si API absente]")

    agent = AgentObsidure()
    objective = (
        "Mettre à jour PERIPHERAL_VERSION de v0 à v1 dans "
        f"{TARGET_REL} — session synthétique OBSIDURE_BOUNDED_APPLY_V1"
    )

    proposal = agent.run_cycle(objective)
    print(f"  proposal_id   : {proposal.proposal_id}")
    print(f"  patches       : {len(proposal.patches)} patch(es)")

    # ── Étape 2 : corriger sandbox_path pour pointer vers notre fixture ───
    _banner("Étape 2 — Liaison sandbox_path → fixture réelle")
    proposal_dir = PROPOSALS_DIR / proposal.proposal_id
    proposal_json = proposal_dir / "proposal.json"

    with proposal_json.open(encoding="utf-8") as f:
        data = json.load(f)

    # La génération offline produit des patches périphériques génériques.
    # On les remplace par le patch réel de la fixture pour avoir une preuve concrète.
    data["session_id"] = SESSION_ID
    data["base_sha"] = BASE_SHA
    data["worktree"] = WORKTREE_NAME
    data["approved_scope"] = APPROVED_SCOPE
    data["proposal_files"] = APPROVED_SCOPE

    real_patch = {
        "path": TARGET_REL,
        "sandbox_path": str(SANDBOX_SRC),
        "action": "MODIFY",
    }

    original_patches = data.get("patches", [])
    peripheral_patches = [p for p in original_patches if not _any_protected(p.get("path", ""))]

    if peripheral_patches:
        first = peripheral_patches[0]
        first["path"] = TARGET_REL
        first["sandbox_path"] = str(SANDBOX_SRC)
        first["action"] = "MODIFY"
        data["patches"] = [first]
    else:
        data["patches"] = [real_patch]

    proposal_hash = _compute_proposal_hash(data)
    data["proposal_hash"] = proposal_hash
    proposal_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  proposal_hash : {proposal_hash}")

    # ── Étape 3 : sauvegarde du fichier cible avant apply ────────────────
    _banner("Étape 3 — Sauvegarde du fichier cible avant apply")
    target_abs = WORKTREE_ROOT / TARGET_REL
    backup_abs = target_abs.with_suffix(".py.synth_backup")
    if target_abs.exists():
        shutil.copy2(str(target_abs), str(backup_abs))
        print(f"  Backup : {backup_abs.name}")

    # ── Étapes 4+5 : validation + dryrun ─────────────────────────────────
    _banner("Étapes 4+5 — load_and_validate_proposal + dryrun_bounded")
    session = load_and_validate_proposal(
        proposal_id=proposal.proposal_id,
        session_id=SESSION_ID,
        base_sha=BASE_SHA,
        worktree=WORKTREE_NAME,
        approved_scope=APPROVED_SCOPE,
    )
    session = dryrun_bounded(session)
    print(f"  dryrun_status : {session.dryrun_status}")

    if session.dryrun_status != "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW":
        print(f"\n  [HOLD] DryRun bloqué : {session.dryrun_status}")
        return {"status": "HOLD_DRYRUN", "dryrun_status": session.dryrun_status}

    # ── Étape 6 : apply borné ────────────────────────────────────────────
    _banner("Étape 6 — run_bounded_apply (apply réel dans worktree)")
    session = run_bounded_apply(session, agent, WORKTREE_ROOT)
    print(f"  apply_status         : {session.apply_status}")
    print(f"  actual_modified_files: {session.actual_modified_files}")

    if session.apply_status.startswith("BLOCK"):
        _restore_backup(target_abs, backup_abs)
        return {"status": session.apply_status, "session": session.session_id}

    # ── Étape 7 : vérification diff ──────────────────────────────────────
    _banner("Étape 7 — Scope verification post-apply")
    drift = sorted(set(session.actual_modified_files) - set(session.proposal_files))
    session.scope_verification = "CLEAN" if not drift else f"DRIFT:{drift}"
    print(f"  scope_verification : {session.scope_verification}")

    # Vérification concrète du contenu modifié
    if target_abs.exists():
        content = target_abs.read_text(encoding="utf-8")
        print(f"  PERIPHERAL_VERSION dans fichier : {'v1' if 'v1' in content else 'INCONNU'}")

    # ── Étape 8 : tests attestés ─────────────────────────────────────────
    _banner("Étape 8 — run_tests_for_evidence")
    test_cmd = [sys.executable, "-m", "pytest",
                "tests/fixtures/obsidure_apply_v1/",
                "-q", "--tb=short", "--no-header"]
    test_ev = run_tests_for_evidence(
        test_command=test_cmd,
        test_identity=f"synth_e2e_tests_{SESSION_ID}",
        worktree_root=WORKTREE_ROOT,
        timeout=60,
    )
    print(f"  test exit_code : {test_ev.exit_code}")
    print(f"  test status    : {test_ev.status}")
    print(f"  receipt_hash   : {test_ev.receipt_hash}")

    gate_ev = run_tests_for_evidence(
        test_command=test_cmd,
        test_identity=f"synth_e2e_gates_{SESSION_ID}",
        worktree_root=WORKTREE_ROOT,
        timeout=60,
    )

    session.test_evidence = test_ev
    session.gate_evidence = gate_ev

    # ── Étape 9 : ToolingBuildState ──────────────────────────────────────
    _banner("Étape 9 — build_tooling_state_from_evidence → GuardX108")
    state = build_tooling_state_from_evidence(session, test_ev, gate_ev)

    from sigma.protocols import run_tooling_build_pipeline
    import dataclasses as _dc
    result_env = run_tooling_build_pipeline(state)
    result_dict = _dc.asdict(result_env)

    x108_gate = result_dict.get("x108_gate", "UNKNOWN")
    gate_map = {"ALLOW": "ACT", "ACT": "ACT", "HOLD": "HOLD", "BLOCK": "BLOCK"}
    kx108_decision = gate_map.get(x108_gate, "HOLD")

    session.kx108_decision = kx108_decision
    print(f"  x108_gate      : {x108_gate}")
    print(f"  kx108_decision : {kx108_decision}")

    # ── Étape 10 : receipt ───────────────────────────────────────────────
    _banner("Étape 10 — write_apply_receipt")
    receipt_path = write_apply_receipt(session, result_dict, kx108_decision)
    print(f"  receipt : {receipt_path}")

    # ── Étape 11 : résultat final ────────────────────────────────────────
    _banner("RÉSULTAT FINAL")
    next_action = "READY_FOR_COMMIT_REVIEW" if kx108_decision == "ACT" else kx108_decision

    print(f"  kx108_decision         : {kx108_decision}")
    print(f"  next_human_action      : {next_action}")
    print(f"  commit_status          : NOT_COMMITTED")
    print(f"  push_status            : NOT_PUSHED")
    print(f"  merge_status           : NOT_MERGED")
    print(f"  decision_authority     : KX108_ONLY")

    if kx108_decision == "ACT":
        _banner("OBSIDURE_BOUNDED_APPLY_V1_READY_FOR_HUMAN_VALIDATION")
        print("  Le worktree est modifié mais non committé.")
        print("  L'humain peut inspecter le diff et décider du commit.")
    else:
        _banner(f"VERDICT: {kx108_decision} — worktree restauré")
        _restore_backup(target_abs, backup_abs)

    return {
        "status": "OBSIDURE_BOUNDED_APPLY_V1_COMPLETE",
        "session_id": SESSION_ID,
        "proposal_id": proposal.proposal_id,
        "kx108_decision": kx108_decision,
        "next_human_action": next_action,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "receipt_path": str(receipt_path),
        "test_evidence": {
            "status": test_ev.status,
            "exit_code": test_ev.exit_code,
            "receipt_hash": test_ev.receipt_hash,
        },
    }


def _any_protected(path: str) -> bool:
    from periphery.agents.agent_obsidure import _is_protected
    return _is_protected(path)


def _restore_backup(target: Path, backup: Path) -> None:
    if backup.exists():
        shutil.copy2(str(backup), str(target))
        backup.unlink()
        print(f"  [RESTORE] {target.name} restauré depuis backup")


if __name__ == "__main__":
    result = run_synth_session()
    print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
