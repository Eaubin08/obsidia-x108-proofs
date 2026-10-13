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
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

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
    r12 inspect <checkpoint_id>  → lire la projection supervisée R12
    r12 holds <checkpoint_id>    → afficher HOLD/BLOCK R12
    r12 evidence <checkpoint_id> → afficher preuves/limites R12
    quit     → quitter
  """))


# ── Commandes spéciales ───────────────────────────────────────────────────

def _load_supervised_client():
    if str(_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPT_DIR))
    import obsidure_cli_supervised_r12 as _sup
    return _sup


def _print_json_block(title: str, payload: Mapping[str, Any]) -> None:
    print(C_TITLE(f"  {title} :"))
    print(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True))


def _git_text(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        capture_output=True,
        text=True,
        timeout=20,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[-240:]
        raise RuntimeError(detail or "GIT_READ_FAILED")
    return proc.stdout.strip()


def _proposal_json_path(proposal: Any) -> Path:
    proposal_id = str(getattr(proposal, "proposal_id", "") or "").strip()
    if not proposal_id:
        raise RuntimeError("PROPOSAL_ID_MISSING")
    path = _REPO_ROOT / "_PATCH_PROPOSALS" / proposal_id / "proposal.json"
    if not path.is_file():
        raise RuntimeError("PROPOSAL_JSON_MISSING")
    return path


def _csv_values(raw: str) -> list[str]:
    return [item.strip().replace("\\", "/").lstrip("./") for item in raw.split(",") if item.strip()]


def _load_json_object(path_raw: str, *, label: str) -> dict[str, Any] | None:
    path = Path(path_raw).expanduser()
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        print(C_WARN(f"  R12 HOLD : {label}_UNREADABLE:{type(exc).__name__}"))
        return None
    if not isinstance(data, dict):
        print(C_WARN(f"  R12 HOLD : {label}_NOT_OBJECT"))
        return None
    return data


def _read_operator_native_inputs(*, proposal: Any, exported: Any, phase1_plan: Mapping[str, Any]) -> dict[str, Any] | None:
    print(C_TITLE("  Mandat explicite requis (aucune autorisation d'exécution)."))
    mission_id = input(C_TITLE("  mission_id mandat > ")).strip()
    mandate_ref = input(C_TITLE("  référence mandat humain > ")).strip()
    target_default = ",".join(getattr(exported, "files", ()) or phase1_plan.get("candidate_patch_files") or ())
    targets_raw = input(C_TITLE(f"  chemins autorisés [{target_default}] > ")).strip() or target_default
    operations_raw = input(C_TITLE("  opérations autorisées [UPDATE_TARGET_FROM_SOURCE] > ")).strip() or "UPDATE_TARGET_FROM_SOURCE"
    tests_raw = input(C_TITLE("  commandes de test (séparées par ;) > ")).strip()
    criteria_raw = input(C_TITLE("  critères d'acceptation (séparés par ;) > ")).strip()
    provider_path = input(C_TITLE("  provider_config JSON existant > ")).strip()
    evidence_path = input(C_TITLE("  evidence bundle JSON existant > ")).strip()

    targets = _csv_values(targets_raw)
    operations = [item.upper() for item in _csv_values(operations_raw)]
    if not mission_id or not mandate_ref or not targets or not operations:
        print(C_WARN("  R12 HOLD : EXPLICIT_MANDATE_SCOPE_REQUIRED"))
        return None
    if not provider_path or not evidence_path:
        print(C_WARN("  R12 HOLD : PROVIDER_AND_EVIDENCE_BUNDLE_REQUIRED"))
        return None
    provider_config = _load_json_object(provider_path, label="PROVIDER_CONFIG")
    evidence_bundle = _load_json_object(evidence_path, label="EVIDENCE_BUNDLE")
    if provider_config is None or evidence_bundle is None:
        return None
    required = ("inventory_snapshot", "deficiency_evidence", "validation_evidence")
    missing = [name for name in required if not isinstance(evidence_bundle.get(name), Mapping)]
    if missing:
        print(C_WARN(f"  R12 HOLD : EVIDENCE_BUNDLE_INCOMPLETE:{','.join(missing)}"))
        return None
    validation = evidence_bundle["validation_evidence"]
    patch_hash = str(phase1_plan.get("candidate_patch_hash") or getattr(exported, "patch_sha256", ""))
    if str(validation.get("candidate_patch_hash") or "") != patch_hash:
        print(C_WARN("  R12 HOLD : VALIDATION_EVIDENCE_PATCH_HASH_MISMATCH"))
        return None
    return {
        "mission_id": mission_id,
        "mandate_reference": mandate_ref,
        "target_paths": targets,
        "operations": operations,
        "test_commands": [item.strip() for item in tests_raw.split(";") if item.strip()],
        "acceptance_criteria": [item.strip() for item in criteria_raw.split(";") if item.strip()] or [str(getattr(proposal, "objective", "") or "AVDR proposal prepared")],
        "provider_config": provider_config,
        "inventory_snapshot": dict(evidence_bundle["inventory_snapshot"]),
        "deficiency_evidence": dict(evidence_bundle["deficiency_evidence"]),
        "validation_evidence": dict(validation),
    }


def _build_native_r12_payload(proposal: Any) -> dict[str, Any] | None:
    try:
        from obsidure_candidate_export_v1 import (
            CandidateExportError,
            build_phase1_plan,
            export_proposal_candidate,
        )
    except Exception as exc:
        print(C_WARN(f"  R12 HOLD : CANDIDATE_EXPORT_UNAVAILABLE ({type(exc).__name__})"))
        return None

    try:
        proposal_json = _proposal_json_path(proposal)
        artifact_root = Path(tempfile.mkdtemp(prefix="obsidure_r12_candidate_"))
        exported = export_proposal_candidate(_REPO_ROOT, proposal_json, artifact_root)
        objective = str(getattr(proposal, "objective", "") or "")
        phase1_plan = build_phase1_plan(_REPO_ROOT, objective, exported)
    except CandidateExportError as exc:
        print(C_WARN(f"  R12 HOLD : AVDR_CANDIDATE_EXPORT_FAILED:{exc}"))
        return None
    except Exception as exc:
        print(C_WARN(f"  R12 HOLD : AVDR_CANDIDATE_EXPORT_ERROR:{type(exc).__name__}:{exc}"))
        return None

    try:
        head = _git_text(_REPO_ROOT, "rev-parse", "HEAD")
        branch = _git_text(_REPO_ROOT, "branch", "--show-current")
        status = _git_text(_REPO_ROOT, "status", "--short")
    except Exception as exc:
        print(C_WARN(f"  R12 HOLD : REPOSITORY_IDENTITY_UNAVAILABLE:{exc}"))
        return None
    if status.strip():
        print(C_WARN("  R12 HOLD : WORKTREE_DIRTY"))
        return None

    operator = _read_operator_native_inputs(proposal=proposal, exported=exported, phase1_plan=phase1_plan)
    if operator is None:
        return None

    candidate_files = list(getattr(exported, "files", ()) or phase1_plan.get("candidate_patch_files") or ())
    if not set(candidate_files).issubset(set(operator["target_paths"])):
        print(C_WARN("  R12 HOLD : SCOPE_VIOLATION"))
        return None

    payload = {
        "human_request": str(getattr(proposal, "objective", "") or "Prepare AVDR proposal with R12"),
        "repository_context": {
            "repository_identity": f"repo://{_REPO_ROOT.name}",
            "local_root": str(_REPO_ROOT),
            "main_worktree": str(_REPO_ROOT),
            "worktree": str(_REPO_ROOT),
            "branch": branch,
            "base_sha": head,
        },
        "proposed_scope": {
            "objective": str(getattr(proposal, "objective", "") or "Prepare AVDR proposal with R12"),
            "target_paths": candidate_files,
            "operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "tools": ["OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1", "GIT_APPLY_CHECK"],
            "test_commands": operator["test_commands"],
            "acceptance_criteria": operator["acceptance_criteria"],
        },
        "human_mandate": {
            "mission_id": operator["mission_id"],
            "status": "ACTIVE",
            "mission_authority": "KX108_ONLY",
            "human_mandate_reference": operator["mandate_reference"],
            "authorized_target_paths": operator["target_paths"],
            "authorized_operations": operator["operations"],
            "approved_tools": ["OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1", "GIT_APPLY_CHECK"],
            "mission_budget": 1,
            "attempt_limit": 1,
        },
        "provider_config": operator["provider_config"],
        "explicit_references": {
            "proposal": {
                "kind": "patch",
                "patch_id": str(getattr(proposal, "proposal_id", "") or exported.proposal_id),
                "proposal_sha256": exported.proposal_sha256,
                "candidate_patch_hash": exported.patch_sha256,
                "candidate_patch_source": str(exported.patch_path),
                "manifest_path": str(exported.manifest_path),
                "producer": "OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1",
            }
        },
        "phase1_candidate": {
            "session_id": f"avdr-{exported.proposal_id}",
            "session_contract": "OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1",
            "status": phase1_plan.get("status") or "PLAN_PROPOSED",
            "targets": candidate_files,
            "candidate_patch_hash": exported.patch_sha256,
            "candidate_files": candidate_files,
            "plan": phase1_plan,
            "producer_authority": "NONE",
            "backend_authority": "NONE",
            "decision_authority": "KX108_ONLY",
            "phase2_executed": False,
            "human_approval_synthesized": False,
            "approval_token_exposed": False,
            "repo_mutation": False,
            "mutated_repo": False,
            "world_action": False,
        },
        "inventory_snapshot": operator["inventory_snapshot"],
        "deficiency_evidence": operator["deficiency_evidence"],
        "validation_evidence": operator["validation_evidence"],
        "session_id": operator["mission_id"],
        "require_local_model_evidence": False,
    }

    print(C_TITLE("  Récapitulatif R12 PREPARE_ONLY :"))
    print(f"    proposal_id   : {getattr(proposal, 'proposal_id', exported.proposal_id)}")
    print(f"    base_sha      : {head}")
    print(f"    branch        : {branch}")
    print(f"    targets       : {', '.join(candidate_files)}")
    print(f"    mandate_ref   : {operator['mandate_reference']}")
    print(f"    patch_hash    : {exported.patch_sha256}")
    confirm = input(C_TITLE("  Confirmer PREPARE_ONLY sans ACT ? (o/N) > ")).strip().lower()
    if confirm not in {"o", "oui", "y", "yes"}:
        print(C_DIM("  R12 : préparation native annulée."))
        return None
    return payload


def _checkpoint_id_from(payload: Mapping[str, Any]) -> str:
    checkpoint = payload.get("checkpoint")
    if isinstance(checkpoint, Mapping):
        value = checkpoint.get("checkpoint_id")
        if value:
            return str(value)
    value = payload.get("checkpoint_id")
    return str(value or "")


def _mission_id_from(payload: Mapping[str, Any]) -> str:
    value = payload.get("mission_id")
    return str(value or "")


def _print_supervised_summary(payload: Mapping[str, Any]) -> None:
    status = payload.get("status") or payload.get("state") or "UNKNOWN"
    print(C_OK(f"  R12 status : {status}"))
    mission_id = _mission_id_from(payload)
    checkpoint_id = _checkpoint_id_from(payload)
    if mission_id:
        print(f"  mission_id    : {mission_id}")
    if checkpoint_id:
        print(f"  checkpoint_id : {checkpoint_id}")
    if payload.get("reason"):
        print(C_WARN(f"  reason        : {payload['reason']}"))
    if payload.get("hold"):
        _print_json_block("HOLD", payload["hold"])
    if payload.get("binder_replay"):
        _print_json_block("Binder/R8", payload["binder_replay"])
    if payload.get("verification"):
        _print_json_block("Vérification", payload["verification"])


def _supervised_projection(api_base: str, checkpoint_id: str) -> tuple[int, dict[str, Any]]:
    _sup = _load_supervised_client()
    return _sup._api_json(
        api_base,
        "GET",
        f"/api/supervised-missions/checkpoints/{checkpoint_id}/projection",
    )


def _handle_r12_command(cmd: str, api_base: str) -> bool:
    parts = cmd.strip().split()
    if len(parts) != 3 or parts[0].lower() != "r12" or parts[1].lower() not in {"inspect", "holds", "evidence"}:
        return False
    action = parts[1].lower()
    checkpoint_id = parts[2].strip()
    if not checkpoint_id:
        print(C_WARN("  Usage: r12 inspect|holds|evidence <checkpoint_id>"))
        return True

    _sup = _load_supervised_client()
    status, payload = _supervised_projection(api_base, checkpoint_id)
    if not 200 <= status < 300:
        payload.setdefault("status", "HOLD")
        payload.setdefault("reason", "PROJECTION_UNAVAILABLE")
    elif action == "holds":
        payload = _sup._holds(payload)
    elif action == "evidence":
        payload = _sup._evidence(payload)
    payload.setdefault("decision_authority", "KX108_ONLY")
    payload.update({k: payload.get(k, v) for k, v in _sup.NO_AUTHORITY.items()})
    _print_supervised_summary(payload)
    return True


def _maybe_prepare_r12_after_proposal(api_base: str, proposal: Any) -> None:
    ans = input(C_TITLE("  Préparer ce proposal via R12 PREPARE_ONLY ? (o/N) > ")).strip().lower()
    if ans not in {"o", "oui", "y", "yes"}:
        print(C_DIM("  R12 : aucune préparation demandée."))
        return

    _sup = _load_supervised_client()
    payload_file = input(C_TITLE("  Payload R12 prepare-only JSON (vide = handoff natif AVDR) > ")).strip()
    if payload_file:
        payload, reason = _sup._load_payload(payload_file)
        if reason:
            print(C_WARN(f"  R12 HOLD : {reason}"))
            return
    else:
        payload = _build_native_r12_payload(proposal)
        if payload is None:
            return

    status, result = _sup._api_json(api_base, "POST", "/api/supervised-missions/prepare-only", body=payload)
    result.setdefault("schema_version", _sup.SCHEMA_VERSION)
    result.setdefault("decision_authority", "KX108_ONLY")
    result.update({k: result.get(k, v) for k, v in _sup.NO_AUTHORITY.items()})
    _print_supervised_summary(result)

    checkpoint_id = _checkpoint_id_from(result)
    if checkpoint_id and 200 <= status < 300:
        proj_status, projection = _supervised_projection(api_base, checkpoint_id)
        if 200 <= proj_status < 300:
            projection.setdefault("decision_authority", "KX108_ONLY")
            projection.update({k: projection.get(k, v) for k, v in _sup.NO_AUTHORITY.items()})
            _print_supervised_summary(projection)
        else:
            projection.setdefault("status", "HOLD")
            projection.setdefault("reason", "PROJECTION_UNAVAILABLE")
            _print_supervised_summary(projection)


def handle_special_command(cmd: str, agent: "AgentObsidure", api_base: str) -> bool:
    """Retourne True si la commande a été traitée."""
    raw_cmd = cmd.strip()
    cmd = raw_cmd.lower()

    if _handle_r12_command(raw_cmd, api_base):
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
    sup = p.add_argument_group("mode supervise R12 (distinct du CLI AVDR historique)")
    sup.add_argument("--supervised", choices=["status", "prepare", "inspect", "holds", "evidence", "verification", "authorize"],
                     default=None, help="Mode supervise : client du backend R12 (aucune autorite d'action)")
    sup.add_argument("--mission-id", default=None)
    sup.add_argument("--checkpoint-id", default=None)
    sup.add_argument("--ticket-id", default=None)
    sup.add_argument("--payload-file", default=None, help="JSON de preparation (prepare)")
    sup.add_argument("--execution-authority-hash", default=None, help="Autorisation HUMAINE explicite (authorize)")
    sup.add_argument("--human-authorization-reference", default=None, help="Reference d'autorisation humaine (authorize)")
    sup.add_argument("--confirm-human-authorization", action="store_true",
                     help="Atteste que l'humain autorise explicitement ce hash (requis pour authorize)")
    sup.add_argument("--json", action="store_true", help="Sortie JSON (mode supervise)")
    p.add_argument("--version", action="version", version="obsidure 2.0.0")
    return p


def main() -> int:
    parser = build_parser()
    args   = parser.parse_args()

    # R12 supervised mode is a thin client for canonical backend APIs. It does
    # not instantiate AgentObsidure, invoke KX108/Binder, or create authority.
    if args.supervised:
        if str(_SCRIPT_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPT_DIR))
        import obsidure_cli_supervised_r12 as _sup
        return _sup.run_supervised(
            args.supervised,
            api=args.api,
            args={
                "mission_id": args.mission_id,
                "checkpoint_id": args.checkpoint_id,
                "ticket_id": args.ticket_id,
                "payload_file": args.payload_file,
                "execution_authority_hash": args.execution_authority_hash,
                "human_authorization_reference": args.human_authorization_reference,
                "confirm_human_authorization": args.confirm_human_authorization,
                "json": args.json,
            },
        )

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
        # ── C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1 — LEGACY_DIRECT_APPLY_DISABLED ──
        # L'apply direct legacy (mutation canonique via AgentObsidure, hors
        # séquence gouvernée KX108_PRE -> apply -> KX108_POST -> keep|rollback)
        # est fermé. Utiliser scripts/obsidia_governed_apply_v0.run_governed_content_apply.
        print(C_ERR("  LEGACY_DIRECT_APPLY_DISABLED"))
        print(C_WARN("  L'application directe de proposals via ce CLI est désactivée "
                     "(C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1)."))
        print(C_WARN("  Chemin gouverné : obsidia_governed_apply_v0.run_governed_content_apply "
                     "(KX108_PRE ALLOW + HumanApproval -> apply -> tests -> KX108_POST -> keep|rollback)."))
        return 4
        # Bloc historique conservé pour référence — inatteignable.
        print(C_WARN(f"  [APPLY] Proposal cible : {apply_id}"))  # noqa
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
            if handle_special_command(objective, agent, args.api):
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
                _maybe_prepare_r12_after_proposal(args.api, proposal)
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
