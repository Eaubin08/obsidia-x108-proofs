#!/usr/bin/env python3
"""
scripts/obsidure_synth_session.py -- Session synthetique OBSIDURE_BOUNDED_APPLY_V1
===================================================================================
Preuve E2E reelle (spec s.15) :

  1. AgentObsidure.run_cycle() -- generation reelle (1 seul appel)
  2. Mise a jour des metadonnees de session uniquement (pas de remplacement patches)
  3. load_and_validate_proposal()
  4. dryrun_bounded()
  5. run_bounded_apply()
  6. diff verification (scope post-apply)
  7. target_effect_evidence -- lecture reelle du fichier modifie
  8. regression_test_evidence -- suite de tests existante
  9. build_tooling_state_from_evidence()
  10. GuardX108 (run_tooling_build_pipeline)
      ACT seulement si target_effect_evidence ET regression_test_evidence sont PASS
  11. write_apply_receipt()
  12. READY_FOR_COMMIT_REVIEW

Cible : periphery/math_core/peripheral_version_target.py
  -- chemin en periphery/ : aucune redirection par _generate_python_peripheral_patches.
  -- patches produits par run_cycle() utilises tels quels (PATCH_INJECTION = FALSE).
  -- BASE_SHA capture git rev-parse HEAD une seule fois au debut.

INTERDIT : remplacer data["patches"] apres run_cycle().
INTERDIT : injecter sandbox_path externe.
INTERDIT : court-circuiter GuardX108.
INTERDIT : falsifier test_evidence (booleen injecte).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.agent_obsidure import AgentObsidure, PROPOSALS_DIR
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
WORKTREE_NAME = "TERMINAL_BOUNDED_V1"

# Objectif pointant directement vers periphery/ : pas de redirection par l'agent.
_SYNTH_OBJECTIVE = (
    "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
    "periphery/math_core/peripheral_version_target.py -- "
    "session synthetique OBSIDURE_BOUNDED_APPLY_V1"
)


def _capture_head(worktree: Path) -> str:
    """Lit git rev-parse HEAD dans le worktree une seule fois au demarrage."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(worktree), timeout=10,
        )
        sha = r.stdout.strip()
        if r.returncode != 0 or not sha:
            raise RuntimeError(f"git rev-parse HEAD echec : {r.stderr.strip()}")
        return sha
    except Exception as exc:
        raise RuntimeError(f"Impossible de lire HEAD : {exc}") from exc


