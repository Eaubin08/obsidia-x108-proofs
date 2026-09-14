#!/usr/bin/env python3
"""
scripts/obsidure_cli.py — Point d'entrée CLI de l'Agent Obsidure
=================================================================
Usage :
  python scripts/obsidure_cli.py
  python scripts/obsidure_cli.py --objective "Créer le gate bank P3-01"
  python scripts/obsidure_cli.py --objective "Théorème Lean P107" --domain LEAN
  python scripts/obsidure_cli.py --max-cycles 3 --dry-run
  python scripts/obsidure_cli.py --api http://127.0.0.1:8000

Options :
  --objective TEXT     Objectif direct (sinon mode interactif)
  --domain TEXT        BANK | TRADING | GPS | ECOM | LEAN | SRL (optionnel)
  --max-cycles N       Nombre max de cycles AVDR (défaut: illimité en interactif)
  --api URL            Base URL de l'API (défaut: http://127.0.0.1:8000)
  --dry-run            Audit seul — aucune sandbox ni proposal créé
  --quiet              Sortie minimale
  --version            Version de l'agent

Standalone — NE PAS brancher à l'UI Cockpit ou au moteur Brody pour l'instant.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ajout du repo root au path pour imports
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from periphery.agents.agent_obsidure import (
        AgentObsidure,
        AGENT_OBSIDURE_BOUNDARY,
        ProtectedPathError,
        BackupFailedError,
        ImmutableBoundaryError,
        AVDRPhase,
    )
    _IMPORT_OK = True
except ImportError as _imp_err:
    _IMPORT_OK = False
    _IMPORT_ERR = str(_imp_err)


# ── Couleurs ANSI (désactivables) ──────────────────────────────────────────
_COLOR = os.environ.get("OBSIDURE_COLOR", "1") != "0" and sys.stdout.isatty()

def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text

C_TITLE  = lambda t: _c(t, "1;36")  # cyan gras
C_OK     = lambda t: _c(t, "1;32")  # vert
C_WARN   = lambda t: _c(t, "1;33")  # jaune
C_ERR    = lambda t: _c(t, "1;31")  # rouge
C_DIM    = lambda t: _c(t, "2")     # gris


# ── Bannière ───────────────────────────────────────────────────────────────

BANNER = """
  ╔══════════════════════════════════════════════════════════════╗
  ║          AGENT OBSIDURE — v2.0 — CLI STANDALONE             ║
  ║    CO_PILOTE_CODE (#6) × CI_REPO_SURGEON (#7)               ║
  ║                                                              ║
  ║  Bâtisseur périphérique Obsidia X-108                       ║
  ║  Domaines · Mémoire SRL · Lean 4 · Patches                  ║
  ║                                                              ║
  ║  Kernel X-108 = MUR DE BÉTON INTOUCHABLE                    ║
  ║  Toute sortie attend HUMAN_APPROVED_WRITE                    ║
  ╚══════════════════════════════════════════════════════════════╝
"""


def print_banner() -> None:
    print(C_TITLE(BANNER))


def print_boundary() -> None:
    print(C_DIM("  Frontières actives :"))
    for k, v in AGENT_OBSIDURE_BOUNDARY.items():
        color = C_OK if v is False or v == "KX108_ONLY" or v == "HUMAN_APPROVED_WRITE" else C_WARN
        print(f"    {k:<30} = {color(str(v))}")
    print()


def print_menu() -> None:
    print(C_DIM("""
  Commandes spéciales (en mode interactif) :
    status   → état du cycle courant
    srl      → résumé mémoire SRL
    domains  → audit des gates P3
    boundary → afficher les frontières de sécurité
    context navier → lire les sources Navier-Stokes, sans cycle ni proposal
    quit     → quitter
  """))


# ── Commandes spéciales ───────────────────────────────────────────────────

def handle_special_command(cmd: str, agent: "AgentObsidure") -> bool:
    """Retourne True si la commande a été traitée."""
    cmd = cmd.strip().lower()

    if cmd == "context navier":
        import json
        from periphery.agents.agent_obsidure import _build_math_memory_context_pack
        context = _build_math_memory_context_pack("NS_ANTI_PUMPING")
        print(json.dumps(context, ensure_ascii=False, indent=2))
        print("Lecture documentaire uniquement; aucune preuve ni analyse automatique effectuee.")
        return True

    if cmd == "status":
        print(f"  Phase courante : {C_OK(agent.phase.value)}")
        print(f"  Cycles AVDR   : {agent._cycle}")
        print(f"  Proposals     : {len(agent.proposals)}")
        return True

    if cmd == "srl":
        summary = agent._srl.read_summary()
        print(C_TITLE("  Mémoire SRL (lecture seule) :"))
        for tier, count in summary["tiers"].items():
            print(f"    {tier:<20} : {count} fichier(s)")
        print(f"    memory_write : {C_ERR('False')} (invariant permanent)")
        return True

    if cmd == "domains":
        print(C_TITLE("  Audit gates P3 :"))
        for domain in ("BANK", "TRADING", "GPS", "ECOM"):
            audit = agent._domain_brancher.audit_domain(domain)
            for key, info in audit.get("files", {}).items():
                status = C_OK("EXISTE") if info["exists"] else C_WARN("ABSENT")
                print(f"    {domain}/{key:<12} : {status}  {info['path']}")
        return True

    if cmd == "boundary":
        print_boundary()
        return True

    return False


# ── Main ──────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obsidure",
        description="Agent Obsidure — Bâtisseur CLI Obsidia X-108",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--objective", "-o", default=None, help="Objectif direct (mode non-interactif)")
    p.add_argument("--domain",    "-d", default=None, choices=["BANK","TRADING","GPS","ECOM","LEAN","SRL"],
                   help="Domaine cible (optionnel — détection automatique sinon)")
    p.add_argument("--max-cycles", "-n", type=int, default=None, help="Nombre max de cycles")
    p.add_argument("--api", default=os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000"),
                   help="Base URL de l'API OS_TRAD_REVERSE")
    p.add_argument("--apply", "-a", default=None, metavar="PROPOSAL_ID",
                   help="Applique un proposal existant (HUMAN_APPROVED_WRITE)")
    p.add_argument("--dry-run", action="store_true", help="Audit seul — aucun patch généré")
    p.add_argument("--quiet", "-q", action="store_true", help="Sortie minimale")
    p.add_argument("--version", action="version", version="obsidure 2.0.0")
    return p


def main() -> int:
    parser = build_parser()
    args   = parser.parse_args()

    if not _IMPORT_OK:
        print(C_ERR(f"Erreur d'import : {_IMPORT_ERR}"))
        print(C_WARN("Vérifiez que periphery/agents/agent_obsidure.py est présent."))
        return 1

    if not args.quiet:
        print_banner()
        print_boundary()

    if args.dry_run:
        print(C_WARN("  Mode DRY-RUN — audit seul, aucun patch ni backup."))

    agent = AgentObsidure(
        api_base=args.api,
        max_cycles=args.max_cycles,
        verbose=not args.quiet,
    )

    # ── Mode APPLY_PROPOSAL ──────────────────────────────────────────────
    # Déclenché par --apply <id> OU --objective "APPLY_PROPOSAL <id>"
    apply_id = args.apply
    if not apply_id and args.objective:
        obj_stripped = args.objective.strip()
        if obj_stripped.upper().startswith("APPLY_PROPOSAL"):
            parts = obj_stripped.split()
            if len(parts) >= 2:
                apply_id = parts[1]

    if apply_id:
        print(C_WARN(f"  [APPLY] Proposal cible : {apply_id}"))
        try:
            bilan = agent.apply_proposal(apply_id)
            if bilan["applied"]:
                print(C_OK(f"\n  APPLIQUÉ ({len(bilan['applied'])} fichier(s)) :"))
                for p in bilan["applied"]:
                    print(C_OK(f"    ✓ {p}"))
            if bilan["skipped"]:
                print(C_WARN(f"  IGNORÉ ({len(bilan['skipped'])}) :"))
                for s in bilan["skipped"]:
                    print(C_WARN(f"    ~ {s['path']} ({s['reason']})"))
            if bilan["errors"]:
                print(C_ERR(f"  ERREURS ({len(bilan['errors'])}) :"))
                for e in bilan["errors"]:
                    print(C_ERR(f"    ✗ {e['path']} ({e['reason']})"))
            print(C_OK(f"\n  Statut final : {bilan['status']}"))
        except FileNotFoundError as exc:
            print(C_ERR(f"  Proposal introuvable : {exc}"))
            return 1
        except Exception as exc:
            print(C_ERR(f"  Erreur apply : {exc}"))
            return 4
        return 0

    # ── Mode non-interactif (--objective fourni) ─────────────────────────
    if args.objective:
        objective = args.objective
        if args.domain:
            objective = f"[DOMAINE:{args.domain}] {objective}"
        if args.dry_run:
            print(C_WARN(f"  [DRY-RUN] Objectif : {objective}"))
            result = agent.phase_a_audit(objective)
            print(f"  Intent      : {result.intent}")
            print(f"  Source      : {result.source}")
            print(f"  Risk flags  : {result.risk_flags}")
            return 0
        try:
            proposal = agent.run_cycle(objective)
            if not args.quiet:
                print(C_OK(f"\n  Proposal émis avec succès."))
                print(f"  ID       : {proposal.proposal_id}")
                print(f"  Receipt  : _PATCH_PROPOSALS/{proposal.proposal_id}/RECEIPT.md")
                print(f"  Patches  : {len(proposal.patches)}")
        except ProtectedPathError as exc:
            print(C_ERR(f"\n  BLOC ABSOLU : {exc}"))
            return 2
        except BackupFailedError as exc:
            print(C_ERR(f"\n  FAIL-CLOSED : {exc}"))
            return 3
        except Exception as exc:
            print(C_ERR(f"\n  Erreur : {exc}"))
            return 4
        return 0

    # ── Mode interactif ───────────────────────────────────────────────────
    if not args.quiet:
        print_menu()

    try:
        while True:
            if agent._max_cycles and agent._cycle >= agent._max_cycles:
                print(f"\n  max-cycles={agent._max_cycles} atteint.")
                break
            try:
                objective = input(C_TITLE("\n[OBSIDURE] Objectif > ")).strip()
            except EOFError:
                break

            if not objective:
                continue
            if objective.lower() in ("quit", "exit", "q"):
                print("  Arrêt.")
                break
            if handle_special_command(objective, agent):
                continue

            if args.domain:
                objective = f"[DOMAINE:{args.domain}] {objective}"

            if args.dry_run:
                try:
                    result = agent.phase_a_audit(objective)
                    print(C_WARN(f"  [DRY-RUN] intent={result.intent} source={result.source}"))
                except ProtectedPathError as exc:
                    print(C_ERR(f"  BLOC : {exc}"))
                    break
                continue

            try:
                proposal = agent.run_cycle(objective)
                print(C_OK(f"\n  Proposal prêt : _PATCH_PROPOSALS/{proposal.proposal_id}/RECEIPT.md"))
            except ProtectedPathError as exc:
                print(C_ERR(f"  BLOC ABSOLU : {exc}"))
                break
            except BackupFailedError as exc:
                print(C_ERR(f"  FAIL-CLOSED : {exc}"))
                break
            except Exception as exc:
                print(C_ERR(f"  Erreur : {exc}"))

    except KeyboardInterrupt:
        print("\n  Arrêt (Ctrl+C).")

    print(f"\n  Cycles : {agent._cycle}  |  Proposals : {len(agent.proposals)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
