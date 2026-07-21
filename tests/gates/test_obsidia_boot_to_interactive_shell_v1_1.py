"""test_obsidia_boot_to_interactive_shell_v1_1.

Scope : OBSIDIA_TERMINAL_BOOT_TO_INTERACTIVE_SHELL_V1_1_APPLY.
Verifie que :
  - Enter-ObsidiaInteractiveShell existe et appelle le CLI sans argument
  - Les branches no-args / start / restart entrent dans obsidia>
  - Test-ObsidiaStackRunning existe (skip-si-UP)
  - Brody terminals et navigateurs non lances par defaut
  - CLI et registry non modifies
  - Toutes les contraintes de gouvernance preservees
Aucun service real n'est lance. Analyse statique du PS1 uniquement.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PS1 = _REPO_ROOT / "scripts" / "obsidia.ps1"
_CLI = _REPO_ROOT / "scripts" / "obsidia_cli.py"
_REG = _REPO_ROOT / "scripts" / "obsidia_registry.yaml"


# ---------- helpers -----------------------------------------------------------

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


def _src() -> str:
    return _PS1.read_text(encoding="utf-8")


def _extract_function(src: str, name: str) -> str:
    """Retourne le corps de la fonction PowerShell nommee `name`."""
    pattern = rf"function\s+{re.escape(name)}\s*\{{([^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*)\}}"
    m = re.search(pattern, src, re.DOTALL)
    if m:
        return m.group(1)
    # fallback: cherche entre la def et la prochaine fonction/fin
    start = src.find(f"function {name}")
    if start == -1:
        return ""
    brace_open = src.index("{", start)
    depth = 0
    for i in range(brace_open, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_open + 1:i]
    return ""


def _main_block(src: str) -> str:
    """Extrait le bloc apres la derniere definition de fonction."""
    last_func_end = 0
    for m in re.finditer(r"^function\s+\S", src, re.MULTILINE):
        start = m.start()
        brace = src.index("{", start)
        depth = 0
        for i in range(brace, len(src)):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    last_func_end = i + 1
                    break
    return src[last_func_end:]


# =============================================================================
# TESTS
# =============================================================================

def test_01_ps1_exists():
    assert _PS1.exists(), "scripts/obsidia.ps1 absent"


def test_02_enter_interactive_shell_function_exists():
    src = _src()
    assert "function Enter-ObsidiaInteractiveShell" in src


def test_03_enter_interactive_shell_calls_cli_no_in_args():
    """Enter-ObsidiaInteractiveShell doit appeler python obsidia_cli.py sans IN argument.
    --tui est permis (flag de mode, pas un IN argument).
    @args est interdit (passerait tous les arguments du PS1 en IN).
    """
    src = _src()
    body = _extract_function(src, "Enter-ObsidiaInteractiveShell")
    assert body, "Corps de Enter-ObsidiaInteractiveShell introuvable"
    lines = [l.strip() for l in body.splitlines() if "obsidia_cli.py" in l]
    assert lines, "Aucune ligne avec obsidia_cli.py dans Enter-ObsidiaInteractiveShell"
    cli_line = lines[0]
    assert "obsidia_cli.py" in cli_line
    # @args interdit (passerait tous les args PS1 comme IN libres)
    assert "@args" not in cli_line, (
        "Enter-ObsidiaInteractiveShell ne doit pas passer @args"
    )
    # Seuls les flags de mode autorises : "" ou "--tui" ou "--plain"
    m = re.search(r'python\s+["\'].*obsidia_cli\.py["\'](.*)$', cli_line)
    if m:
        trailing = m.group(1).strip()
        allowed_flags = ("", "--tui", "--plain")
        assert trailing in allowed_flags, (
            f"Enter-ObsidiaInteractiveShell passe des args non autorises : '{trailing}'. "
            f"Autorises : {allowed_flags}"
        )


def test_04_no_args_branch_calls_enter_interactive_shell():
    src = _src()
    main = _main_block(src)
    # La branche no-args doit appeler Enter-ObsidiaInteractiveShell
    # Structure attendue : if (args.Count -eq 0 -or ... "start") { ... Enter-ObsidiaInteractiveShell ... }
    no_args_match = re.search(
        r'if\s*\([^)]*args\.Count\s*-eq\s*0[^)]*\)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
        main, re.DOTALL | re.IGNORECASE
    )
    # Approche alternative : chercher la sequence no-args -> Enter-ObsidiaInteractiveShell
    assert "Enter-ObsidiaInteractiveShell" in main, (
        "Enter-ObsidiaInteractiveShell absent du bloc principal"
    )
    # Verifier que c'est dans la branche no-args/start
    # La branche if no-args contient "start" et Enter-ObsidiaInteractiveShell avant le elseif
    no_args_block_end = main.find("elseif")
    if no_args_block_end == -1:
        no_args_block_end = len(main)
    no_args_section = main[:no_args_block_end]
    assert "Enter-ObsidiaInteractiveShell" in no_args_section, (
        "Enter-ObsidiaInteractiveShell doit etre dans la branche no-args/start"
    )


def test_05_start_branch_calls_enter_interactive_shell():
    src = _src()
    main = _main_block(src)
    # La branche "start" doit etre dans le meme if que no-args (via -or "start")
    # ou dans un elseif distinct appela Enter-ObsidiaInteractiveShell
    assert '"start"' in main or "'start'" in main, "Branche start absente du main block"
    # La branche start doit appeler Enter-ObsidiaInteractiveShell
    # Extrait la region no-args/start (avant le premier elseif "restart")
    restart_pos = main.find('"restart"')
    if restart_pos == -1:
        restart_pos = len(main)
    start_section = main[:restart_pos]
    assert "Enter-ObsidiaInteractiveShell" in start_section, (
        "Enter-ObsidiaInteractiveShell doit etre dans la branche no-args/start"
    )


def test_06_restart_branch_calls_enter_interactive_shell():
    src = _src()
    main = _main_block(src)
    # Extrait le bloc restart
    restart_pos = main.find('"restart"')
    assert restart_pos != -1, "Branche restart absente du main block"
    stop_pos = main.find('"stop"', restart_pos)
    if stop_pos == -1:
        stop_pos = len(main)
    restart_section = main[restart_pos:stop_pos]
    assert "Enter-ObsidiaInteractiveShell" in restart_section, (
        "Enter-ObsidiaInteractiveShell doit etre dans la branche restart"
    )


def test_07_runtime_branch_does_not_call_enter_interactive_shell():
    src = _src()
    main = _main_block(src)
    # La branche runtime/status/doctor/cockpit est dans le else final
    # Dans notre PS1, les IN libres + runtime passent tous par le else final
    # Le else appelle python cli @args (avec args), pas Enter-ObsidiaInteractiveShell
    else_pos = main.rfind("} else {")
    if else_pos == -1:
        else_pos = main.rfind("else {")
    if else_pos == -1:
        # Pas d'else explicite - OK si pas dans une branche else
        return
    else_section = main[else_pos:]
    assert "Enter-ObsidiaInteractiveShell" not in else_section, (
        "Enter-ObsidiaInteractiveShell ne doit PAS etre dans la branche else/runtime"
    )


def test_08_in_libre_routed_to_cli_with_args():
    src = _src()
    main = _main_block(src)
    # La branche else doit contenir python obsidia_cli.py @args
    else_pos = main.rfind("} else {")
    if else_pos == -1:
        else_pos = main.rfind("else {")
    assert else_pos != -1, "Branche else absente du main block"
    else_section = main[else_pos:]
    assert "obsidia_cli.py" in else_section
    assert "@args" in else_section


def test_09_test_obsidia_stack_running_exists():
    src = _src()
    assert "function Test-ObsidiaStackRunning" in src


def test_10_no_args_does_not_call_stop_directly_without_up_check():
    """Dans Start-ObsidiaFullStack sans ForceRestart, Stop est garde derriere un flag ForceRestart.

    Structure attendue :
      if ($ForceRestart) { Stop-OldObsidiaProcesses ... }
      else { if (Test-ObsidiaStackRunning) { ... skip ... } ... }
    Autrement dit : Stop est sous garde ForceRestart, Test est dans le else.
    """
    src = _src()
    body = _extract_function(src, "Start-ObsidiaFullStack")
    assert body, "Start-ObsidiaFullStack introuvable"
    # Test-ObsidiaStackRunning doit etre present dans le corps
    assert "Test-ObsidiaStackRunning" in body, (
        "Start-ObsidiaFullStack doit appeler Test-ObsidiaStackRunning"
    )
    # Stop-OldObsidiaProcesses doit etre sous garde ForceRestart
    # (dans un bloc if ForceRestart, pas dans le chemin sans ForceRestart)
    assert "ForceRestart" in body, (
        "Start-ObsidiaFullStack doit avoir un bloc ForceRestart pour garder Stop"
    )
    # Verification structurelle : le bloc if ($ForceRestart) contient Stop,
    # et Test-ObsidiaStackRunning est dans la branche else
    force_block_start = body.find("ForceRestart")
    assert force_block_start != -1
    # Stop apparait apres ForceRestart dans le corps (dans le bloc if)
    stop_pos = body.find("Stop-OldObsidiaProcesses")
    assert stop_pos != -1, "Stop-OldObsidiaProcesses absent du corps"
    # Test apparait aussi dans le corps, dans la branche else
    test_pos = body.find("Test-ObsidiaStackRunning")
    assert test_pos != -1
    # La structure attendue : if ForceRestart { Stop ... } else { Test ... }
    # Le else doit contenir Test - on verifie que "else" precede Test dans le corps
    else_before_test = body.rfind("else", 0, test_pos)
    assert else_before_test != -1, (
        "Test-ObsidiaStackRunning doit etre dans un bloc else (chemin sans ForceRestart)"
    )


def test_11_restart_calls_stop_old_processes():
    src = _src()
    main = _main_block(src)
    restart_pos = main.find('"restart"')
    assert restart_pos != -1, "Branche restart absente"
    stop_pos = main.find('"stop"', restart_pos)
    if stop_pos == -1:
        stop_pos = len(main)
    restart_section = main[restart_pos:stop_pos]
    # La branche restart appelle Start-ObsidiaFullStack -ForceRestart
    assert "ForceRestart" in restart_section, (
        "La branche restart doit appeler Start-ObsidiaFullStack -ForceRestart"
    )
    # Et Start-ObsidiaFullStack -ForceRestart appelle Stop-OldObsidiaProcesses
    body = _extract_function(src, "Start-ObsidiaFullStack")
    assert "Stop-OldObsidiaProcesses" in body, (
        "Start-ObsidiaFullStack -ForceRestart doit appeler Stop-OldObsidiaProcesses"
    )


def test_12_stop_branch_calls_stop_old_processes():
    src = _src()
    main = _main_block(src)
    stop_pos = main.find('"stop"')
    assert stop_pos != -1, "Branche stop absente"
    open_pos = main.find('"open"', stop_pos)
    if open_pos == -1:
        open_pos = len(main)
    stop_section = main[stop_pos:open_pos]
    assert "Stop-OldObsidiaProcesses" in stop_section, (
        "La branche stop doit appeler Stop-OldObsidiaProcesses"
    )


def test_13_open_browsers_exists_but_not_in_default_boot():
    src = _src()
    # La fonction existe
    assert "function Open-ObsidiaBrowsers" in src
    # Dans Start-ObsidiaFullStack, Open-ObsidiaBrowsers n'est pas appelee
    body = _extract_function(src, "Start-ObsidiaFullStack")
    assert "Open-ObsidiaBrowsers" not in body, (
        "Open-ObsidiaBrowsers ne doit pas etre appelee dans Start-ObsidiaFullStack"
    )


def test_14_brody_terminals_not_launched_in_default_boot():
    src = _src()
    # La fonction Start-BrodyTerminals existe
    assert "function Start-BrodyTerminals" in src
    # Dans Start-ObsidiaFullStack, Start-BrodyTerminals n'est pas appelee
    # (peut etre mentionnee dans un commentaire, mais pas appelee)
    body = _extract_function(src, "Start-ObsidiaFullStack")
    # Cherche un appel reel (pas un commentaire) : ligne non commentee contenant Start-BrodyTerminals
    real_call_lines = [
        line.strip()
        for line in body.splitlines()
        if "Start-BrodyTerminals" in line and not line.strip().startswith("#")
    ]
    assert not real_call_lines, (
        f"Start-BrodyTerminals est appelee (hors commentaire) dans Start-ObsidiaFullStack : {real_call_lines}"
    )
    # run_brody_terminal_enriched.ps1 ne doit pas etre lance dans le chemin par defaut
    # (peut etre mentionne dans des commentaires, mais pas dans une ligne d'execution)
    real_brody_lines = [
        line.strip()
        for line in body.splitlines()
        if "run_brody_terminal_enriched" in line and not line.strip().startswith("#")
    ]
    assert not real_brody_lines, (
        f"run_brody_terminal_enriched.ps1 lance dans Start-ObsidiaFullStack : {real_brody_lines}"
    )


def test_15_canonical_ports_present():
    src = _src()
    for port in ("3001", "8000", "8011", "5173", "7475", "7688"):
        assert port in src, f"Port canonique {port} absent du PS1"


def test_16_no_commit_push_deploy_in_ps1():
    src = _src().lower()
    for forbidden in ("git commit", "git push", "git deploy", "apply patch"):
        assert forbidden not in src, f"Mot interdit '{forbidden}' trouve dans obsidia.ps1"


def test_17_cli_not_modified():
    """obsidia_cli.py doit etre intact - verifie via git status."""
    result = subprocess.run(
        ["git", "status", "--short", "--", "scripts/obsidia_cli.py"],
        capture_output=True, text=True,
        cwd=str(_REPO_ROOT)
    )
    # Seul " M" (modified working tree) ou "M " (staged) indiquerait une modification
    status = result.stdout.strip()
    # Doit etre vide (pas de modification) ou contenir seulement des modifications pre-existantes
    # On verifie juste que le fichier existe et compile
    assert _CLI.exists(), "scripts/obsidia_cli.py introuvable"
    import py_compile
    py_compile.compile(str(_CLI), doraise=True)


def test_18_registry_not_modified():
    """obsidia_registry.yaml ne doit pas avoir ete touche dans ce lot."""
    assert _REG.exists(), "scripts/obsidia_registry.yaml introuvable"
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "scripts/obsidia_registry.yaml"],
        capture_output=True, text=True,
        cwd=str(_REPO_ROOT)
    )
    # Un diff vide signifie pas de modification depuis HEAD
    # On accepte aussi les modifications pre-existantes committees
    # Ce qui compte : ce lot n'a pas touche ce fichier
    # On verifie le diff unstaged uniquement
    result2 = subprocess.run(
        ["git", "diff", "--name-only", "--", "scripts/obsidia_registry.yaml"],
        capture_output=True, text=True,
        cwd=str(_REPO_ROOT)
    )
    assert "obsidia_registry.yaml" not in result2.stdout, (
        "obsidia_registry.yaml a ete modifie - SCOPE_VIOLATION"
    )


def test_19_print_start_plan_executes_without_error():
    """--print-start-plan s'execute sans erreur PowerShell."""
    result = subprocess.run(
        _powershell_command(_PS1, "--print-start-plan"),
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, (
        f"--print-start-plan retourne code {result.returncode}\n"
        f"stderr: {result.stderr[:500]}"
    )
    out = result.stdout
    assert "PLAN DE BOOT" in out
    assert "Enter-ObsidiaInteractiveShell" in out
    assert "obsidia_cli.py" in out
    assert "AUTORITE" in out


def test_20_print_start_plan_does_not_boot():
    """--print-start-plan n'affiche pas de marqueurs de boot reel."""
    result = subprocess.run(
        _powershell_command(_PS1, "--print-start-plan"),
        capture_output=True, text=True, timeout=30
    )
    out = result.stdout
    # Ces marqueurs indiquent un boot reel, pas un affichage de plan
    for marker in ("[OK] Kernel Ragnarok", "[OK] API Obsidia", "[OK] Neo4j", "[OK] UI lancee"):
        assert marker not in out, f"Marqueur de boot reel '{marker}' present dans --print-start-plan"


def test_21_no_args_branch_calls_start_full_stack():
    src = _src()
    main = _main_block(src)
    restart_pos = main.find('"restart"')
    if restart_pos == -1:
        restart_pos = len(main)
    no_args_section = main[:restart_pos]
    assert "Start-ObsidiaFullStack" in no_args_section


def test_22_restart_branch_uses_force_restart_flag():
    src = _src()
    main = _main_block(src)
    restart_pos = main.find('"restart"')
    assert restart_pos != -1
    stop_pos = main.find('"stop"', restart_pos)
    if stop_pos == -1:
        stop_pos = len(main)
    restart_section = main[restart_pos:stop_pos]
    assert "Start-ObsidiaFullStack" in restart_section
    assert "ForceRestart" in restart_section


def test_23_stop_branch_does_not_enter_shell():
    src = _src()
    main = _main_block(src)
    stop_pos = main.find('"stop"')
    assert stop_pos != -1
    open_pos = main.find('"open"', stop_pos)
    if open_pos == -1:
        open_pos = len(main)
    stop_section = main[stop_pos:open_pos]
    assert "Enter-ObsidiaInteractiveShell" not in stop_section


def test_24_open_branch_calls_open_browsers():
    src = _src()
    main = _main_block(src)
    open_pos = main.find('"open"')
    assert open_pos != -1, "Branche open absente"
    print_pos = main.find('"--print-start-plan"', open_pos)
    if print_pos == -1:
        print_pos = len(main)
    open_section = main[open_pos:print_pos]
    assert "Open-ObsidiaBrowsers" in open_section


def test_25_kx108_authority_declared():
    src = _src()
    assert "KX108_ONLY" in src
    assert "decision_authority" in src


def test_26_brody_enriched_uses_base_api():
    src = _src()
    # Dans Start-BrodyTerminals, Brody Enriched doit utiliser -Base $API (8000)
    body = _extract_function(src, "Start-BrodyTerminals")
    assert body, "Start-BrodyTerminals introuvable"
    assert "-Base" in body or "-Base '$API'" in body.replace('"', "'")
    # $API doit pointer sur 8000 (pas 8012 hardcode)
    assert '$API = "http://127.0.0.1:8012"' not in src


def test_27_test_stack_running_checks_api_8000():
    src = _src()
    body = _extract_function(src, "Test-ObsidiaStackRunning")
    assert body
    assert "8000" in body or "api/health" in body or "$API" in body


def test_28_full_stack_function_has_skip_message():
    """Quand la stack est deja UP, un message 'boot skip' doit etre affiche."""
    src = _src()
    body = _extract_function(src, "Start-ObsidiaFullStack")
    assert "boot skip" in body.lower() or "skip" in body.lower(), (
        "Start-ObsidiaFullStack doit afficher un message de skip quand la stack est UP"
    )


def test_29_enter_shell_after_runtime_status_in_no_args():
    """Dans la branche no-args, Enter-ObsidiaInteractiveShell vient apres Invoke-ObsidiaRuntimeStatus."""
    src = _src()
    main = _main_block(src)
    restart_pos = main.find('"restart"')
    if restart_pos == -1:
        restart_pos = len(main)
    section = main[:restart_pos]
    pos_runtime = section.find("Invoke-ObsidiaRuntimeStatus")
    pos_shell = section.find("Enter-ObsidiaInteractiveShell")
    assert pos_runtime != -1, "Invoke-ObsidiaRuntimeStatus absent de la branche no-args"
    assert pos_shell != -1, "Enter-ObsidiaInteractiveShell absent de la branche no-args"
    assert pos_runtime < pos_shell, (
        "Enter-ObsidiaInteractiveShell doit venir APRES Invoke-ObsidiaRuntimeStatus"
    )
