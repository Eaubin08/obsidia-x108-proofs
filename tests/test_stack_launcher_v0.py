"""
tests/test_stack_launcher_v0.py — Suite Phase 6 : Stack Launcher Terminal/Brody/Obsidure
==========================================================================================
Vérifie :
  - scripts de lancement présents et syntaxiquement corrects
  - composants présents
  - défaut port canonique (8000 non 8012)
  - aucune mutation du dépôt pendant status/help/doctor
  - aucun secret dans stdout
  - chemins Windows avec espaces
  - UTF-8
  - KX108_ONLY préservé
  - stack_status.ps1 présent
  - Obsidure CLI importable

NE LANCE AUCUN SERVEUR. NE COMMIT RIEN. LECTURE SEULE.
decision_authority = KX108_ONLY
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

# ── Racine du repo ─────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
PERIPHERY = REPO / "periphery"
TESTS = REPO / "tests"

# =============================================================================
# GROUPE A — Présence des fichiers
# =============================================================================

class TestFilePresence:
    """Vérifie que tous les fichiers du lanceur sont présents."""

    def test_cockpit_ps1_present(self):
        assert (SCRIPTS / "obsidia.ps1").is_file(), "scripts/obsidia.ps1 manquant"

    def test_stack_status_ps1_present(self):
        assert (SCRIPTS / "stack_status.ps1").is_file(), "scripts/stack_status.ps1 manquant"

    def test_stop_all_servers_present(self):
        assert (SCRIPTS / "OBSIDIA_LAUNCHERS" / "00_STOP_ALL_SERVERS.ps1").is_file()

    def test_start_brody_stack_present(self):
        assert (SCRIPTS / "OBSIDIA_LAUNCHERS" / "01_START_BRODY_STACK.ps1").is_file()

    def test_run_agent_obsidure_ps1_present(self):
        assert (SCRIPTS / "run_agent_obsidure.ps1").is_file()

    def test_obsidure_cli_py_present(self):
        assert (SCRIPTS / "obsidure_cli.py").is_file()

    def test_obsidia_cli_py_present(self):
        assert (SCRIPTS / "obsidia_cli.py").is_file()

    def test_brody_terminal_enriched_present(self):
        assert (SCRIPTS / "run_brody_terminal_enriched.ps1").is_file()

    def test_brody_terminal_chat_present(self):
        assert (SCRIPTS / "run_brody_terminal_chat.ps1").is_file()

    def test_agent_obsidure_py_present(self):
        assert (PERIPHERY / "agents" / "agent_obsidure.py").is_file()


# =============================================================================
# GROUPE B — Port canonique
# =============================================================================

class TestCanonicalPort:
    """Vérifie que les scripts utilisent le port canonique 8000, pas 8012."""

    def test_brody_enriched_default_port_is_8000(self):
        content = (SCRIPTS / "run_brody_terminal_enriched.ps1").read_text(encoding="utf-8")
        # Le param doit avoir 8000 comme défaut
        match = re.search(r'\$Base\s*=\s*["\']http://127\.0\.0\.1:(\d+)["\']', content)
        assert match is not None, "Paramètre $Base introuvable dans run_brody_terminal_enriched.ps1"
        assert match.group(1) == "8000", (
            f"Port par défaut = {match.group(1)}, attendu 8000 (8012 est legacy)"
        )

    def test_cockpit_canonical_ports_defined(self):
        content = (SCRIPTS / "obsidia.ps1").read_text(encoding="utf-8")
        assert "3001" in content
        assert "8000" in content
        assert "8011" in content
        assert "5173" in content

    def test_cockpit_does_not_use_8012_as_primary(self):
        content = (SCRIPTS / "obsidia.ps1").read_text(encoding="utf-8")
        # 8012 peut apparaître en commentaire/note, mais pas comme port primaire affecté à une variable active
        # On cherche l'affectation $API = ":8012" — ne doit pas exister
        assert not re.search(r'\$API\s*=\s*["\']http://127\.0\.0\.1:8012["\']', content), (
            "$API ne doit pas pointer sur 8012"
        )

    def test_stack_status_uses_8000(self):
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        assert "8000" in content
        assert "8012" not in content, "stack_status.ps1 ne doit pas référencer 8012"


# =============================================================================
# GROUPE C — KX108_ONLY préservé
# =============================================================================

class TestKX108Authority:
    """Vérifie que les fichiers de lancement maintiennent KX108_ONLY."""

    def test_cockpit_declares_kx108_only(self):
        content = (SCRIPTS / "obsidia.ps1").read_text(encoding="utf-8")
        assert "KX108_ONLY" in content

    def test_obsidia_cli_declares_kx108_only(self):
        content = (SCRIPTS / "obsidia_cli.py").read_text(encoding="utf-8")
        assert "KX108_ONLY" in content

    def test_obsidure_cli_declares_kx108_only(self):
        content = (SCRIPTS / "obsidure_cli.py").read_text(encoding="utf-8")
        assert "KX108_ONLY" in content

    def test_agent_obsidure_boundary_kx108_only(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "KX108_ONLY" in content

    def test_stack_status_declares_kx108_only(self):
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        assert "KX108_ONLY" in content

    def test_obsidia_cli_has_no_apply_flag(self):
        """obsidia_cli.py ne doit pas enregistrer --apply, --commit, --deploy, --act
        comme argument argparse réel (ils peuvent apparaître en commentaire négatif)."""
        content = (SCRIPTS / "obsidia_cli.py").read_text(encoding="utf-8")
        tree = ast.parse(content)
        # Collecte tous les appels add_argument dans le fichier
        registered_flags: list[str] = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
            ):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        registered_flags.append(arg.value)
        for forbidden in ("--apply", "--commit", "--deploy", "--act"):
            assert forbidden not in registered_flags, (
                f"obsidia_cli.py enregistre {forbidden} comme argument argparse "
                f"— le terminal non souverain ne doit pas avoir ce flag"
            )

    def test_obsidia_cli_no_subprocess(self):
        """obsidia_cli.py doit utiliser uniquement la stdlib (pas de subprocess)."""
        content = (SCRIPTS / "obsidia_cli.py").read_text(encoding="utf-8")
        # Vérifie que subprocess n'est pas importé
        assert "import subprocess" not in content, (
            "obsidia_cli.py ne doit pas importer subprocess — AUCUN subprocess"
        )


# =============================================================================
# GROUPE D — Syntaxe Python
# =============================================================================

class TestPythonSyntax:
    """Parse AST pour vérifier la syntaxe des fichiers Python."""

    @pytest.mark.parametrize("relpath", [
        "scripts/obsidure_cli.py",
        "scripts/obsidia_cli.py",
        "periphery/agents/agent_obsidure.py",
    ])
    def test_python_syntax_valid(self, relpath: str):
        path = REPO / relpath
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            pytest.fail(f"Erreur de syntaxe dans {relpath}: {exc}")


# =============================================================================
# GROUPE E — Aucun secret dans le code source
# =============================================================================

class TestNoSecretLeak:
    """Vérifie qu'aucun secret réel n'est dans les fichiers de lancement."""

    SECRET_PATTERNS = [
        r'sk-[A-Za-z0-9]{20,}',           # OpenAI-style key
        r'FIREWORKS_API_KEY\s*=\s*["\'][^"\'$][^"\']{5,}',  # clé réelle (pas de placeholder)
        r'ANTHROPIC_API_KEY\s*=\s*["\'][^"\'$][^"\']{5,}',
        r'ghp_[A-Za-z0-9]{36}',           # GitHub token
        r'bearer [A-Za-z0-9+/]{40,}',     # Bearer token
    ]

    FILES_TO_CHECK = [
        "scripts/obsidia.ps1",
        "scripts/stack_status.ps1",
        "scripts/run_agent_obsidure.ps1",
        "scripts/obsidure_cli.py",
        "scripts/obsidia_cli.py",
        "scripts/OBSIDIA_LAUNCHERS/00_STOP_ALL_SERVERS.ps1",
        "scripts/OBSIDIA_LAUNCHERS/01_START_BRODY_STACK.ps1",
    ]

    @pytest.mark.parametrize("relpath", FILES_TO_CHECK)
    def test_no_secret_in_launcher_file(self, relpath: str):
        path = REPO / relpath
        if not path.is_file():
            pytest.skip(f"Fichier absent : {relpath}")
        content = path.read_text(encoding="utf-8")
        for pattern in self.SECRET_PATTERNS:
            m = re.search(pattern, content, re.IGNORECASE)
            assert m is None, (
                f"Secret potentiel détecté dans {relpath} : pattern={pattern!r} match={m.group()!r}"
            )


# =============================================================================
# GROUPE F — Chemins Windows avec espaces
# =============================================================================

class TestWindowsPathsWithSpaces:
    """Vérifie que les chemins avec espaces sont correctement cités."""

    def test_cockpit_quotes_paths_with_spaces(self):
        content = (SCRIPTS / "obsidia.ps1").read_text(encoding="utf-8")
        # Le chemin contient "obsidia-engine-proof-core" (avec tirets, pas d'espaces)
        # Mais les Start-Process ArgumentList doivent citer $X108 et $SHELL
        # Vérifie que '$X108' ou "'$X108'" apparaît dans les commandes Start-Process
        assert "Start-Process" in content
        # Les chemins passés via -ArgumentList doivent être entre quotes
        assert "\"$X108\"" in content or "'$X108'" in content or "`'$X108`'" in content

    def test_stack_status_path_detection_present(self):
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        # Le script doit utiliser PSScriptRoot pour l'auto-détection
        assert "PSScriptRoot" in content


# =============================================================================
# GROUPE G — UTF-8
# =============================================================================

class TestUtf8:
    """Vérifie que les fichiers peuvent être lus en UTF-8 sans erreur."""

    @pytest.mark.parametrize("relpath", [
        "scripts/obsidia.ps1",
        "scripts/stack_status.ps1",
        "scripts/run_agent_obsidure.ps1",
        "scripts/obsidure_cli.py",
        "scripts/obsidia_cli.py",
        "scripts/run_brody_terminal_enriched.ps1",
    ])
    def test_file_is_valid_utf8(self, relpath: str):
        path = REPO / relpath
        if not path.is_file():
            pytest.skip(f"Fichier absent : {relpath}")
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            pytest.fail(f"Encodage UTF-8 invalide dans {relpath}: {exc}")


# =============================================================================
# GROUPE H — Aucune mutation pendant status/help/doctor
# =============================================================================

class TestNoMutationDuringStatus:
    """
    Vérifie structurellement que les scripts de status/help ne contiennent
    pas de commandes d'écriture (git commit, git push, Set-Content, Out-File
    sur des chemins repo, New-Item dans le repo).
    """

    MUTATION_PATTERNS_PS1 = [
        r'\bgit\s+commit\b',
        r'\bgit\s+push\b',
        r'\bgit\s+add\b',
        r'\bSet-Content\b',
        r'\bOut-File\b',
        r'\bNew-Item\b.*-ItemType\s+File',
        r'\bRemove-Item\b',
    ]

    def test_stack_status_no_mutation(self):
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        for pattern in self.MUTATION_PATTERNS_PS1:
            m = re.search(pattern, content, re.IGNORECASE)
            assert m is None, (
                f"stack_status.ps1 contient une commande de mutation interdite : {m.group()!r}"
            )

    def test_stop_all_servers_no_git_push(self):
        content = (SCRIPTS / "OBSIDIA_LAUNCHERS" / "00_STOP_ALL_SERVERS.ps1").read_text(encoding="utf-8")
        assert not re.search(r'\bgit\s+push\b', content, re.IGNORECASE)
        assert not re.search(r'\bgit\s+commit\b', content, re.IGNORECASE)


# =============================================================================
# GROUPE I — Obsidure importable (dry-run syntaxique)
# =============================================================================

class TestObsidureImportable:
    """Vérifie qu'obsidure_cli.py peut être parsé et que ses dépendances directes sont présentes."""

    def test_obsidure_cli_imports_agent_obsidure(self):
        content = (SCRIPTS / "obsidure_cli.py").read_text(encoding="utf-8")
        assert "agent_obsidure" in content

    def test_agent_obsidure_boundary_dict_present(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "AGENT_OBSIDURE_BOUNDARY" in content

    def test_agent_obsidure_avdr_phases_present(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "phase_a_audit" in content or "AVDRPhase" in content

    def test_agent_obsidure_protected_path_error_present(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "ProtectedPathError" in content

    def test_agent_obsidure_fail_closed_present(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "BackupFailedError" in content or "Fail-Closed" in content.lower() or "fail_closed" in content.lower()


# =============================================================================
# GROUPE J — Kernel protégé
# =============================================================================

class TestKernelProtected:
    """Vérifie que les scripts de lancement ne touchent pas au kernel sealed."""

    KERNEL_FILE = "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs"

    def test_kernel_sealed_present(self):
        assert (REPO / self.KERNEL_FILE).is_file(), (
            f"Kernel sealed absent : {self.KERNEL_FILE}"
        )

    def test_stack_status_does_not_write_kernel(self):
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        assert "server.kernel.sealed" not in content or (
            "Set-Content" not in content and "Out-File" not in content
        ), "stack_status.ps1 ne doit pas écrire dans le kernel sealed"

    def test_agent_obsidure_protects_kernel(self):
        content = (PERIPHERY / "agents" / "agent_obsidure.py").read_text(encoding="utf-8")
        assert "server.kernel.sealed.cjs" in content, (
            "agent_obsidure.py doit explicitement nommer le kernel sealed comme path protégé"
        )


# =============================================================================
# GROUPE K — Compatibilité Windows PowerShell 5.1 (parsing réel)
# =============================================================================

class TestPowerShell51Parsing:
    """
    Parse les scripts PS1 via powershell.exe (PS 5.1) et vérifie 0 erreur.
    Utilise EXCLUSIVEMENT powershell.exe (pas pwsh) conformément au mandat.
    Ces tests sont skippés si powershell.exe n'est pas trouvé dans le PATH.
    """

    PS_SCRIPTS = [
        "scripts/stack_status.ps1",
        "scripts/obsidia.ps1",
        "scripts/run_brody_terminal_enriched.ps1",
        "scripts/run_agent_obsidure.ps1",
        "scripts/OBSIDIA_LAUNCHERS/00_STOP_ALL_SERVERS.ps1",
        "scripts/OBSIDIA_LAUNCHERS/01_START_BRODY_STACK.ps1",
        "scripts/OBSIDIA_LAUNCHERS/02_START_KERNEL_AND_DOMAINS.ps1",
    ]

    @classmethod
    def _find_powershell_exe(cls) -> str | None:
        import shutil
        return shutil.which("powershell.exe")

    @pytest.mark.parametrize("relpath", PS_SCRIPTS)
    def test_ps1_parses_under_ps51(self, relpath: str):
        """Vérifie 0 erreur de parsing PS 5.1 pour chaque script."""
        ps_exe = self._find_powershell_exe()
        if not ps_exe:
            pytest.skip("powershell.exe introuvable dans le PATH")

        script_path = str(REPO / relpath).replace("/", "\\")
        ps_cmd = (
            f"$errs=$null; "
            f"$null=[System.Management.Automation.Language.Parser]::"
            f"ParseFile('{script_path}',[ref]$null,[ref]$errs); "
            f"if($errs.Count -gt 0){{$errs|ForEach-Object{{Write-Host $_.Message}}; exit 1}} "
            f"else{{exit 0}}"
        )
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, (
            f"PS 5.1 parse errors in {relpath}:\n{result.stdout}\n{result.stderr}"
        )

    def test_stack_status_executes_quiet_without_error(self):
        """stack_status.ps1 -Quiet s'exécute sans erreur sous PS 5.1."""
        ps_exe = self._find_powershell_exe()
        if not ps_exe:
            pytest.skip("powershell.exe introuvable dans le PATH")

        script_path = str(SCRIPTS / "stack_status.ps1")
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", script_path, "-Quiet"],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, (
            f"stack_status.ps1 -Quiet a échoué:\n{result.stdout}\n{result.stderr}"
        )
        # Doit contenir au moins un composant lisible
        assert "KERNEL_RAGNAROK" in result.stdout or "TERMINAL_CLI" in result.stdout

    def test_stack_status_json_output_is_parsable(self):
        """stack_status.ps1 -Json produit du JSON parsable par Python."""
        import json
        ps_exe = self._find_powershell_exe()
        if not ps_exe:
            pytest.skip("powershell.exe introuvable dans le PATH")

        script_path = str(SCRIPTS / "stack_status.ps1")
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", script_path, "-Json"],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"stack_status.ps1 -Json a échoué:\n{result.stderr}"
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Sortie JSON non parsable : {exc}\nSortie: {result.stdout[:500]}")
        assert isinstance(data, list), "La sortie JSON doit être une liste de composants"
        assert len(data) >= 11, f"Attendu >= 11 composants, obtenu {len(data)}"
        names = {c.get("name") for c in data if isinstance(c, dict)}
        for required in ("KERNEL_RAGNAROK", "API_OBSIDIA_BRODY", "NEO4J_BROWSER",
                         "NEO4J_INSTANCE", "AGENT_OBSIDURE", "TERMINAL_CLI"):
            assert required in names, f"Composant requis absent du JSON: {required}"

    def test_stack_status_has_no_em_dash_in_string_literals(self):
        """stack_status.ps1 ne doit pas contenir d'em-dash (U+2014) dans les chaînes."""
        content = (SCRIPTS / "stack_status.ps1").read_text(encoding="utf-8")
        # L'em-dash est le bug root-cause PS 5.1
        assert "—" not in content, (
            "stack_status.ps1 contient un em-dash U+2014 — incompatible PS 5.1 sans BOM"
        )

    def test_launcher_scripts_have_no_em_dash_in_string_literals(self):
        """Les launchers ne doivent plus contenir d'em-dash dans des litéraux de chaîne."""
        launchers = [
            "scripts/OBSIDIA_LAUNCHERS/00_STOP_ALL_SERVERS.ps1",
            "scripts/OBSIDIA_LAUNCHERS/01_START_BRODY_STACK.ps1",
            "scripts/OBSIDIA_LAUNCHERS/02_START_KERNEL_AND_DOMAINS.ps1",
        ]
        for relpath in launchers:
            path = REPO / relpath
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            # Recherche d'em-dash dans des lignes qui ne sont pas des commentaires
            for lineno, line in enumerate(content.splitlines(), 1):
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue  # commentaire, pas un problème
                assert "—" not in line, (
                    f"Em-dash U+2014 trouvé dans une ligne de code (non-commentaire) "
                    f"dans {relpath}:{lineno}: {line!r}"
                )
