"""test_check_forbidden_content — vérifications comportementales de scripts/check_forbidden_content.py.

Quatre propriétés garanties simultanément :
  1. brody_secret_scrubber.py (utilitaire de sanitisation) ne déclenche plus de faux positif.
  2. Un vrai fichier de credential (api_credential.json) est bien bloqué.
  3. Une URL ou chaîne avec un secret incorporé est détectée par brody_secret_scrubber.
  4. PEM, mot de passe, token : détectés par brody_secret_scrubber.detect_secret_like.

DECISION_AUTHORITY=KX108_ONLY. No IO. No network. No ACT.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_forbidden_content.py"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run_script(cwd: Path) -> tuple[int, str]:
    """Run check_forbidden_content.py from cwd; return (returncode, stdout)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def _make_tree(tmp_path: Path, files: dict[str, str]) -> Path:
    """Create files relative to tmp_path; return tmp_path."""
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp_path


# ── Propriété 1 — brody_secret_scrubber.py ne doit PAS déclencher de faux positif ──

def test_brody_secret_scrubber_not_flagged(tmp_path: Path) -> None:
    """P1 — brody_secret_scrubber.py est dans ALLOWED_PATH_FRAGMENTS → PASS."""
    _make_tree(tmp_path, {
        "apps/obsidia_api/brody_secret_scrubber.py": "# sanitisation utility — no credential\n",
        "scripts/check_forbidden_content.py": SCRIPT.read_text(encoding="utf-8"),
        # minimal extras to avoid false positives from an empty tree
        "sigma/__init__.py": "",
    })
    code, out = _run_script(tmp_path)
    assert code == 0, f"Faux positif détecté pour brody_secret_scrubber.py : {out}"
    assert "FORBIDDEN_CONTENT_PASS" in out


# ── Propriété 2 — un vrai fichier de credential est bloqué ────────────────────

def test_real_credential_file_flagged(tmp_path: Path) -> None:
    """P2 — un fichier nommé api_credential.json hors whitelist déclenche une violation."""
    _make_tree(tmp_path, {
        "configs/api_credential.json": '{"key": "fake"}',
        "scripts/check_forbidden_content.py": SCRIPT.read_text(encoding="utf-8"),
    })
    code, out = _run_script(tmp_path)
    assert code == 1, f"Un fichier de credential n'a pas été détecté : {out}"
    assert "SUSPICIOUS_FILE" in out or "FORBIDDEN" in out


def test_private_key_filename_flagged(tmp_path: Path) -> None:
    """P2b — un fichier nommé *private_key* hors whitelist est bloqué."""
    _make_tree(tmp_path, {
        "secrets/my_private_key.pem": "---- BEGIN PRIVATE KEY ----",
        "scripts/check_forbidden_content.py": SCRIPT.read_text(encoding="utf-8"),
    })
    code, out = _run_script(tmp_path)
    assert code == 1, f"Fichier private_key non détecté : {out}"


# ── Propriété 3 — URL / chaîne avec secret incorporé → brody_secret_scrubber détecte ──

def test_secret_scrubber_detects_url_with_api_key() -> None:
    """P3 — detect_secret_like détecte API_KEY=abc123 dans une URL."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("https://example.com/api?API_KEY=abc123SECRET") is True


def test_secret_scrubber_detects_bearer_token() -> None:
    """P3b — Bearer token est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("Authorization: Bearer abcdefghij1234567890") is True


def test_secret_scrubber_clean_text_returns_false() -> None:
    """P3c — texte sans secret : detect_secret_like retourne False."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("Bonjour, ceci est un message normal sans credential.") is False


# ── Propriété 4 — PEM, mot de passe, token restent détectés ───────────────────

def test_secret_scrubber_detects_pem_header() -> None:
    """P4a — header PEM BEGIN PRIVATE KEY est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("-----BEGIN PRIVATE KEY-----\nMIIEvQIBADA") is True


def test_secret_scrubber_detects_rsa_pem_header() -> None:
    """P4b — header RSA PRIVATE KEY est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("-----BEGIN RSA PRIVATE KEY-----") is True


def test_secret_scrubber_detects_password() -> None:
    """P4c — PASSWORD=value est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("PASSWORD=mysecretpass123") is True


def test_secret_scrubber_detects_github_pat() -> None:
    """P4d — GitHub PAT ghp_ est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("ghp_" + "A" * 36) is True


def test_secret_scrubber_detects_sk_key() -> None:
    """P4e — sk- token (ex: OpenAI key) est détecté."""
    from apps.obsidia_api.brody_secret_scrubber import detect_secret_like
    assert detect_secret_like("sk-" + "A" * 25) is True


def test_secret_scrubber_scrubs_password() -> None:
    """P4f — scrub_secret_like masque PASSWORD=value correctement."""
    from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like
    result = scrub_secret_like("PASSWORD=mysecretpass123")
    assert "[REDACTED_SECRET]" in result
    assert "mysecretpass123" not in result
