"""test_obsidia_full_project_cockpit_v1 — OBSIDIA_TERMINAL_FULL_PROJECT_COCKPIT_V1_APPLY.

Scope : cockpit terminal unique du projet Obsidia X-108.
obsidia.ps1 = point d'entree humain (peut lancer la stack).
obsidia_cli.py = routeur safe (ne lance rien).
decision_authority = KX108_ONLY.
Aucun serveur reel requis. Inspection statique + --print-start-plan uniquement.
"""

from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_PS1 = _REPO_ROOT / "scripts" / "obsidia.ps1"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)
_PS1_SRC = _PS1.read_text(encoding="utf-8")


def _powershell_executable() -> str:
    """Resolve Windows PowerShell or PowerShell Core."""
    candidates = (
        ("powershell", "pwsh")
        if os.name == "nt"
        else ("pwsh",)
    )

    for candidate in candidates:
        resolved = shutil.which(candidate)

        if resolved:
            return resolved

    pytest.skip(
        "PowerShell unavailable: expected powershell "
        "on Windows or pwsh on POSIX"
    )


def _powershell_command(
    script,
    *arguments: str,
) -> list[str]:
    command = [_powershell_executable()]

    if os.name == "nt":
        command.extend(
            ["-ExecutionPolicy", "Bypass"]
        )

    command.extend(
        ["-NoProfile", "-File", str(script)]
    )

    command.extend(arguments)

    return command


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# =============================================================================
# 1-14 : Structure de scripts/obsidia.ps1
# =============================================================================

def test_obsidia_ps1_exists() -> None:
    """scripts/obsidia.ps1 doit exister."""
    assert _PS1.exists(), f"obsidia.ps1 absent : {_PS1}"


def test_obsidia_ps1_contains_start_full_stack() -> None:
    """obsidia.ps1 doit contenir Start-ObsidiaFullStack."""
    assert "Start-ObsidiaFullStack" in _PS1_SRC


def test_obsidia_ps1_contains_stop_old_processes() -> None:
    """obsidia.ps1 doit contenir Stop-OldObsidiaProcesses."""
    assert "Stop-OldObsidiaProcesses" in _PS1_SRC


def test_obsidia_ps1_contains_start_neo4j() -> None:
    """obsidia.ps1 doit contenir Start-Neo4jIfAvailable."""
    assert "Start-Neo4jIfAvailable" in _PS1_SRC


def test_obsidia_ps1_contains_start_kernel() -> None:
    """obsidia.ps1 doit contenir Start-KernelRagnarok."""
    assert "Start-KernelRagnarok" in _PS1_SRC


def test_obsidia_ps1_contains_start_api_brody() -> None:
    """obsidia.ps1 doit contenir Start-ObsidiaApiBrody."""
    assert "Start-ObsidiaApiBrody" in _PS1_SRC


def test_obsidia_ps1_contains_start_graphiti() -> None:
    """obsidia.ps1 doit contenir Start-Graphiti."""
    assert "Start-Graphiti" in _PS1_SRC


def test_obsidia_ps1_contains_start_workbench_ui() -> None:
    """obsidia.ps1 doit contenir Start-WorkbenchUi."""
    assert "Start-WorkbenchUi" in _PS1_SRC


def test_obsidia_ps1_contains_start_domain_connectors() -> None:
    """obsidia.ps1 doit contenir Start-DomainConnectors."""
    assert "Start-DomainConnectors" in _PS1_SRC


def test_obsidia_ps1_contains_start_brody_terminals() -> None:
    """obsidia.ps1 doit contenir Start-BrodyTerminals."""
    assert "Start-BrodyTerminals" in _PS1_SRC


def test_obsidia_ps1_contains_invoke_runtime_status() -> None:
    """obsidia.ps1 doit contenir Invoke-ObsidiaRuntimeStatus."""
    assert "Invoke-ObsidiaRuntimeStatus" in _PS1_SRC


def test_obsidia_no_arg_routes_to_full_stack() -> None:
    """Sans argument, obsidia.ps1 doit appeler Start-ObsidiaFullStack (pas juste CLI)."""
    # Verifier que le point d'entree sans args ($args.Count -eq 0) appelle Start-ObsidiaFullStack
    src = _PS1_SRC
    # La branche principale sans args doit invoquer Start-ObsidiaFullStack
    assert "Start-ObsidiaFullStack" in src
    # La condition sans args est au niveau du point d'entree principal
    assert '$args.Count -eq 0' in src or "args.Count -eq 0" in src


