"""OBSIDIA_TERMINAL_LAW_REGISTRY_V1 — registre readonly des lois terminales.

Registre central descriptif des invariants non souverains du terminal Obsidia.
Le registry decrit. Il ne decide pas. Il n'autorise rien. Il n'interdit rien
par lui-meme : il rend visibles les lois deja en vigueur par construction.

Garanties (par construction) :
  - stdlib pur, aucun import projet, aucun reseau, aucune ecriture fichier.
  - registry_authority = NONE. decision_authority = KX108_ONLY.
  - auto_execution = False. Aucune mutation. Aucun process.
"""

from __future__ import annotations

OBSIDIA_TERMINAL_LAW_REGISTRY_VERSION = "OBSIDIA_TERMINAL_LAW_REGISTRY_V1"

_LAW_REGISTRY_COMMANDS_ONLY = [
    "python scripts/obsidia_cli.py law status",
    "python scripts/obsidia_cli.py laws",
    "python scripts/obsidia_cli.py gates",
]

_TERMINAL_LAWS = [
    {
        "id": "LAW_TERMINAL_NON_SOVEREIGN",
        "title": "Terminal is not sovereign",
        "statement": ("The terminal can guide, display, route, and propose "
                      "commands, but cannot decide."),
        "scope": ["terminal", "tui", "cli"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_KX108_ONLY_DECISION_AUTHORITY",
        "title": "Kernel-only decision authority",
        "statement": ("decision_authority=KX108_ONLY. Only the X108 kernel "
                      "holds admissibility decisions. No other layer decides."),
        "scope": ["terminal", "kernel", "all_layers"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_COMMANDS_ONLY_FOR_RISKY_OPERATIONS",
        "title": "Risky operations are commands-only",
        "statement": ("Any operation with side effects is surfaced as text "
                      "under COMMANDS_ONLY / WAITING_FOR_HUMAN, never executed."),
        "scope": ["terminal", "lean", "obsidure", "domains"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_NO_AUTO_EXECUTION",
        "title": "No automatic execution",
        "statement": ("auto_execution=False everywhere. The terminal never "
                      "runs a proposed command by itself."),
        "scope": ["terminal", "tui", "cli"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_MEMORY_IS_NOT_SOVEREIGN",
        "title": "Memory is not sovereign",
        "statement": ("Memory layers stay readonly from the terminal. "
                      "memory_write=False. Memory never decides."),
        "scope": ["memory", "brody_memory", "graphiti"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_BRODY_IS_NOT_SOVEREIGN",
        "title": "Brody is not sovereign",
        "statement": ("Brody is consultative only. Brody answers, explains, "
                      "and prepares, but never decides and never mutates."),
        "scope": ["brody", "brody_bridge", "brody_memory"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_OBSIDURE_PROPOSES_ONLY",
        "title": "Obsidure proposes only",
        "statement": ("Obsidure produces proposals in _PATCH_PROPOSALS. "
                      "The human applies. The terminal only reads."),
        "scope": ["obsidure", "proposals"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_SIGMA_ALERTS_ONLY",
        "title": "Sigma alerts only",
        "statement": ("Sigma is advisory-only. It reports coherence and "
                      "contradictions but holds no decision power."),
        "scope": ["sigma"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_OIE_REPORTS_ONLY",
        "title": "OIE reports only",
        "statement": ("OIE benchmarks are report-only. COST_REAL is never "
                      "claimed without proof. No benchmark runs from the terminal."),
        "scope": ["oie"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_DOMAINS_BRIDGE_ONLY",
        "title": "Domains are bridge-only",
        "statement": ("api_role=BRIDGE_ONLY. No financial transaction, no "
                      "trading order, no gps aviation defense action from the terminal."),
        "scope": ["domains", "bank", "trading", "gps_defense_aviation"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_LEAN_PROOF_COMMANDS_ONLY",
        "title": "Lean proof checks are commands-only",
        "statement": ("proof_write=False. lake build and lean checks are "
                      "proposed as text for the human, never launched."),
        "scope": ["lean", "proofs"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_NO_MUTATION_WITHOUT_HUMAN",
        "title": "No mutation without human",
        "statement": ("No apply, no push, no deploy, no file mutation is "
                      "initiated by the terminal. The human stays in the loop."),
        "scope": ["terminal", "git", "filesystem"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_RECEIPTS_ARE_AUDIT_NOT_AUTHORITY",
        "title": "Receipts are audit, not authority",
        "statement": ("Receipts record what happened for audit. They grant "
                      "no rights and carry no decision power."),
        "scope": ["receipts", "audit"],
        "status": "ACTIVE",
    },
    {
        "id": "LAW_GATES_ARE_ADVISORY_IN_TERMINAL",
        "title": "Gates are advisory in the terminal",
        "statement": ("The terminal gate planner is advisory-only "
                      "(NONE_GATE_PLANNER_IS_ADVISORY_ONLY). No sovereign "
                      "decision is emitted by the terminal."),
        "scope": ["gates", "gate_planner", "terminal"],
        "status": "ACTIVE",
    },
]

_KNOWN_PANELS = {
    "OBSIDURE_PROPOSAL_READER_V2": {
        "mode": "readonly",
        "law_ids": ["LAW_OBSIDURE_PROPOSES_ONLY", "LAW_NO_MUTATION_WITHOUT_HUMAN"],
        "command": "python scripts/obsidia_cli.py proposal list",
    },
    "SIGMA_OIE_STATUS_PANEL_V1": {
        "mode": "readonly",
        "law_ids": ["LAW_SIGMA_ALERTS_ONLY", "LAW_OIE_REPORTS_ONLY"],
        "command": "python scripts/obsidia_cli.py status sigma",
    },
    "BRODY_MEMORY_VISIBILITY_V1": {
        "mode": "readonly",
        "law_ids": ["LAW_BRODY_IS_NOT_SOVEREIGN", "LAW_MEMORY_IS_NOT_SOVEREIGN"],
        "command": "python scripts/obsidia_cli.py status brody memory",
    },
    "DOMAIN_BRIDGE_READONLY_V1": {
        "mode": "readonly",
        "law_ids": ["LAW_DOMAINS_BRIDGE_ONLY"],
        "command": "python scripts/obsidia_cli.py status domains",
    },
    "LEAN_PROOF_PANEL_V1": {
        "mode": "readonly",
        "law_ids": ["LAW_LEAN_PROOF_COMMANDS_ONLY"],
        "command": "python scripts/obsidia_cli.py proof status",
    },
}


def get_terminal_law_registry_v1() -> dict:
    """Retourne le registre descriptif des lois terminales. Pure, readonly."""
    return {
        "version": OBSIDIA_TERMINAL_LAW_REGISTRY_VERSION,
        "mode": "READONLY",
        "decision_authority": "KX108_ONLY",
        "registry_authority": "NONE",
        "auto_execution": False,
        "mutation": "none",
        "subprocess": "none",
        "laws": [dict(law) for law in _TERMINAL_LAWS],
        "panels": {name: dict(spec) for name, spec in _KNOWN_PANELS.items()},
        "commands_only": list(_LAW_REGISTRY_COMMANDS_ONLY),
    }


def get_terminal_law_panel_v1() -> dict:
    """Construit la reponse terminal TERMINAL_LAW_REGISTRY_V1. Pure, readonly."""
    registry = get_terminal_law_registry_v1()
    law_count = len(registry["laws"])
    panel_count = len(registry["panels"])
    reponse_text = (
        f"Law Registry readonly ({law_count} lois, {panel_count} panneaux).\n\n"
        "Le registry decrit les invariants non souverains du terminal. "
        "Il ne decide rien — registry_authority=NONE, "
        "decision_authority=KX108_ONLY."
    )
    return {
        "panel": "TERMINAL_LAW_REGISTRY_V1",
        "detected_layer": "law",
        "mode_reponse": "ANSWER_STATUS",
        "output": "COMMANDS",
        "reponse": reponse_text,
        "etat_technique": {
            "version": OBSIDIA_TERMINAL_LAW_REGISTRY_VERSION,
            "mode": "READONLY",
            "decision_authority": "KX108_ONLY",
            "registry_authority": "NONE",
            "auto_execution": False,
            "mutation": "none",
            "subprocess": "none",
        },
        "law_registry": registry,
        "main_answer": {
            "direct": reponse_text,
            "next": ["law status", "laws", "gates"],
        },
        "outils_panel": {
            "TERMINAL_LAW_REGISTRY_V1": "available",
            "law_status_cmd": "python scripts/obsidia_cli.py law status",
            "laws_cmd": "python scripts/obsidia_cli.py laws",
            "registry_authority": "NONE",
            "mutation": "none",
        },
        "next_suggestions": ["law status", "laws", "gates"],
    }


def format_terminal_law_registry_v1(data: dict) -> str:
    """Formate la reponse TERMINAL_LAW_REGISTRY_V1 pour affichage terminal."""
    etat = data.get("etat_technique", {})
    registry = data.get("law_registry", {})
    lines = [
        OBSIDIA_TERMINAL_LAW_REGISTRY_VERSION,
        f"mode={etat.get('mode', 'READONLY')}",
        f"decision_authority={etat.get('decision_authority', 'KX108_ONLY')}",
        f"registry_authority={etat.get('registry_authority', 'NONE')}",
        f"auto_execution={etat.get('auto_execution', False)}",
        "",
        "LAWS:",
    ]
    laws = registry.get("laws") or []
    lines += [f"  {law.get('id', '?')}: {law.get('status', '?')}" for law in laws] \
        if laws else ["  none"]
    lines += ["", "PANELS:"]
    panels = registry.get("panels") or {}
    lines += [f"  {name}: {spec.get('mode', '?')}" for name, spec in panels.items()] \
        if panels else ["  none"]
    lines += ["", "COMMANDS_ONLY:"]
    lines += [f"  {c}" for c in (registry.get("commands_only")
                                 or _LAW_REGISTRY_COMMANDS_ONLY)]
    lines += [
        "",
        "FORBIDDEN:",
        "  no registry authority",
        "  no automatic action",
        "  no mutation",
        "  no sovereign decision",
    ]
    return "\n".join(lines)
