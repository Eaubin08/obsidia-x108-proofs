"""
Tests for brody_secret_scrubber — V3 Block 3F repair.
PATCH=YES_SECRET_REPAIR_ONLY. COMMIT=NO. DECISION_AUTHORITY=KX108_ONLY.
"""
import pytest
from apps.obsidia_api.brody_secret_scrubber import (
    detect_secret_like,
    scrub_secret_like,
    secret_flags,
    is_private_key_message,
)


# ── detect_secret_like ────────────────────────────────────────────────────────

def test_detect_api_key():
    """T1 — API_KEY brut est détecté."""
    assert detect_secret_like("Mémorise API_KEY=abc123SECRET.") is True


def test_detect_password():
    """T2 — PASSWORD brut est détecté."""
    assert detect_secret_like("Ajoute PASSWORD=supersecret à la mémoire.") is True


def test_detect_bearer():
    """T3 — Bearer token brut est détecté."""
    assert detect_secret_like("Sauvegarde Bearer abc.def.ghi.") is True


def test_detect_private_key():
    """T4 — PRIVATE KEY header brut est détecté."""
    assert detect_secret_like("-----BEGIN PRIVATE KEY----- test") is True


def test_detect_sk_key():
    """T5 — sk- token brut est détecté."""
    assert detect_secret_like("Stocke ce token: sk-test-ABCDEFGHIJKLMNOPQRSTU.") is True


def test_detect_ghp_token():
    """T6 — ghp_ token brut est détecté."""
    assert detect_secret_like("Token: ghp_" + "A" * 36) is True


def test_detect_clean_text():
    """T7 — texte propre n'est pas détecté comme secret."""
    assert detect_secret_like("Quelle est la politique de taux d'intérêt?") is False


def test_detect_empty():
    """T8 — texte vide ne lève pas d'erreur."""
    assert detect_secret_like("") is False
    assert detect_secret_like(None) is False  # type: ignore[arg-type]


# ── scrub_secret_like ─────────────────────────────────────────────────────────

def test_scrub_api_key():
    """T9 — scrub remplace la valeur API_KEY par [REDACTED_SECRET]."""
    result = scrub_secret_like("API_KEY=abc123SECRET")
    assert "abc123SECRET" not in result
    assert "[REDACTED_SECRET]" in result
    assert "API_KEY" in result


def test_scrub_password():
    """T10 — scrub remplace PASSWORD=supersecret."""
    result = scrub_secret_like("Ajoute PASSWORD=supersecret à la mémoire.")
    assert "supersecret" not in result
    assert "[REDACTED_SECRET]" in result


def test_scrub_bearer():
    """T11 — scrub remplace Bearer abc.def.ghi."""
    result = scrub_secret_like("Sauvegarde Bearer abc.def.ghi.")
    assert "abc.def.ghi" not in result
    assert "[REDACTED_SECRET]" in result


def test_scrub_private_key():
    """T12 — scrub remplace -----BEGIN PRIVATE KEY-----."""
    text = "Garde cette clé: -----BEGIN PRIVATE KEY----- test"
    result = scrub_secret_like(text)
    assert "BEGIN PRIVATE KEY-----" not in result or "[REDACTED_SECRET]" in result


def test_scrub_no_double_redaction():
    """T13 — texte déjà redacté n'est pas double-redacté."""
    already = "API_KEY=[REDACTED_SECRET]"
    result = scrub_secret_like(already)
    assert result.count("[REDACTED_SECRET]") == 1


def test_scrub_clean_text_unchanged():
    """T14 — texte propre sort intact."""
    text = "Quelle est la politique de taux d'intérêt?"
    assert scrub_secret_like(text) == text


def test_scrub_empty():
    """T15 — texte vide ne lève pas d'erreur."""
    assert scrub_secret_like("") == ""
    assert scrub_secret_like(None) is None  # type: ignore[arg-type]


# ── secret_flags ─────────────────────────────────────────────────────────────

def test_flags_api_key():
    """T16 — secret_flags détecte api_key."""
    flags = secret_flags("API_KEY=abc123SECRET")
    assert flags["api_key"] is True


def test_flags_bearer():
    """T17 — secret_flags détecte bearer."""
    flags = secret_flags("Bearer abc.def.ghi longtoken")
    assert flags["bearer"] is True


def test_flags_clean():
    """T18 — secret_flags retourne tout False sur texte propre."""
    flags = secret_flags("quel est le taux d'intérêt?")
    assert all(v is False for v in flags.values())


# ── is_private_key_message ────────────────────────────────────────────────────

def test_private_key_detected():
    """T19 — is_private_key_message retourne True sur BEGIN PRIVATE KEY."""
    assert is_private_key_message("-----BEGIN PRIVATE KEY----- test") is True


def test_private_key_rsa_detected():
    """T20 — is_private_key_message retourne True sur BEGIN RSA PRIVATE KEY."""
    assert is_private_key_message("-----BEGIN RSA PRIVATE KEY-----") is True


def test_private_key_clean():
    """T21 — is_private_key_message retourne False sur texte propre."""
    assert is_private_key_message("Quelle est la politique de taux?") is False


def test_private_key_none():
    """T22 — is_private_key_message ne lève pas d'erreur sur None."""
    assert is_private_key_message(None) is False  # type: ignore[arg-type]