def _banner(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def run_synth_session() -> dict:
    _banner("OBSIDURE_BOUNDED_APPLY_V1 -- Session synthetique E2E")

    # -- Capture HEAD avant tout autre appel (Section 2) -----------------
    base_sha = _capture_head(WORKTREE_ROOT)
    print(f"  session_id         : {SESSION_ID}")
    print(f"  base_sha (HEAD)    : {base_sha}")
    print(f"  PATCH_INJECTION    : FALSE")
    print(f"  run_cycle_count    : 1")
    print()

    # -- Etape 1 : generation reelle via AgentObsidure (1 seul appel) ---
    _banner("Etape 1 -- AgentObsidure.run_cycle() REAL [offline si API absente]")

    agent = AgentObsidure()
    _run_cycle_count = 0

    proposal = agent.run_cycle(_SYNTH_OBJECTIVE)
    _run_cycle_count += 1

    print(f"  proposal_id        : {proposal.proposal_id}")
    print(f"  patches            : {len(proposal.patches)} patch(es)")
    print(f"  PATCH_SOURCE       : REAL_AGENTOBSIDURE")
    print(f"  run_cycle_count    : {_run_cycle_count}")

    if not proposal.patches:
        print("  [HOLD] run_cycle() a produit 0 patch -- chaine reelle bloquee.")
        return {"status": "HOLD_NO_PATCHES", "proposal_id": proposal.proposal_id}

    assert _run_cycle_count == 1, "Invariant : run_cycle() ne doit etre appele qu'une fois"

    # -- Etape 2 : metadonnees de session uniquement (pas de patches) ---
    _banner("Etape 2 -- Metadonnees de session (PATCH_INJECTION = FALSE)")
    proposal_dir = PROPOSALS_DIR / proposal.proposal_id
    proposal_json = proposal_dir / "proposal.json"

    with proposal_json.open(encoding="utf-8") as f:
        data = json.load(f)

    # Chemins reels produits par l'agent -- NE PAS remplacer
    actual_patch_paths = [p["path"] for p in data.get("patches", [])]
    print(f"  chemins generes    : {actual_patch_paths}")

    peripheral_ok = all(p.startswith("periphery/") for p in actual_patch_paths)
    if not peripheral_ok:
        print(f"  [HOLD] Patches hors periphery/ : {actual_patch_paths}")
        return {"status": "HOLD_PATCH_OUT_OF_PERIPHERY", "paths": actual_patch_paths}

    # Mise a jour des seules metadonnees de session
    data["session_id"] = SESSION_ID
    data["base_sha"] = base_sha
    data["worktree"] = WORKTREE_NAME
    data["approved_scope"] = actual_patch_paths
    data["proposal_files"] = actual_patch_paths

    proposal_hash = _compute_proposal_hash(data)
    data["proposal_hash"] = proposal_hash
    proposal_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  proposal_hash      : {proposal_hash}")
    print(f"  PATCH_INJECTION    : FALSE")

    # -- Etape 3 : sauvegarde si cible existante -------------------------
    _banner("Etape 3 -- Sauvegarde avant apply")
    target_rel = actual_patch_paths[0]
    target_abs = WORKTREE_ROOT / target_rel
    backup_abs = target_abs.with_suffix(".py.synth_backup")
    if target_abs.exists():
        shutil.copy2(str(target_abs), str(backup_abs))
        print(f"  Backup             : {backup_abs.name}")
    else:
        print(f"  Cible inexistante (nouveau fichier) : {target_rel}")

    # -- Etapes 4+5 : validation + dryrun --------------------------------
    _banner("Etapes 4+5 -- load_and_validate_proposal + dryrun_bounded")
    session = load_and_validate_proposal(
        proposal_id=proposal.proposal_id,
        session_id=SESSION_ID,
        base_sha=base_sha,
        worktree=WORKTREE_NAME,
        approved_scope=actual_patch_paths,
    )
    session = dryrun_bounded(session)
    print(f"  dryrun             : {session.dryrun_status}")

    if session.dryrun_status != "OBSIDURE_DRYRUN_READY_FOR_PROPOSAL_REVIEW":
        print(f"\n  [HOLD] DryRun bloque : {session.dryrun_status}")
        return {"status": "HOLD_DRYRUN", "dryrun_status": session.dryrun_status}

    # -- Etape 6 : apply borne -------------------------------------------
    _banner("Etape 6 -- run_bounded_apply (apply reel)")
    session = run_bounded_apply(session, agent, WORKTREE_ROOT)
    print(f"  apply_status       : {session.apply_status}")
    print(f"  actual_modified    : {session.actual_modified_files}")

    if session.apply_status.startswith("BLOCK"):
        _restore_backup(target_abs, backup_abs)
        return {"status": session.apply_status, "session": session.session_id}

    # -- Etape 7 : scope verification ------------------------------------
    _banner("Etape 7 -- Scope verification post-apply")
    drift = sorted(set(session.actual_modified_files) - set(session.proposal_files))
    session.scope_verification = "CLEAN" if not drift else f"DRIFT:{drift}"
    print(f"  scope_verification : {session.scope_verification}")

    # -- Etape 8a : TARGET_EFFECT_EVIDENCE (lecture reelle du fichier) ---
    _banner("Etape 8a -- target_effect_evidence (lecture fichier modifie)")
    check_script = (
        "import sys; from pathlib import Path; "
        "p = Path('" + target_rel.replace("\\", "/") + "'); "
        "assert p.exists(), 'Fichier non cree: ' + str(p); "
        "c = p.read_text(encoding='utf-8'); "
        "lines = [l.strip() for l in c.splitlines() if 'PERIPHERAL_VERSION' in l]; "
        "assert lines, 'PERIPHERAL_VERSION absent du fichier'; "
        "assert any('v1' in l for l in lines), "
        "'PERIPHERAL_VERSION=v1 non confirme: ' + str(lines); "
        "print('TARGET_EFFECT_PASS: PERIPHERAL_VERSION=v1 confirme'); sys.exit(0)"
    )
    target_effect_cmd = [sys.executable, "-c", check_script]
    target_effect_ev = run_tests_for_evidence(
        test_command=target_effect_cmd,
        test_identity=f"target_effect_{SESSION_ID}",
        worktree_root=WORKTREE_ROOT,
        timeout=30,
    )
    print(f"  target_effect      : {target_effect_ev.status} (exit={target_effect_ev.exit_code})")
    print(f"  receipt_hash       : {target_effect_ev.receipt_hash}")
    if not target_effect_ev.passed:
        print(f"  [HOLD] target_effect FAIL : {target_effect_ev.results_summary[:200]}")

    # -- Etape 8b : REGRESSION_TEST_EVIDENCE (suite de tests moteur) -----
    _banner("Etape 8b -- regression_test_evidence (suite obsidure_bounded_apply)")
    regression_cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_obsidure_bounded_apply_v1.py",
        "-q", "--tb=short", "--no-header",
    ]
    regression_ev = run_tests_for_evidence(
        test_command=regression_cmd,
        test_identity=f"regression_{SESSION_ID}",
        worktree_root=WORKTREE_ROOT,
        timeout=180,
    )
    print(f"  regression         : {regression_ev.status} (exit={regression_ev.exit_code})")
    print(f"  receipt_hash       : {regression_ev.receipt_hash}")

    session.test_evidence = target_effect_ev
    session.gate_evidence = regression_ev

    both_pass = target_effect_ev.passed and regression_ev.passed

    # -- Etape 9 : ToolingBuildState + GuardX108 -------------------------
    _banner("Etape 9 -- build_tooling_state_from_evidence -> GuardX108")
    # test_ev = target_effect, gate_ev = regression
    state = build_tooling_state_from_evidence(session, target_effect_ev, regression_ev)

    from sigma.protocols import run_tooling_build_pipeline
    import dataclasses as _dc
    result_env = run_tooling_build_pipeline(state)
    result_dict = _dc.asdict(result_env)

    x108_gate = result_dict.get("x108_gate", "UNKNOWN")
    gate_map = {"ALLOW": "ACT", "ACT": "ACT", "HOLD": "HOLD", "BLOCK": "BLOCK"}
    kx108_decision = gate_map.get(x108_gate, "HOLD")

    # ACT seulement si les deux evidences passent
    if kx108_decision == "ACT" and not both_pass:
        kx108_decision = "HOLD"
        print("  [HOLD] KX108 retrogradé : target_effect ou regression non PASS")

    session.kx108_decision = kx108_decision
    print(f"  x108_gate          : {x108_gate}")
    print(f"  kx108_decision     : {kx108_decision}")

    # -- Etape 10 : receipt ----------------------------------------------
    _banner("Etape 10 -- write_apply_receipt")
    receipt_path = write_apply_receipt(session, result_dict, kx108_decision)
    print(f"  receipt            : {receipt_path}")

    # -- Etape 11 : resultat final ---------------------------------------
    _banner("RESULTAT FINAL")
    next_action = "READY_FOR_COMMIT_REVIEW" if kx108_decision == "ACT" else kx108_decision

    print(f"  base_sha                   : {base_sha}")
    print(f"  AgentObsidure.run_cycle    : REAL")
    print(f"  run_cycle_count            : {_run_cycle_count}")
    print(f"  patches                    : {len(proposal.patches)}")
    print(f"  PATCH_SOURCE               : REAL_AGENTOBSIDURE")
    print(f"  PATCH_INJECTION            : FALSE")
    print(f"  dryrun                     : PASS")
    print(f"  apply                      : {session.apply_status}")
    print(f"  scope_verification         : {session.scope_verification}")
    print(f"  target_effect_evidence     : {target_effect_ev.status}")
    print(f"  regression_test_evidence   : {regression_ev.status}")
    print(f"  gates                      : {'PASS' if both_pass else 'FAIL'}")
    print(f"  x108_gate                  : {x108_gate}")
    print(f"  kx108_decision             : {kx108_decision}")
    print(f"  next_human_action          : {next_action}")
    print(f"  commit_status              : NOT_COMMITTED")
    print(f"  push_status                : NOT_PUSHED")
    print(f"  merge_status               : NOT_MERGED")
    print(f"  decision_authority         : KX108_ONLY")

    if kx108_decision == "ACT":
        _banner("OBSIDURE_BOUNDED_APPLY_V1_READY_FOR_HUMAN_VALIDATION")
        print("  Le worktree est modifie mais non committe.")
        print("  L'humain peut inspecter le diff et decider du commit.")
    else:
        _banner(f"VERDICT: {kx108_decision} -- worktree restaure")
        _restore_backup(target_abs, backup_abs)

    return {
        "status": "OBSIDURE_BOUNDED_APPLY_V1_COMPLETE",
        "session_id": SESSION_ID,
        "proposal_id": proposal.proposal_id,
        "proposal_hash": proposal_hash,
        "base_sha": base_sha,
        "kx108_decision": kx108_decision,
        "next_human_action": next_action,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "decision_authority": "KX108_ONLY",
        "receipt_path": str(receipt_path),
        "patch_source": "REAL_AGENTOBSIDURE",
        "patch_injection": False,
        "run_cycle_count": _run_cycle_count,
        "target_effect_evidence": {
            "status": target_effect_ev.status,
            "exit_code": target_effect_ev.exit_code,
            "receipt_hash": target_effect_ev.receipt_hash,
        },
        "regression_test_evidence": {
            "status": regression_ev.status,
            "exit_code": regression_ev.exit_code,
            "receipt_hash": regression_ev.receipt_hash,
        },
    }


def _restore_backup(target: Path, backup: Path) -> None:
    if backup.exists():
        shutil.copy2(str(backup), str(target))
        backup.unlink()
        print(f"  [RESTORE] {target.name} restaure depuis backup")
    elif target.exists():
        target.unlink()
        print(f"  [RESTORE] {target.name} supprime (fichier nouveau)")


if __name__ == "__main__":
    result = run_synth_session()
    print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