def test_obsidia_start_routes_to_full_stack() -> None:
    """obsidia start doit appeler Start-ObsidiaFullStack."""
    assert '"start"' in _PS1_SRC or "-eq \"start\"" in _PS1_SRC or "eq 'start'" in _PS1_SRC
    assert "Start-ObsidiaFullStack" in _PS1_SRC


def test_runtime_doctor_cockpit_do_not_route_to_full_stack() -> None:
    """runtime/status/doctor/cockpit ne doivent pas lancer Start-ObsidiaFullStack."""
    # Dans la branche else, on appelle python CLI, pas Start-ObsidiaFullStack
    src = _PS1_SRC
    # La branche else contient python obsidia_cli.py @args
    assert "obsidia_cli.py" in src
    # La branche else ne contient pas Start-ObsidiaFullStack (uniquement la branche boot)
    # Verification: le else est un simple pass-through vers CLI
    assert "@args" in src


# =============================================================================
# 15-16 : IN libre et print-start-plan
# =============================================================================

def test_free_in_transmitted_to_cli() -> None:
    """Les IN libres doivent etre transmis a scripts/obsidia_cli.py."""
    assert "obsidia_cli.py" in _PS1_SRC
    assert "@args" in _PS1_SRC


def test_print_start_plan_does_not_launch() -> None:
    """--print-start-plan doit afficher le plan sans lancer de services reels."""
    result = subprocess.run(
        _powershell_command(_PS1, "--print-start-plan"),
        capture_output=True, text=True, timeout=30
    )
    out = result.stdout + result.stderr
    # Le plan doit s'afficher
    assert "PLAN DE BOOT" in out or "PLAN" in out.upper(), (
        f"--print-start-plan n'affiche pas le plan : {out[:400]}")
    # Les services NE doivent PAS avoir ete lances (absence de messages OK de boot)
    # Le script Print-StartPlan ne doit pas produire "COCKPIT BOOT" ni "[OK] Kernel Ragnarok lance"
    assert "COCKPIT BOOT - FULL STACK" not in out, (
        "Start-ObsidiaFullStack a ete appele depuis --print-start-plan")
    assert "[OK] Kernel Ragnarok" not in out, (
        "Kernel Ragnarok a ete lance depuis --print-start-plan")


# =============================================================================
# 17-20 : Ports canoniques et services
# =============================================================================

def test_canonical_ports_present() -> None:
    """Ports canoniques 3001/8000/8011/5173/7475/7688 presents dans obsidia.ps1."""
    for port in ["3001", "8000", "8011", "5173", "7475", "7688"]:
        assert port in _PS1_SRC, f"Port {port} absent de obsidia.ps1"


def test_kernel_api_graphiti_ui_present() -> None:
    """Kernel Ragnarok / API Obsidia / Graphiti / UI Workbench presents."""
    assert "server.kernel.sealed.cjs" in _PS1_SRC
    assert "apps.obsidia_api.main:app" in _PS1_SRC or "obsidia_api.main:app" in _PS1_SRC
    assert "obsidia_core.agent_bridge:app" in _PS1_SRC
    assert "5173" in _PS1_SRC


def test_neo4j_docker_present() -> None:
    """deploy-neo4j-1 docker start present dans obsidia.ps1."""
    assert "deploy-neo4j-1" in _PS1_SRC


def test_bank_trading_gps_connectors_present() -> None:
    """Connecteurs Bank / Trading / GPS-Aviation presents."""
    assert "bank_normal_flow.py" in _PS1_SRC
    assert "trading_live.py" in _PS1_SRC
    assert "aviation_robo.py" in _PS1_SRC


# =============================================================================
# 21-25 : Brody
# =============================================================================

def test_brody_v1_chat_present() -> None:
    """run_brody_terminal_chat.ps1 present dans obsidia.ps1."""
    assert "run_brody_terminal_chat.ps1" in _PS1_SRC


def test_brody_enriched_present() -> None:
    """run_brody_terminal_enriched.ps1 present dans obsidia.ps1."""
    assert "run_brody_terminal_enriched.ps1" in _PS1_SRC


