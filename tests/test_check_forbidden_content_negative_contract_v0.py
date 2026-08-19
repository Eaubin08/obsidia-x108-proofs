"""
tests/test_check_forbidden_content_negative_contract_v0.py
=============================================================
Régression de sécurité PERMANENTE pour scripts/check_forbidden_content.py.

Contexte (PREPARE_ACD01_EXECUTION_TEST_CONTRACT_V0) : ACD-01 ajoute une
exception d'allowlist à ce scanner. Cette exception doit rester bornée
au fichier légitime — elle ne doit JAMAIS rendre le scanner globalement
permissif. Ce test PASSE déjà à HEAD, AVANT toute application d'ACD-01 :
il prouve une propriété de sécurité qu'ACD-01 doit PRÉSERVER, pas créer.

Le test invoque le VRAI script de production (sous-processus, argv réel,
aucune réimplémentation des règles de correspondance) contre un
répertoire temporaire isolé contenant un nom de fichier authentiquement
suspect et non-allowlisté. Le dépôt réel n'est jamais modifié.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCANNER = _REPO_ROOT / "scripts" / "check_forbidden_content.py"


def _run_scanner_against(cwd: Path) -> "tuple[int, str]":
    """Invoque le VRAI scripts/check_forbidden_content.py — argv réel, pas de shell=True."""
    result = subprocess.run(
        [sys.executable, str(_SCANNER)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


class TestNegativeSecurityRegression:
    def test_genuine_suspicious_credential_path_still_rejected(self, tmp_path):
        """
        NEGATIVE_PROBE_SUSPICIOUS_PATH — un chemin non-allowlisté
        contenant un motif de nom suspect (ici "credential", reconnu
        explicitement par le scanner de production) doit être détecté :
        exit != 0 + preuve SUSPICIOUS_FILE.
        """
        target = tmp_path / "configs" / "api_credential.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"key": "not_a_real_secret"}', encoding="utf-8")

        code, output = _run_scanner_against(tmp_path)
        assert code != 0
        assert "SUSPICIOUS_FILE" in output
        assert "api_credential.json" in output

    def test_genuine_private_key_filename_still_rejected(self, tmp_path):
        """Un fichier nommé *private_key* hors allowlist reste bloqué."""
        target = tmp_path / "secrets" / "my_private_key.pem"
        target.parent.mkdir(parents=True)
        target.write_text("---- BEGIN PRIVATE KEY ----", encoding="utf-8")

        code, output = _run_scanner_against(tmp_path)
        assert code != 0
        assert "SUSPICIOUS_FILE" in output

    def test_clean_tree_passes(self, tmp_path):
        """Contrôle positif : un arbre sans fichier suspect passe (exit 0)."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("print('hello')\n", encoding="utf-8")

        code, output = _run_scanner_against(tmp_path)
        assert code == 0
        assert "FORBIDDEN_CONTENT_PASS" in output

    def test_allowlisted_scrubber_style_path_not_flagged_but_others_still_are(self, tmp_path):
        """
        Preuve que l'exception ACD-01 (quand elle sera appliquée) reste
        BORNÉE : ce test isolé, tel qu'il tourne aujourd'hui (avant
        ACD-01), confirme qu'un fichier "secret"-nommé HORS de l'entrée
        d'allowlist exacte d'ACD-01 (apps/obsidia_api/brody_secret_scrubber.py)
        est toujours rejeté — la portée de l'exception ne s'étend pas.
        """
        target = tmp_path / "apps" / "obsidia_api" / "totally_different_secret_handler.py"
        target.parent.mkdir(parents=True)
        target.write_text("# not the scrubber\n", encoding="utf-8")

        code, output = _run_scanner_against(tmp_path)
        assert code != 0
        assert "SUSPICIOUS_FILE" in output
