"""test_obsidia_tui_layout_v1 — OBSIDIA_TERMINAL_TUI_LAYOUT_V1_APPLY.

Scope : verifier que le TUI layout est correctement implemente dans
obsidia_cli.py : fonctions pures renderer, ANSWER_STATUS, --tui/--plain,
PS1 --tui, commandes internes TUI, non-regression routes existantes.
Aucun serveur, aucun subprocess, analyse statique + appels de fonctions pures.
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_CLI = _CLI_DIR / "obsidia_cli.py"
_PS1 = _REPO_ROOT / "scripts" / "obsidia.ps1"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli

_REG = cli.load_registry(cli.REGISTRY_PATH)


# ── helpers ───────────────────────────────────────────────────────────────────

def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


def _src_cli() -> str:
    return _CLI.read_text(encoding="utf-8")


def _src_ps1() -> str:
    return _PS1.read_text(encoding="utf-8")


# =============================================================================
# STRUCTURE DU CLI
# =============================================================================

def test_01_cli_compiles() -> None:
    py_compile.compile(str(_CLI), doraise=True)


def test_02_interactive_tui_shell_exists() -> None:
    assert hasattr(cli, "interactive_tui_shell")
    assert callable(cli.interactive_tui_shell)


def test_03_render_two_pane_layout_exists() -> None:
    assert hasattr(cli, "render_two_pane_layout")
    assert callable(cli.render_two_pane_layout)


def test_04_extract_main_answer_panel_exists() -> None:
    assert hasattr(cli, "extract_main_answer_panel")
    assert callable(cli.extract_main_answer_panel)


def test_05_extract_plan_panel_exists() -> None:
    assert hasattr(cli, "extract_plan_panel")
    assert callable(cli.extract_plan_panel)


def test_06_get_terminal_size_safe_exists() -> None:
    assert hasattr(cli, "get_terminal_size_safe")
    w, h = cli.get_terminal_size_safe()
    assert isinstance(w, int) and w > 0
    assert isinstance(h, int) and h > 0


def test_07_tui_flag_in_main_src() -> None:
    src = _src_cli()
    assert "--tui" in src
    assert "interactive_tui_shell" in src


def test_08_plain_flag_in_main_src() -> None:
    src = _src_cli()
    assert "--plain" in src


# =============================================================================
# PS1 — Enter-ObsidiaInteractiveShell appelle --tui
# =============================================================================

def test_09_ps1_calls_tui_flag() -> None:
    src = _src_ps1()
    import re
    body_match = re.search(
        r"function\s+Enter-ObsidiaInteractiveShell\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
        src, re.DOTALL
    )
    if not body_match:
        # fallback : cherche entre la def et la prochaine accolade fermante
        start = src.find("function Enter-ObsidiaInteractiveShell")
        assert start != -1, "Enter-ObsidiaInteractiveShell absent du PS1"
        brace = src.index("{", start)
        depth, body = 0, ""
        for i in range(brace, len(src)):
            if src[i] == "{": depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    body = src[brace + 1:i]
                    break
    else:
        body = body_match.group(1)

    lines_with_cli = [l.strip() for l in body.splitlines() if "obsidia_cli.py" in l]
    assert lines_with_cli, "Aucune ligne obsidia_cli.py dans Enter-ObsidiaInteractiveShell"
    cli_line = lines_with_cli[0]
    assert "--tui" in cli_line, (
        f"Enter-ObsidiaInteractiveShell doit appeler --tui, pas : '{cli_line}'"
    )


# =============================================================================
# RENDERER TUI — fonctions pures, dimensions simulees
# =============================================================================

def test_10_render_contains_obsidia_response_panel() -> None:
    screen = cli.render_two_pane_layout(
        main_lines=["[OBSIDIA RESPONSE]", "Reponse test"],
        plan_lines=["=== PLAN ==="],
        composer_hint="/help  exit",
        status_line="OBSIDIA | test",
        width=100, height=20,
    )
    assert "OBSIDIA RESPONSE" in screen


def test_11_render_contains_plan_panel() -> None:
    screen = cli.render_two_pane_layout(
        main_lines=["Reponse"],
        plan_lines=["=== PLAN ===", "layer: sigma"],
        composer_hint="hint",
        status_line="status",
        width=100, height=20,
    )
    assert "PLAN" in screen


def test_12_render_contains_composer() -> None:
    screen = cli.render_two_pane_layout(
        main_lines=["Reponse"],
        plan_lines=["PLAN"],
        composer_hint="obsidia> ",
        status_line="status",
        width=100, height=20,
    )
    assert "COMPOSER" in screen


def test_13_render_plan_is_right_of_response() -> None:
    """Plan doit etre sur la meme ligne que la reponse principale (panneau droit)."""
    screen = cli.render_two_pane_layout(
        main_lines=["RESPONSE_LEFT"],
        plan_lines=["PLAN_RIGHT"],
        composer_hint="hint",
        status_line="status",
        width=100, height=20,
    )
    for line in screen.splitlines():
        if "RESPONSE_LEFT" in line:
            assert "PLAN_RIGHT" in line, (
                "PLAN_RIGHT doit etre sur la meme ligne que RESPONSE_LEFT"
            )
            break


def test_14_render_composer_is_last_block() -> None:
    """COMPOSER doit etre dans les dernieres lignes du rendu."""
    screen = cli.render_two_pane_layout(
        main_lines=["Reponse"],
        plan_lines=["Plan"],
        composer_hint="hint",
        status_line="status",
        width=100, height=20,
    )
    lines = screen.splitlines()
    # COMPOSER doit apparaitre dans les 4 dernieres lignes
    last_block = "\n".join(lines[-5:])
    assert "COMPOSER" in last_block, "COMPOSER absent des dernieres lignes"


def test_15_render_two_pane_separator_on_same_line() -> None:
    """Les lignes de corps doivent contenir ' | ' pour separer les panneaux."""
    screen = cli.render_two_pane_layout(
        main_lines=["left"],
        plan_lines=["right"],
        composer_hint="hint",
        status_line="status",
        width=100, height=20,
    )
    body_lines = [l for l in screen.splitlines() if "left" in l or "right" in l]
    assert body_lines, "Aucune ligne de corps trouvee"
    for bl in body_lines:
        if "left" in bl:
            assert " | " in bl, f"Separateur ' | ' absent dans : {bl!r}"


# =============================================================================
# ANSWER_STATUS — detection et contenu
# =============================================================================

def test_16_obsidure_est_actif_returns_answer_status() -> None:
    r = _a("obsidure est actif ?")
    assert r["mode_reponse"] == "ANSWER_STATUS", (
        f"mode_reponse attendu ANSWER_STATUS, obtenu {r['mode_reponse']}"
    )


def test_17_obsidure_actif_has_human_answer() -> None:
    """V2 : reponse contient le texte humain (plus de header REPONSE DIRECTE).
    Motif du changement : surfaces separees — REPONSE DIRECTE etait un header interne."""
    r = _a("obsidure est actif ?")
    # La reponse doit contenir le texte humain (pas les metadonnees systeme)
    assert "Obsidure" in r["reponse"]
    assert "_PATCH_PROPOSALS" not in r["reponse"]
    assert "INTERDIT" not in r["reponse"]
    assert "ETAT" not in r["reponse"]


def test_18_brody_est_actif_returns_answer_status() -> None:
    r = _a("brody est actif ?")
    assert r["mode_reponse"] == "ANSWER_STATUS"


def test_19_stack_active_returns_status() -> None:
    r = _a("stack active")
    assert r["mode_reponse"] in ("ANSWER_STATUS", "ANSWER_LOCAL", "ANSWER_PLAN"), (
        f"stack active doit retourner un status ou plan, pas {r['mode_reponse']}"
    )
    # Au minimum, la couche doit etre live ou terminal
    assert r["detected_layer"] in ("live", "terminal_self", "unknown", "brody")


def test_20_tout_est_actif_returns_answer_status() -> None:
    r = _a("tout est actif ?")
    assert r["mode_reponse"] == "ANSWER_STATUS"


def test_21_detect_status_query_obsidure() -> None:
    target = cli.detect_status_query("obsidure est actif ?", cli.normalize("obsidure est actif ?"))
    assert target == "obsidure"


def test_22_detect_status_query_brody() -> None:
    target = cli.detect_status_query("brody est actif ?", cli.normalize("brody est actif ?"))
    assert target == "brody"


def test_23_detect_status_query_tout() -> None:
    target = cli.detect_status_query("tout est actif ?", cli.normalize("tout est actif ?"))
    assert target == "_all"


def test_24_detect_status_query_stack() -> None:
    target = cli.detect_status_query("stack active", cli.normalize("stack active"))
    assert target == "_all"


def test_25_detect_status_no_false_positive_capabilities() -> None:
    """capabilities brody ne doit PAS etre detecte comme status query."""
    target = cli.detect_status_query("capabilities brody", cli.normalize("capabilities brody"))
    assert target is None, f"False positive sur 'capabilities brody': {target}"


def test_26_detect_status_no_false_positive_peux_tu_coder() -> None:
    target = cli.detect_status_query("peux tu coder", cli.normalize("peux tu coder"))
    assert target is None


def test_27_detect_status_no_false_positive_sigma_coherence() -> None:
    target = cli.detect_status_query("sigma coherence", cli.normalize("sigma coherence"))
    assert target is None


def test_28_detect_status_no_false_positive_oie_benchmark() -> None:
    target = cli.detect_status_query("oie benchmark", cli.normalize("oie benchmark"))
    assert target is None


# =============================================================================
# NON-REGRESSION — routes existantes toujours operationnelles
# =============================================================================

def test_29_capabilities_brody_still_works() -> None:
    r = _a("capabilities brody")
    assert r["output"] in ("GUIDE", "EXECUTE", "COMMANDS")
    assert r["mode_reponse"] != "ANSWER_STATUS"


def test_30_peux_tu_coder_still_works() -> None:
    r = _a("peux tu coder")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert r["output"] in ("GUIDE", "EXECUTE")


def test_31_oie_benchmark_still_works() -> None:
    r = _a("oie benchmark")
    assert r["output"] in ("GUIDE", "COMMANDS", "EXECUTE")


def test_32_preuves_lean_still_works() -> None:
    r = _a("preuves lean")
    assert r["output"] in ("GUIDE", "COMMANDS", "EXECUTE")


def test_33_sigma_coherence_still_works() -> None:
    r = _a("sigma coherence")
    assert r["output"] in ("GUIDE", "EXECUTE", "COMMANDS")


# =============================================================================
# GOUVERNANCE — aucune mutation
# =============================================================================

def test_34_no_subprocess_in_cli() -> None:
    src = _src_cli()
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_35_no_auto_commit_push_in_cli() -> None:
    """Verifie qu'aucun appel git commit/push n'est execute depuis le CLI.
    'git commit' peut apparaitre dans des constantes de documentation (forbidden_always, etc.)
    mais pas comme appel real : run("git commit"), os.system("git commit"), etc.
    """
    import re
    src = _src_cli()
    # Cherche des patterns d'invocation reelle (subprocess, os.system, run(
    execution_patterns = [
        r'subprocess\.[a-z]+\s*\(\s*["\'].*git\s+(commit|push|deploy)',
        r'os\.system\s*\(\s*["\'].*git\s+(commit|push|deploy)',
        r'run\s*\(\s*\[["\']git["\'],\s*["\'](?:commit|push|deploy)',
    ]
    for pat in execution_patterns:
        m = re.search(pat, src, re.IGNORECASE)
        assert m is None, f"Invocation git detectee dans CLI : {m.group(0)}"


def test_36_x108_authority_in_tui_functions() -> None:
    src = _src_cli()
    assert "X108" in src
    assert "KX108_ONLY" in src or "X108=AUTHORITY" in src or "KX108" in src


def test_37_fallback_plain_if_terminal_too_small() -> None:
    """interactive_tui_shell doit contenir une logique de fallback vers plain."""
    src = _src_cli()
    # Cherche la reference au fallback dans interactive_tui_shell
    tui_start = src.find("def interactive_tui_shell")
    tui_end = src.find("\ndef interactive_shell", tui_start)
    if tui_end == -1:
        tui_end = tui_start + 5000
    tui_body = src[tui_start:tui_end]
    assert "_TUI_MIN_WIDTH" in tui_body or "trop petit" in tui_body, (
        "interactive_tui_shell doit avoir un fallback si terminal trop petit"
    )
    assert "interactive_shell" in tui_body, (
        "interactive_tui_shell doit appeler interactive_shell en fallback"
    )


def test_38_extract_main_panel_uses_main_answer_field() -> None:
    """V2 : extract_main_answer_panel utilise main_answer.direct si present.
    Motif : surfaces separees — REPONSE DIRECTE etait un header interne, plus dans LEFT."""
    resp = {
        "mode_reponse": "ANSWER_STATUS",
        "reponse": "Obsidure est actif cote terminal.",
        "main_answer": {
            "direct": "Obsidure est actif cote terminal.",
            "summary": "",
            "next": ["peux tu coder", "capabilities obsidure"],
        },
        "limites": [],
        "next_human_action": "peux tu coder",
    }
    lines = cli.extract_main_answer_panel(resp)
    combined = "\n".join(lines)
    # La reponse humaine doit etre presente
    assert "Obsidure" in combined
    # Les headers internes NE doivent PAS etre presents
    assert "REPONSE DIRECTE" not in combined
    assert "ETAT" not in combined
    assert "INTERDIT" not in combined


def test_39_extract_plan_panel_shows_layer_mode_output() -> None:
    resp = {
        "detected_layer": "obsidure",
        "mode_reponse": "ANSWER_STATUS",
        "output": "GUIDE",
        "confidence": 0.7,
        "organes_mobilises": ["Terminal [MOBILISE]"],
        "organes_mobilisables": [],
        "limites": ["limite1"],
        "next_human_action": "capabilities obsidure",
    }
    lines = cli.extract_plan_panel(resp)
    combined = "\n".join(lines)
    assert "obsidure" in combined
    assert "ANSWER_STATUS" in combined or "STATUS" in combined
    assert "GUIDE" in combined
    assert "X108" in combined


def test_40_wrap_cell_pure_function() -> None:
    lines = cli.wrap_cell("Hello world this is a test", width=10)
    for l in lines:
        assert len(l) <= 10


def test_41_wrap_cell_max_lines() -> None:
    lines = cli.wrap_cell("a\nb\nc\nd\ne", width=80, max_lines=3)
    assert len(lines) <= 3


def test_42_ps1_still_has_print_start_plan() -> None:
    """--print-start-plan doit rester fonctionnel apres modification PS1."""
    import subprocess
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS1), "--print-start-plan"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert "PLAN DE BOOT" in result.stdout


def test_43_status_response_has_correct_keys() -> None:
    r = _a("obsidure est actif ?")
    required_keys = {"mode_reponse", "detected_layer", "reponse", "output",
                     "organes_mobilises", "limites", "next_human_action"}
    for k in required_keys:
        assert k in r, f"Cle manquante dans ANSWER_STATUS : {k}"
    assert r["output"] in ("GUIDE", "EXECUTE", "COMMANDS")


def test_44_tui_min_width_constant_exists() -> None:
    assert hasattr(cli, "_TUI_MIN_WIDTH")
    assert isinstance(cli._TUI_MIN_WIDTH, int)
    assert cli._TUI_MIN_WIDTH >= 80