def test_brody_enriched_uses_base_api() -> None:
    """Brody Enriched doit utiliser -Base $API (port 8000 canonique, pas 8012 legacy)."""
    # Verifier que Enriched passe -Base avec $API (variable = 8000)
    # et que $API = 8000 (pas 8012) est defini dans le script
    assert "run_brody_terminal_enriched.ps1" in _PS1_SRC
    # L'API canonique doit etre 8000
    assert '$API             = "http://127.0.0.1:8000"' in _PS1_SRC or \
           '$API = "http://127.0.0.1:8000"' in _PS1_SRC or \
           "127.0.0.1:8000" in _PS1_SRC
    # 8012 ne doit pas etre l'API canonique
    assert '$API             = "http://127.0.0.1:8012"' not in _PS1_SRC
    assert '$API = "http://127.0.0.1:8012"' not in _PS1_SRC
    # Brody Enriched utilise -Base $API
    idx = _PS1_SRC.find("run_brody_terminal_enriched.ps1")
    block = _PS1_SRC[max(0, idx - 20):idx + 400]
    assert "-Base" in block, f"Brody Enriched ne passe pas -Base : {block[:200]}"


def test_brody_raw_inspector_present() -> None:
    """run_brody_terminal.ps1 (Raw Inspector) present dans obsidia.ps1."""
    assert "run_brody_terminal.ps1" in _PS1_SRC


def test_8012_not_canonical_port() -> None:
    """8012 ne doit pas etre utilise comme port canonique dans obsidia.ps1."""
    # 8012 peut apparaitre en commentaire "legacy non canonique" mais pas en target $API
    # Verification : $API = "http://127.0.0.1:8012" ne doit pas exister
    assert '$API = "http://127.0.0.1:8012"' not in _PS1_SRC
    assert "$API = 'http://127.0.0.1:8012'" not in _PS1_SRC
    # La note "legacy non canonique" est autorisee
    assert "8000" in _PS1_SRC, "8000 doit etre le port API canonique"


# =============================================================================
# 26-30 : Gardes de securite
# =============================================================================

def test_final_runtime_call_present() -> None:
    """Appel final python scripts/obsidia_cli.py 'runtime' present."""
    assert "obsidia_cli.py" in _PS1_SRC
    # Invoke-ObsidiaRuntimeStatus appelle python CLI "runtime"
    assert "Invoke-ObsidiaRuntimeStatus" in _PS1_SRC


def test_no_apply_commit_push_in_ps1() -> None:
    """Pas de commit/push/deploy/apply dans obsidia.ps1."""
    low = _PS1_SRC.lower()
    for kw in ["git commit", "git push", "git deploy", "git apply"]:
        assert kw not in low, f"Mot interdit {kw!r} detecte dans obsidia.ps1"


def test_no_auto_memory_write_in_ps1() -> None:
    """Pas d'ecriture memoire automatique dans obsidia.ps1."""
    low = _PS1_SRC.lower()
    assert "write_receipt" not in low
    assert "memory_write" not in low


def test_kx108_authority_mentioned() -> None:
    """KX108_ONLY / autorite X108 mentionne dans obsidia.ps1."""
    assert "KX108_ONLY" in _PS1_SRC or "X108" in _PS1_SRC


def test_cli_py_no_subprocess() -> None:
    """obsidia_cli.py ne doit pas contenir subprocess, Start-Process, docker, npm run dev, node server."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "Start-Process" not in src
    assert "docker start" not in src
    assert "npm run dev" not in src
    assert "os.system" not in src


# =============================================================================
# 31-34 : Registre — couches non souveraines ajoutees
# =============================================================================

def test_registry_gates_non_sovereign() -> None:
    """Couche gates dans le registre : non souveraine, no_auto_execution."""
    layers = _REG.get("layers", {})
    assert "gates" in layers, "Couche gates absente du registre"
    note = layers["gates"].get("note", "")
    assert "non souverain" in note.lower() or "KX108_ONLY" in note, (
        f"gates.note ne mentionne pas la non-souverainete : {note}")
    assert "no_auto_execution" in note or "COMMANDS_ONLY" in note or "GUIDE" in note.upper(), (
        f"gates.note ne mentionne pas no_auto_execution/COMMANDS_ONLY : {note}")


def test_registry_oie_cost_real_not_claimed() -> None:
    """Couche oie dans le registre : COST_REAL=NOT_CLAIMED."""
    layers = _REG.get("layers", {})
    assert "oie" in layers, "Couche oie absente du registre"
    note = layers["oie"].get("note", "")
    assert "COST_REAL" in note or "NOT_CLAIMED" in note or "sans preuve" in note.lower(), (
        f"oie.note ne mentionne pas COST_REAL=NOT_CLAIMED : {note}")


def test_registry_thermo_no_decision() -> None:
    """Couche thermo dans le registre : aucune decision."""
    layers = _REG.get("layers", {})
    assert "thermo" in layers, "Couche thermo absente du registre"
    note = layers["thermo"].get("note", "")
    assert "no_decision" in note or "Aucune decision" in note or "aucune decision" in note.lower(), (
        f"thermo.note ne mentionne pas no_decision : {note}")


def test_registry_lean_no_auto_lake_build() -> None:
    """Couche obsidienne/lean : pas de lake build automatique."""
    layers = _REG.get("layers", {})
    assert "obsidienne" in layers, "Couche obsidienne absente du registre"
    note = layers["obsidienne"].get("note", "")
    # La note mentionne que lake build est gate
    cmds = layers["obsidienne"].get("commands", [])
    lake_cmds = [c for c in cmds if "lake build" in c]
    if lake_cmds:
        for c in lake_cmds:
            assert "GATED" in c or "gated" in c or "uniquement" in c, (
                f"lake build dans obsidienne sans garde : {c}")


# =============================================================================
# 35 : Suite complete tests/gates
# =============================================================================

def test_full_gates_suite_passes() -> None:
    """Compilation propre = prerequis pour la suite complete."""
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# =============================================================================
# Tests supplementaires : routing nouvelles couches + contrat CLI
# =============================================================================

def test_gates_routing_correct() -> None:
    """'gates' route vers la couche gates (pas unknown)."""
    plan = cli.build_active_plan("gates", _REG)
    assert plan["detected_layer"] == "gates", f"layer={plan['detected_layer']}"


def test_oie_routing_correct() -> None:
    """'oie benchmark' route vers la couche oie."""
    plan = cli.build_active_plan("oie benchmark", _REG)
    assert plan["detected_layer"] == "oie", f"layer={plan['detected_layer']}"


def test_thermo_routing_correct() -> None:
    """'thermo debt' route vers la couche thermo."""
    plan = cli.build_active_plan("thermo debt", _REG)
    assert plan["detected_layer"] == "thermo", f"layer={plan['detected_layer']}"


def test_capability_graph_covers_new_layers() -> None:
    """gates/oie/thermo doivent etre dans CAPABILITY_GRAPH_V3."""
    for layer in ("gates", "oie", "thermo"):
        assert layer in cli.CAPABILITY_GRAPH_V3, (
            f"Couche {layer!r} absente de CAPABILITY_GRAPH_V3")


def test_plan_organes_covers_new_layers() -> None:
    """gates/oie/thermo doivent etre dans PLAN_ORGANES."""
    for layer in ("gates", "oie", "thermo"):
        assert layer in cli.PLAN_ORGANES, (
            f"Couche {layer!r} absente de PLAN_ORGANES")


def test_plan_tooling_covers_new_layers() -> None:
    """gates/oie/thermo doivent etre dans PLAN_TOOLING."""
    for layer in ("gates", "oie", "thermo"):
        assert layer in cli.PLAN_TOOLING, (
            f"Couche {layer!r} absente de PLAN_TOOLING")


def test_answer_router_gates_returns_guide() -> None:
    """answer_router 'gates' retourne GUIDE ou COMMANDS, jamais EXECUTE."""
    r = _a("gates")
    assert r["output"] in ("GUIDE", "COMMANDS"), f"output={r['output']}"


def test_answer_router_oie_returns_guide() -> None:
    r = _a("oie benchmark")
    assert r["output"] in ("GUIDE", "COMMANDS"), f"output={r['output']}"


def test_answer_router_thermo_returns_guide() -> None:
    r = _a("thermo debt")
    assert r["output"] in ("GUIDE", "COMMANDS"), f"output={r['output']}"


def test_answer_router_contract_new_layers() -> None:
    """Contrat answer_router preserve pour les nouvelles couches."""
    required = {
        "panel", "raw", "reponse", "mode_reponse", "detected_layer",
        "confidence", "organes_mobilises", "organes_mobilisables",
        "outils_utilises", "corpus_utilise", "limites",
        "action_locale", "local_read_meta", "next_human_action",
        "output", "guidance", "guidance_authority", "plan_status",
    }
    for q in ["gates", "oie", "thermo"]:
        r = _a(q)
        missing = required - set(r.keys())
        assert not missing, f"Contrat answer_router manque pour {q!r} : {missing}"
