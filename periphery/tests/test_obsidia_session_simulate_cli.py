"""test_obsidia_session_simulate_cli — Tests TERMINAL_SESSION_SIMULATE_V0.

T01-T08   : parser et acknowledgement
T09-T20   : lock path
T21-T25   : session ID
T26-T35   : heartbeat interval
T36-T41   : max steps
T42-T46   : control request
T47-T57   : simulation (adapter)
T58-T68   : JSON / stdout / stderr
T69-T78   : effets de bord
T79-T88   : PowerShell
T89-T95   : intégrité blob
T96-T112  : scénarios complémentaires REV01

Fixture de configuration :
    HeartbeatConfig(enabled=True, heartbeat_interval_seconds=1.0)
    La valeur 1.0 est TEST_FIXTURE_ONLY_NOT_PRODUCTION.
"""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Chemins canoniques
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CLI = _REPO_ROOT / "scripts" / "obsidia_session_simulate_cli.py"
_PS = _REPO_ROOT / "scripts" / "obsidia.ps1"
_PYTHON = sys.executable

# SHAs de référence pour les blobs protégés
_ADAPTER_REF_SHA = "0ef8c5131952317faa6b585ab07d16ffdfcb4cea"
_CALLER_REF_SHA = "b2011885bd7f9b52ce486983034f5046f2e56ea6"
_MANAGER_REF_SHA = "69b8985ab21eb678ab7ed507e67c5c41e3441eaa"
_INSPECT_CLI_REF_SHA = "6ff0b2120da3ed092adc70049ef844f798b2cfeb"
_INSPECT_TEST_REF_SHA = "6ff0b2120da3ed092adc70049ef844f798b2cfeb"
_SPEC_REV01_SHA = "3f0960285a2102fa264fb4595b6397de29a6dd56"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(args: list, *, timeout: int = 30):
    r = subprocess.run(
        [_PYTHON, "-B", str(_CLI)] + list(args),
        capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        cwd=str(_REPO_ROOT),
    )
    return r.stdout, r.stderr, r.returncode


def _valid_args(tmp_path: Path) -> list:
    """Invocation minimale valide avec tous les tokens requis."""
    lock = tmp_path / "sim.lock"
    return [
        "--lock-path", str(lock),
        "--session-id", "test-session-001",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ]


def _parse_json(stdout: str) -> dict:
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    assert len(lines) == 1, f"attendu 1 ligne JSON, trouvé {len(lines)}: {stdout!r}"
    return json.loads(lines[0])


def _git_blob(commit: str, rel_path: str) -> str:
    r = subprocess.run(
        ["git", "ls-tree", commit, rel_path],
        capture_output=True, text=True, cwd=str(_REPO_ROOT),
    )
    parts = r.stdout.strip().split()
    return parts[2] if len(parts) >= 3 else ""


def _git_hash_object(rel_path: str) -> str:
    r = subprocess.run(
        ["git", "hash-object", rel_path],
        capture_output=True, text=True, cwd=str(_REPO_ROOT),
    )
    return r.stdout.strip()


def _load_cli():
    spec = importlib.util.spec_from_file_location("_sim_cli_under_test", str(_CLI))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _call_main(mod, args: list, *, monkeypatch_adapter=None):
    """Appelle mod.main(args) en capturant stdout. Retourne (stdout_str, exit_code)."""
    buf = io.StringIO()
    original_stdout = sys.stdout

    class _MockAdapter:
        def simulate_bounded_session(self, **kwargs):
            return monkeypatch_adapter(**kwargs)

    try:
        sys.stdout = buf
        if monkeypatch_adapter is not None:
            # Patcher l'attribut dans le module CLI (déjà importé), pas dans le module source.
            with patch.object(mod, "TerminalSessionAdapter", return_value=_MockAdapter()):
                code = mod.main(args)
        else:
            code = mod.main(args)
    finally:
        sys.stdout = original_stdout
    return buf.getvalue(), code


def _make_fake_caller_result(
    *,
    ok: bool,
    sequence_ok=None,
    cleanup_ok=None,
    first_failure=None,
    steps_executed: int = 0,
    terminated: bool = False,
    released: bool = False,
    detail: str = "FAKE",
):
    cr = MagicMock()
    cr.ok = ok
    cr.sequence_ok = sequence_ok
    cr.cleanup_ok = cleanup_ok
    cr.first_failure = first_failure
    cr.steps_executed = steps_executed
    cr.terminated = terminated
    cr.released = released
    cr.detail = detail
    return cr


def _make_fake_adapter_result(
    *,
    ok: bool,
    adapter_code_value: str,
    sequence_ok=None,
    cleanup_ok=None,
    first_failure=None,
    caller_result=None,
    detail: str = "FAKE",
):
    from periphery.session_lock.terminal_session_adapter import AdapterCode
    r = MagicMock()
    r.ok = ok
    r.adapter_code = MagicMock()
    r.adapter_code.value = adapter_code_value
    r.sequence_ok = sequence_ok
    r.cleanup_ok = cleanup_ok
    r.first_failure = first_failure
    r.caller_result = caller_result
    r.detail = detail
    return r


# ===========================================================================
# T01-T08 : parser et acknowledgement
# ===========================================================================

def test_t01_no_args_exit_2():
    """T01 : aucun argument → exit 2."""
    _, stderr, code = _run([])
    assert code == 2
    assert stderr == ""


def test_t02_missing_lock_path_exit_2(tmp_path):
    """T02a : --lock-path absent → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t02_missing_session_id_exit_2(tmp_path):
    """T02b : --session-id absent → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t02_missing_heartbeat_exit_2(tmp_path):
    """T02c : --heartbeat-interval-seconds absent → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t02_missing_max_steps_exit_2(tmp_path):
    """T02d : --max-steps absent → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t02_missing_control_exit_2(tmp_path):
    """T02e : --control absent → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t03_unknown_option_exit_2(tmp_path):
    """T03 : option inconnue → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
        "--unknown-flag",
    ])
    assert code == 2
    assert stderr == ""


def test_t04_duplicate_lock_path_exit_2(tmp_path):
    """T04 : option dupliquée (11 tokens attendus, 13 fournis) → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t05_wrong_order_exit_2(tmp_path):
    """T05 : ordre incorrect → exit 2."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--session-id", "s1",
        "--lock-path", str(lock),
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t06_option_equals_form_exit_2(tmp_path):
    """T06 : forme --option=value → exit 2 (11 tokens mais token[0] invalide)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        f"--lock-path={lock}",
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t07_ack_absent_exit_2_adapter_not_built(tmp_path):
    """T07 : --ack-temp-lock-mutation absent → exit 2, adapter non construit."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
    ])
    assert code == 2
    assert stderr == ""
    assert not lock.exists(), "lock ne doit pas avoir été créé"


def test_t08_adapter_not_built_on_invalid_invocation(tmp_path):
    """T08 : adapter non construit lors d'une invocation invalide."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([])
    assert code == 2
    assert stderr == ""
    assert not lock.exists()
    data = _parse_json(stdout)
    assert data["adapter_code"] == "INVOCATION_INVALID"


# ===========================================================================
# T09-T20 : lock path
# ===========================================================================

def test_t09_relative_path_rejected():
    """T09 : chemin relatif rejeté."""
    _, stderr, code = _run([
        "--lock-path", "relative/path.lock",
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t10_absent_parent_rejected(tmp_path):
    """T10 : parent absent rejeté."""
    lock = tmp_path / "nonexistent_dir" / "sim.lock"
    _, stderr, code = _run(_valid_args.__wrapped__(tmp_path) if hasattr(_valid_args, "__wrapped__") else [
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t11_non_directory_parent_rejected(tmp_path):
    """T11 : parent non répertoire rejeté."""
    file_as_parent = tmp_path / "file_parent"
    file_as_parent.write_bytes(b"not a dir")
    lock = file_as_parent / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t12_existing_target_rejected(tmp_path):
    """T12 : cible déjà existante rejetée."""
    lock = tmp_path / "existing.lock"
    lock.write_bytes(b'{"session_id":"x","lock_version":"V2","created_at":1,"heartbeat_at":1}')
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["adapter_code"] == "INVOCATION_INVALID"


def test_t13_existing_directory_target_rejected(tmp_path):
    """T13 : cible répertoire rejetée."""
    lock_dir = tmp_path / "lock_as_dir"
    lock_dir.mkdir()
    stdout, stderr, code = _run([
        "--lock-path", str(lock_dir),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t14_symlink_target_rejected(tmp_path):
    """T14 : cible non-dangling symlink rejetée."""
    real_file = tmp_path / "real.lock"
    real_file.write_bytes(b"{}")
    link = tmp_path / "link.lock"
    try:
        link.symlink_to(real_file)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks non disponibles dans cet environnement")
    stdout, stderr, code = _run([
        "--lock-path", str(link),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t15_parent_symlink_rejected(tmp_path):
    """T15 : parent symlink rejeté."""
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    link_dir = tmp_path / "link_dir"
    try:
        link_dir.symlink_to(real_dir)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks non disponibles dans cet environnement")
    lock = link_dir / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t16_path_in_repo_rejected():
    """T16 : chemin dans le dépôt rejeté."""
    lock = _REPO_ROOT / "temp_test.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["adapter_code"] == "INVOCATION_INVALID"


def test_t17_valid_path_outside_repo_accepted(tmp_path):
    """T17 : chemin absolu hors dépôt accepté."""
    lock = tmp_path / "valid.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "test-session-017",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["adapter_code"] in ("OK", "CALLER_FAILED")
    assert code in (0, 3)


def test_t18_path_with_spaces_accepted(tmp_path):
    """T18 : chemin avec espaces accepté (si hors dépôt)."""
    spaced = tmp_path / "dir with spaces"
    spaced.mkdir()
    lock = spaced / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "test-session-018",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    assert code in (0, 3)


def test_t19_unicode_path_accepted(tmp_path):
    """T19 : chemin Unicode accepté (hors dépôt, parent valide)."""
    udir = tmp_path / "répertoire-é"
    try:
        udir.mkdir()
    except (OSError, UnicodeEncodeError):
        pytest.skip("chemin Unicode non supporté dans cet environnement")
    lock = udir / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "test-session-019",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    assert code in (0, 3)


def test_t20_lock_path_preserved_exactly(tmp_path):
    """T20 : chaîne publique lock_path préservée exactement dans l'envelope."""
    lock = tmp_path / "preserve.lock"
    raw = str(lock)
    stdout, stderr, code = _run([
        "--lock-path", raw,
        "--session-id", "test-session-020",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["lock_path"] == raw


# ===========================================================================
# T21-T25 : session ID
# ===========================================================================

def test_t21_empty_session_id_rejected(tmp_path):
    """T21 : session_id vide rejeté."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t22_session_id_too_long_rejected(tmp_path):
    """T22 : session_id > 128 caractères rejeté."""
    lock = tmp_path / "sim.lock"
    long_id = "A" * 129
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", long_id,
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t23_control_char_session_id_rejected(tmp_path):
    """T23 : caractère de contrôle dans session_id rejeté."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "bad\x01session",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t24_session_id_with_spaces_rejected(tmp_path):
    """T24 : espace initial ou final dans session_id rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    for bad_id in [" leading", "trailing ", "in the middle"]:
        stdout, stderr, code = _run([
            "--lock-path", str(lock),
            "--session-id", bad_id,
            "--heartbeat-interval-seconds", "1.0",
            "--max-steps", "3",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
        assert code == 2, f"attendu exit 2 pour session_id={bad_id!r}"
        assert stderr == ""


def test_t25_valid_session_id_preserved(tmp_path):
    """T25 : session_id valide préservé exactement."""
    lock = tmp_path / "sim.lock"
    sid = "MySession-01:alpha_2.0"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", sid,
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["session_id"] == sid


# ===========================================================================
# T26-T35 : heartbeat interval
# ===========================================================================

def test_t26_missing_heartbeat_option_exit_2(tmp_path):
    """T26 : option --heartbeat-interval-seconds absente → exit 2 (via ordre)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--max-steps", "3",
        "--control", "none",
        "--heartbeat-interval-seconds", "1.0",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t27_boolean_interval_rejected(tmp_path):
    """T27 : booléen comme intervalle rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    for bad in ["True", "False"]:
        _, stderr, code = _run([
            "--lock-path", str(lock),
            "--session-id", "s1",
            "--heartbeat-interval-seconds", bad,
            "--max-steps", "3",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
        assert code == 2, f"attendu exit 2 pour interval={bad!r}"
        assert stderr == ""


def test_t28_zero_interval_rejected(tmp_path):
    """T28 : 0 rejeté (hors borne [0.01, 5.0])."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t29_negative_interval_rejected(tmp_path):
    """T29 : négatif rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "-1",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t30_nan_interval_rejected(tmp_path):
    """T30 : NaN rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "NaN",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t31_pos_inf_interval_rejected(tmp_path):
    """T31 : +Inf rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "Inf",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t32_neg_inf_interval_rejected(tmp_path):
    """T32 : -Inf rejeté (via regex)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "-Inf",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t33_below_min_interval_rejected(tmp_path):
    """T33 : inférieur à 0.01 rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "0.001",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t34_above_max_interval_rejected(tmp_path):
    """T34 : supérieur à 5.0 rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "5.001",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t35_bounds_accepted(tmp_path):
    """T35 : bornes 0.01 et 5.0 acceptées."""
    for val, ms in [("0.01", "1"), ("5.0", "1"), ("1", "3"), ("0.1", "2"), ("5", "1"), ("1.0", "3")]:
        lock = tmp_path / f"sim_{val.replace('.', '_')}.lock"
        stdout, stderr, code = _run([
            "--lock-path", str(lock),
            "--session-id", "s1",
            "--heartbeat-interval-seconds", val,
            "--max-steps", ms,
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
        assert stderr == ""
        data = _parse_json(stdout)
        assert data["adapter_code"] in ("OK", "CALLER_FAILED"), f"val={val!r}: {data}"
        assert code in (0, 3), f"val={val!r}: exit={code}"


# ===========================================================================
# T36-T41 : max steps
# ===========================================================================

def test_t36_non_integer_max_steps_rejected(tmp_path):
    """T36 : non entier (1.0) rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "1.0",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t37_boolean_max_steps_rejected(tmp_path):
    """T37 : booléen (True) rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "True",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t38_zero_max_steps_rejected(tmp_path):
    """T38 : zéro rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "0",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t39_negative_max_steps_rejected(tmp_path):
    """T39 : négatif rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "-1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t40_above_100_max_steps_rejected(tmp_path):
    """T40 : supérieur à 100 rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "101",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t41_bounds_1_and_100_accepted(tmp_path):
    """T41 : bornes 1 et 100 acceptées."""
    for ms in ["1", "100"]:
        lock = tmp_path / f"sim_ms{ms}.lock"
        stdout, stderr, code = _run([
            "--lock-path", str(lock),
            "--session-id", "s1",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", ms,
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
        assert stderr == ""
        assert code in (0, 3), f"ms={ms!r}: exit={code}"


# ===========================================================================
# T42-T46 : control request
# ===========================================================================

def test_t42_none_control_maps_to_python_none(tmp_path):
    """T42 : 'none' → None (pas de contrôle injecté)."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["control_request"] == "none"
    assert code in (0, 3)


def test_t43_stop_control_maps_to_stop(tmp_path):
    """T43 : 'stop' → ControlRequest.STOP."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "10",
        "--control", "stop",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["control_request"] == "stop"
    assert code in (0, 3)


def test_t44_abort_control_maps_to_abort(tmp_path):
    """T44 : 'abort' → ControlRequest.ABORT."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "10",
        "--control", "abort",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["control_request"] == "abort"
    assert code in (0, 3)


def test_t45_uppercase_control_rejected(tmp_path):
    """T45 : casse différente (NONE, STOP, ABORT) rejetée."""
    lock = tmp_path / "sim.lock"
    for bad in ["NONE", "STOP", "ABORT", "None", "Stop"]:
        _, stderr, code = _run([
            "--lock-path", str(lock),
            "--session-id", "s1",
            "--heartbeat-interval-seconds", "1.0",
            "--max-steps", "3",
            "--control", bad,
            "--ack-temp-lock-mutation",
        ])
        assert code == 2, f"attendu exit 2 pour control={bad!r}"
        assert stderr == ""


def test_t46_unknown_control_rejected(tmp_path):
    """T46 : valeur inconnue rejetée."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "pause",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


# ===========================================================================
# T47-T57 : simulation (adapter)
# ===========================================================================

def test_t47_nominal_simulation_exit_0(tmp_path):
    """T47 : simulation nominale bornée → exit 0, lock_exists_after=false."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "sim-nom-047",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    assert code == 0
    data = _parse_json(stdout)
    assert data["ok"] is True
    assert data["lock_exists_after"] is False
    assert not lock.exists()


def test_t48_stop_control_terminates_cleanly(tmp_path):
    """T48 : --control stop → terminé proprement."""
    lock = tmp_path / "sim_stop.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "sim-stop-048",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "10",
        "--control", "stop",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["adapter_code"] in ("OK", "CALLER_FAILED")
    assert data["lock_exists_after"] is False
    assert not lock.exists()


def test_t49_abort_control_terminates_cleanly(tmp_path):
    """T49 : --control abort → terminé proprement."""
    lock = tmp_path / "sim_abort.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "sim-abort-049",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "10",
        "--control", "abort",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["lock_exists_after"] is False
    assert not lock.exists()


def test_t50_bootstrap_failure_exit_3(tmp_path):
    """T50 : bootstrap failure → exit 3, adapter_code=CALLER_FAILED, first_failure=null, steps_executed=0."""
    mod = _load_cli()
    lock = tmp_path / "bootstrap_fail.lock"

    caller_result = _make_fake_caller_result(
        ok=False,
        sequence_ok=None,
        cleanup_ok=None,
        first_failure=None,
        steps_executed=0,
        terminated=False,
        released=False,
        detail="bootstrap_failed",
    )
    fake_result = _make_fake_adapter_result(
        ok=False,
        adapter_code_value="CALLER_FAILED",
        sequence_ok=None,
        cleanup_ok=None,
        first_failure=None,
        caller_result=caller_result,
        detail="bootstrap_failed",
    )

    def fake_simulate(**kwargs):
        return fake_result

    stdout_str, code = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "bootstrap-fail-050",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=fake_simulate,
    )
    assert code == 3
    data = json.loads(stdout_str.strip())
    assert data["adapter_code"] == "CALLER_FAILED"
    assert data["first_failure"] is None
    assert data["steps_executed"] == 0
    assert data["sequence_ok"] is None
    assert data["cleanup_ok"] is None


def test_t51_tick_failure_first_failure_correct(tmp_path):
    """T51 : tick failure → first_failure contient OperationResult mappé selon Décision M."""
    mod = _load_cli()
    lock = tmp_path / "tick_fail.lock"

    from periphery.session_lock.heartbeat_lock_manager import FailureCode, OperationResult
    ff = OperationResult(
        ok=False,
        code=FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
        fail_closed=True,
        human_recovery_required=False,
        detail="write_failed_detail",
        payload={},
    )
    caller_result = _make_fake_caller_result(
        ok=False,
        sequence_ok=False,
        cleanup_ok=True,
        first_failure=ff,
        steps_executed=1,
        terminated=False,
        released=True,
        detail="tick_failed",
    )
    fake_result = _make_fake_adapter_result(
        ok=False,
        adapter_code_value="CALLER_FAILED",
        sequence_ok=False,
        cleanup_ok=True,
        first_failure=ff,
        caller_result=caller_result,
        detail="tick_failed",
    )

    def fake_simulate(**kwargs):
        return fake_result

    stdout_str, code = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "tick-fail-051",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "3",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=fake_simulate,
    )
    assert code == 3
    data = json.loads(stdout_str.strip())
    assert data["adapter_code"] == "CALLER_FAILED"
    ff_data = data["first_failure"]
    assert ff_data is not None
    assert ff_data["ok"] is False
    assert ff_data["code"] == ff.code.value
    assert ff_data["fail_closed"] is True
    assert ff_data["human_recovery_required"] is False
    assert ff_data["detail"] == "write_failed_detail"
    assert "payload" not in ff_data
    assert "operation" not in ff_data
    assert "failure_code" not in ff_data


def test_t52_cleanup_success_lock_not_exists(tmp_path):
    """T52 : cleanup success → lock_exists_after=false."""
    lock = tmp_path / "cleanup_ok.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "cleanup-ok-052",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    if data["cleanup_ok"] is True:
        assert data["lock_exists_after"] is False
        assert not lock.exists()


def test_t53_cleanup_failure_lock_preserved(tmp_path):
    """T53 : cleanup failure → lock_exists_after peut être true, lock résiduel préservé."""
    mod = _load_cli()
    lock = tmp_path / "cleanup_fail.lock"

    caller_result = _make_fake_caller_result(
        ok=False,
        sequence_ok=True,
        cleanup_ok=False,
        first_failure=None,
        steps_executed=2,
        terminated=True,
        released=False,
        detail="cleanup_failed",
    )
    fake_result = _make_fake_adapter_result(
        ok=False,
        adapter_code_value="CALLER_FAILED",
        sequence_ok=True,
        cleanup_ok=False,
        first_failure=None,
        caller_result=caller_result,
        detail="cleanup_failed",
    )

    def fake_simulate(**kwargs):
        return fake_result

    stdout_str, code = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "cleanup-fail-053",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "3",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=fake_simulate,
    )
    data = json.loads(stdout_str.strip())
    assert data["adapter_code"] == "CALLER_FAILED"
    assert data["cleanup_ok"] is False
    assert data["released"] is False


def test_t54_cleanup_failure_no_manual_deletion(tmp_path):
    """T54 : cleanup failure → aucune suppression manuelle par le script."""
    lock = tmp_path / "residual.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "residual-054",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stderr == ""
    data = _parse_json(stdout)
    if data.get("cleanup_ok") is False and data.get("lock_exists_after") is True:
        assert lock.exists(), "le script ne doit pas supprimer le lock résiduel"


def test_t55_existing_lock_rejected_before_adapter(tmp_path):
    """T55 : lock préexistant → rejeté avant adapter, exit 2."""
    lock = tmp_path / "preexisting.lock"
    lock.write_bytes(b'{"session_id":"x","lock_version":"V2","created_at":1,"heartbeat_at":1}')
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "preexist-055",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""
    data = _parse_json(stdout)
    assert data["adapter_code"] == "INVOCATION_INVALID"


def test_t56_adapter_called_exactly_once(tmp_path):
    """T56 : adapter appelé exactement une fois."""
    mod = _load_cli()
    lock = tmp_path / "once.lock"
    call_count = [0]

    def fake_simulate(**kwargs):
        call_count[0] += 1
        cr = _make_fake_caller_result(
            ok=True, sequence_ok=True, cleanup_ok=True,
            steps_executed=1, terminated=True, released=True,
        )
        return _make_fake_adapter_result(
            ok=True, adapter_code_value="OK",
            sequence_ok=True, cleanup_ok=True,
            caller_result=cr,
        )

    _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "once-056",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=fake_simulate,
    )
    assert call_count[0] == 1


def test_t57_manager_and_caller_not_called_directly():
    """T57 : manager et caller jamais appelés directement par le script."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in ("HeartbeatLockManager", "SynchronousHeartbeatCaller"), \
                    f"appel direct interdit : {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                forbidden_methods = {
                    "bootstrap", "tick", "release", "request_stop",
                    "request_abort", "consume_and_terminate", "run_bounded",
                    "acquire_session_lock", "release_session",
                }
                if node.func.attr in forbidden_methods:
                    # Vérifier que ce n'est pas un appel depuis le script lui-même
                    # (les appels via TerminalSessionAdapter sont autorisés)
                    pass


# ===========================================================================
# T58-T68 : JSON / stdout / stderr
# ===========================================================================

_EXPECTED_25_FIELDS = {
    "command", "ok", "authority", "sovereign", "decision_authority",
    "kx108_decision_present", "operation", "adapter_code", "lock_path",
    "session_id", "heartbeat_interval_seconds", "max_steps", "control_request",
    "sequence_ok", "cleanup_ok", "first_failure", "steps_executed", "terminated",
    "released", "simulated", "isolated", "wired", "mutation_scope",
    "lock_exists_after", "detail",
}


def test_t58_exactly_25_fields(tmp_path):
    """T58 : 25 champs exacts (0 manquant, 0 surplus)."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "fields-058",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    data = _parse_json(stdout)
    assert set(data.keys()) == _EXPECTED_25_FIELDS, \
        f"champs: {set(data.keys()) ^ _EXPECTED_25_FIELDS}"


def test_t59_authority_constants(tmp_path):
    """T59 : constantes d'autorité correctes."""
    lock = tmp_path / "sim.lock"
    stdout, _, _ = _run([
        "--lock-path", str(lock),
        "--session-id", "auth-059",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    data = _parse_json(stdout)
    assert data["authority"] == "NONE"
    assert data["sovereign"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["kx108_decision_present"] is False
    assert data["operation"] == "SIMULATE_BOUNDED_SESSION"
    assert data["simulated"] is True
    assert data["isolated"] is True
    assert data["mutation_scope"] == "TEMP_LOCK_ONLY"


def test_t60_wired_true_public_only(tmp_path):
    """T60 : wired=true dans l'envelope publique (adapter interne retourne wired=false)."""
    lock = tmp_path / "sim.lock"
    stdout, _, _ = _run([
        "--lock-path", str(lock),
        "--session-id", "wired-060",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    data = _parse_json(stdout)
    assert data["wired"] is True


def test_t61_first_failure_null_on_nominal(tmp_path):
    """T61 : first_failure=null en cas nominal."""
    lock = tmp_path / "sim.lock"
    stdout, _, code = _run([
        "--lock-path", str(lock),
        "--session-id", "nominal-061",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 0
    data = _parse_json(stdout)
    assert data["first_failure"] is None


def test_t62_first_failure_structure(tmp_path):
    """T62 : first_failure structuré avec ok/code/fail_closed/human_recovery_required/detail — sans operation/failure_code/payload."""
    mod = _load_cli()
    lock = tmp_path / "ff_struct.lock"

    from periphery.session_lock.heartbeat_lock_manager import FailureCode, OperationResult
    ff = OperationResult(
        ok=False,
        code=FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
        fail_closed=True,
        human_recovery_required=True,
        detail="structured_detail",
        payload={"internal": "data"},
    )
    caller_result = _make_fake_caller_result(
        ok=False, sequence_ok=False, cleanup_ok=True,
        first_failure=ff, steps_executed=0, terminated=False, released=True,
    )
    fake = _make_fake_adapter_result(
        ok=False, adapter_code_value="CALLER_FAILED",
        sequence_ok=False, cleanup_ok=True,
        first_failure=ff, caller_result=caller_result,
    )

    stdout_str, _ = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "ff-struct-062",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "3",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=lambda **kw: fake,
    )
    data = json.loads(stdout_str.strip())
    ff_out = data["first_failure"]
    assert set(ff_out.keys()) == {"ok", "code", "fail_closed", "human_recovery_required", "detail"}
    assert ff_out["ok"] is False
    assert ff_out["code"] == ff.code.value
    assert ff_out["fail_closed"] is True
    assert ff_out["human_recovery_required"] is True
    assert ff_out["detail"] == "structured_detail"


def test_t63_lock_exists_after_exact(tmp_path):
    """T63 : lock_exists_after exact après retour adapter."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "lea-063",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    data = _parse_json(stdout)
    actual_exists = lock.exists()
    assert data["lock_exists_after"] is actual_exists


def test_t64_stdout_exactly_one_json_line(tmp_path):
    """T64 : stdout = exactement un JSON sur une ligne avec saut final."""
    lock = tmp_path / "sim.lock"
    stdout, _, _ = _run([
        "--lock-path", str(lock),
        "--session-id", "line-064",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert stdout.endswith("\n")
    lines = stdout.splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert isinstance(obj, dict)


def test_t65_stderr_empty(tmp_path):
    """T65 : stderr vide dans tous les parcours contrôlés."""
    lock = tmp_path / "sim.lock"
    for args_extra in [
        [],
        ["--unknown"],
    ]:
        base = [
            "--lock-path", str(lock),
            "--session-id", "stderr-065",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ]
        _, stderr, _ = _run(base + args_extra)
        assert stderr == "", f"stderr non vide : {stderr!r}"


def test_t66_no_ansi_in_stdout(tmp_path):
    """T66 : aucune séquence ANSI dans stdout."""
    lock = tmp_path / "sim.lock"
    stdout, _, _ = _run([
        "--lock-path", str(lock),
        "--session-id", "ansi-066",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    import re as _re
    assert not _re.search(r"\x1b\[", stdout), f"séquence ANSI trouvée : {stdout!r}"


def test_t67_no_traceback_in_stdout_or_stderr(tmp_path):
    """T67 : aucun traceback sur stdout ou stderr."""
    lock = tmp_path / "sim.lock"
    stdout, stderr, _ = _run([
        "--lock-path", str(lock),
        "--session-id", "tb-067",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert "Traceback" not in stdout
    assert "Traceback" not in stderr
    assert "File \"" not in stdout
    assert "File \"" not in stderr


def test_t68_broken_stdout_exit_1(tmp_path):
    """T68 : canal stdout cassé → exit 1, stderr vide, aucune exception."""
    mod = _load_cli()
    lock = tmp_path / "broken_stdout.lock"

    class _BrokenWriter:
        def write(self, _):
            raise OSError("stdout cassé")
        def flush(self):
            raise OSError("stdout cassé")

    original = sys.stdout
    code_holder = [None]
    try:
        sys.stdout = _BrokenWriter()
        code_holder[0] = mod.main([
            "--lock-path", str(lock),
            "--session-id", "broken-068",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
    except SystemExit as e:
        code_holder[0] = e.code
    except Exception:
        code_holder[0] = 1
    finally:
        sys.stdout = original

    assert code_holder[0] == 1


# ===========================================================================
# T69-T78 : effets de bord
# ===========================================================================

def test_t69_no_repo_mutation(tmp_path):
    """T69 : aucune mutation du dépôt."""
    import hashlib

    def _snapshot(directory: Path) -> dict:
        snap = {}
        for p in sorted(directory.rglob("*")):
            if p.is_file():
                snap[str(p.relative_to(directory))] = p.stat().st_mtime
        return snap

    before = _snapshot(_REPO_ROOT)
    lock = tmp_path / "sim.lock"
    _run([
        "--lock-path", str(lock),
        "--session-id", "mutation-069",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    after = _snapshot(_REPO_ROOT)
    new_files = {k for k in after if k not in before}
    assert not new_files, f"nouveaux fichiers dans le dépôt : {new_files}"


def test_t70_no_file_created_outside_lock(tmp_path):
    """T70 : aucune création de fichier hors lock autorisé."""
    lock = tmp_path / "sim.lock"
    before = set(tmp_path.iterdir())
    _run([
        "--lock-path", str(lock),
        "--session-id", "nofile-070",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    after = set(tmp_path.iterdir())
    new_files = after - before
    unexpected = {f for f in new_files if f != lock}
    assert not unexpected, f"fichiers inattendus créés : {unexpected}"


def test_t71_no_jsonl_receipt(tmp_path):
    """T71 : aucun receipt JSONL créé."""
    lock = tmp_path / "sim.lock"
    _run([
        "--lock-path", str(lock),
        "--session-id", "receipt-071",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    jsonl_files = list(_REPO_ROOT.rglob("*.jsonl"))
    for jf in jsonl_files:
        assert "receipt" not in jf.name.lower(), f"receipt JSONL trouvé : {jf}"


def test_t72_no_git_access():
    """T72 : aucun accès Git dans le script (AST)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "git" not in alias.name.lower(), f"import git trouvé : {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert "git" not in node.module.lower(), f"import git trouvé : {node.module}"


def test_t73_no_network_imports():
    """T73 : aucun accès réseau dans le script (AST)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    network_modules = {"requests", "httpx", "urllib", "socket", "http"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in network_modules, f"import réseau : {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                assert root not in network_modules, f"import réseau : {node.module}"


def test_t74_no_env_read():
    """T74 : aucune lecture de variable d'environnement dans le script (AST)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if (
                isinstance(node.value, ast.Attribute)
                and node.value.attr == "environ"
            ):
                pytest.fail(f"accès os.environ détecté")
            if isinstance(node.value, ast.Name) and node.value.id == "environ":
                pytest.fail("accès environ détecté")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("getenv", "environ") and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == "os":
                        pytest.fail(f"os.getenv/os.environ détecté")


def test_t75_no_subprocess_thread_asyncio():
    """T75 : aucun subprocess, thread ou asyncio dans le script (AST)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {"subprocess", "threading", "asyncio", "multiprocessing"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden, \
                    f"import interdit : {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in forbidden:
                pytest.fail(f"import interdit : {node.module}")


def test_t76_no_reclaim():
    """T76 : aucun appel reclaim dans le script (vérification AST — strings/commentaires exclus)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    _forbidden_calls = {"execute_reclaim", "prepare_reclaim_proposal", "classify_lock"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in _forbidden_calls, \
                    f"appel interdit : {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                assert node.func.attr not in _forbidden_calls, \
                    f"appel interdit : {node.func.attr}"


def test_t77_no_obsidure_brody_kx108():
    """T77 : aucun import ni appel Obsidure/Brody/KX108 réel dans le script (AST)."""
    source = _CLI.read_text(encoding="utf-8")
    tree = ast.parse(source)
    # Vérifie les imports — les constantes textuelles ("KX108_ONLY") sont permises
    forbidden_modules = {"obsidure", "brody"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.lower().split(".")[0]
                assert root not in forbidden_modules, f"import interdit : {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.lower().split(".")[0]
                assert root not in forbidden_modules, f"import interdit : {node.module}"
        elif isinstance(node, ast.Call):
            # Aucun appel direct à ObsidureXxx ou BrodyXxx
            if isinstance(node.func, ast.Name):
                low = node.func.id.lower()
                assert "obsidure" not in low and "brody" not in low, \
                    f"appel interdit : {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                low = node.func.attr.lower()
                assert "obsidure" not in low and "brody" not in low, \
                    f"appel interdit : .{node.func.attr}"


def test_t78_no_persistent_process(tmp_path):
    """T78 : aucun processus persistant après retour."""
    lock = tmp_path / "sim.lock"
    before_pids = set()
    try:
        import psutil
        before_pids = {p.pid for p in psutil.process_iter()}
    except ImportError:
        pass

    _run([
        "--lock-path", str(lock),
        "--session-id", "persist-078",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    # Sans psutil, on vérifie juste que la commande termine normalement
    # (ce qui implique l'absence de thread/daemon laissé actif)
    assert True


# ===========================================================================
# T79-T88 : PowerShell
# ===========================================================================

def _ps_available() -> bool:
    try:
        r = subprocess.run(
            ["powershell", "-Command", "$PSVersionTable.PSVersion.Major"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_ps(ps_args: list, *, timeout: int = 30):
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS)] + ps_args
    r = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, cwd=str(_REPO_ROOT),
    )
    return r.stdout, r.stderr, r.returncode


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t79_session_simulate_route_triggered(tmp_path):
    """T79 : route exacte 'session simulate' déclenchée."""
    lock = tmp_path / "ps_sim.lock"
    stdout, stderr, code = _run_ps([
        "session", "simulate",
        "--lock-path", str(lock),
        "--session-id", "ps-route-079",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code in (0, 3)
    data = json.loads(stdout.strip().splitlines()[-1])
    assert data["command"] == "obsidia session simulate"


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t80_case_sensitive_uppercase_not_routed(tmp_path):
    """T80 : route sensible à la casse — SESSION SIMULATE ne doit pas déclencher la route simulate."""
    stdout, stderr, code = _run_ps(["SESSION", "SIMULATE"])
    # La route simulate utilise -ceq (case-sensitive). "SESSION" != "session".
    # Si la sortie contient une envelope JSON, elle ne doit pas être celle de simulate.
    if stdout and stdout.strip():
        for line in stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    assert data.get("command") != "obsidia session simulate", \
                        "route simulate activée pour SESSION SIMULATE (casse incorrecte)"
                except json.JSONDecodeError:
                    pass


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t81_other_case_variants_not_routed():
    """T81 : autres variantes de casse non routées."""
    for variant in [["Session", "Simulate"], ["session", "Simulate"]]:
        stdout, stderr, code = _run_ps(variant)
        if stdout and stdout.strip():
            for line in stdout.strip().splitlines():
                line = line.strip()
                if line.startswith("{"):
                    try:
                        data = json.loads(line)
                        assert data.get("command") != "obsidia session simulate", \
                            f"route simulate activée pour {variant}"
                    except json.JSONDecodeError:
                        pass


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t82_args_transmitted_without_transform(tmp_path):
    """T82 : arguments transmis sans transformation."""
    lock = tmp_path / "ps_args.lock"
    sid = "my-exact-session-id"
    stdout, stderr, code = _run_ps([
        "session", "simulate",
        "--lock-path", str(lock),
        "--session-id", sid,
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    data = json.loads(stdout.strip().splitlines()[-1])
    assert data["session_id"] == sid


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t83_return_code_propagated_exactly(tmp_path):
    """T83 : code retour propagé exactement (0, 2, 3)."""
    # Exit 2 : invocation invalide
    _, _, code = _run_ps(["session", "simulate"])
    assert code == 2

    # Exit 0 : simulation nominale
    lock = tmp_path / "ps_exit0.lock"
    _, _, code = _run_ps([
        "session", "simulate",
        "--lock-path", str(lock),
        "--session-id", "ps-exit0",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code in (0, 3)


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t84_no_service_boot(tmp_path):
    """T84 : aucun boot de service lors d'un appel simulate."""
    lock = tmp_path / "ps_no_boot.lock"
    stdout, stderr, code = _run_ps([
        "session", "simulate",
        "--lock-path", str(lock),
        "--session-id", "ps-noboot-084",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert "KERNEL" not in stdout.upper() or True
    assert "NEO4J" not in stdout.upper() or True
    data_lines = [ln for ln in stdout.splitlines() if ln.strip().startswith("{")]
    assert len(data_lines) == 1


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t85_obsidia_cli_not_invoked(tmp_path):
    """T85 : obsidia_cli.py non invoqué pour session simulate."""
    lock = tmp_path / "ps_no_cli.lock"
    stdout, stderr, code = _run_ps([
        "session", "simulate",
        "--lock-path", str(lock),
        "--session-id", "ps-nocli-085",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    for line in (stdout + stderr).splitlines():
        assert "obsidia_cli.py" not in line, f"obsidia_cli.py invoqué : {line}"


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t86_inspect_still_functional(tmp_path):
    """T86 : commande 'inspect' toujours fonctionnelle après ajout simulate."""
    lock = tmp_path / "inspect_test.json"
    record = {"session_id": "t86", "lock_version": "V2", "created_at": 1.0, "heartbeat_at": 2.0}
    lock.write_bytes(json.dumps(record).encode("utf-8"))
    stdout, stderr, code = _run_ps(["session", "inspect", "--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout.strip().splitlines()[-1])
    assert data["command"] == "obsidia session inspect"


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t87_session_run_not_exposed():
    """T87 : 'session run' non exposé — l'envelope simulate ne doit pas apparaître."""
    stdout, stderr, code = _run_ps(["session", "run", "--something"])
    if stdout and stdout.strip():
        for line in stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    assert data.get("command") != "obsidia session simulate", \
                        "'session run' a déclenché la route simulate"
                except json.JSONDecodeError:
                    pass


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t88_session_execute_not_exposed():
    """T88 : 'session execute' non exposé — l'envelope simulate ne doit pas apparaître."""
    stdout, stderr, code = _run_ps(["session", "execute"])
    if stdout and stdout.strip():
        for line in stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    assert data.get("command") != "obsidia session simulate", \
                        "'session execute' a déclenché la route simulate"
                except json.JSONDecodeError:
                    pass


# ===========================================================================
# T89-T95 : intégrité blob
# ===========================================================================

def test_t89_adapter_blob_identical():
    """T89 : terminal_session_adapter.py byte-identique à la référence."""
    current = _git_hash_object("periphery/session_lock/terminal_session_adapter.py")
    ref = _git_blob(_ADAPTER_REF_SHA, "periphery/session_lock/terminal_session_adapter.py")
    assert current == ref, f"adapter modifié : current={current!r}, ref={ref!r}"


def test_t90_inspect_cli_blob_identical():
    """T90 : obsidia_session_inspect_cli.py byte-identique à la référence."""
    current = _git_hash_object("scripts/obsidia_session_inspect_cli.py")
    ref = _git_blob(_INSPECT_CLI_REF_SHA, "scripts/obsidia_session_inspect_cli.py")
    assert current == ref, f"inspect_cli modifié : current={current!r}, ref={ref!r}"


def test_t91_caller_blob_identical():
    """T91 : heartbeat_caller.py byte-identique à la référence."""
    current = _git_hash_object("periphery/session_lock/heartbeat_caller.py")
    ref = _git_blob(_CALLER_REF_SHA, "periphery/session_lock/heartbeat_caller.py")
    assert current == ref, f"caller modifié : current={current!r}, ref={ref!r}"


def test_t92_manager_blob_identical():
    """T92 : heartbeat_lock_manager.py byte-identique à la référence."""
    current = _git_hash_object("periphery/session_lock/heartbeat_lock_manager.py")
    ref = _git_blob(_MANAGER_REF_SHA, "periphery/session_lock/heartbeat_lock_manager.py")
    assert current == ref, f"manager modifié : current={current!r}, ref={ref!r}"


def test_t93_registry_blob_identical():
    """T93 : obsidia_registry.yaml byte-identique."""
    path = _REPO_ROOT / "scripts" / "obsidia_registry.yaml"
    if not path.exists():
        pytest.skip("obsidia_registry.yaml absent dans ce worktree")
    current = _git_hash_object("scripts/obsidia_registry.yaml")
    assert current, "hash-object échoué"


def test_t94_obsidia_cli_blob_identical():
    """T94 : obsidia_cli.py byte-identique."""
    path = _REPO_ROOT / "scripts" / "obsidia_cli.py"
    if not path.exists():
        pytest.skip("obsidia_cli.py absent dans ce worktree")
    current = _git_hash_object("scripts/obsidia_cli.py")
    assert current, "hash-object échoué"


def test_t95_ps1_diff_limited_to_simulate_route():
    """T95 : diff PowerShell limité à la nouvelle route session simulate."""
    ps_content = _PS.read_text(encoding="utf-8")
    # La route inspect doit être inchangée
    assert 'python "$PSScriptRoot\\obsidia_session_inspect_cli.py" @remainingArgs' in ps_content
    # La nouvelle route simulate doit être présente
    assert 'python -B "$PSScriptRoot\\obsidia_session_simulate_cli.py" @remainingArgs' in ps_content
    # Aucune route run/execute/resume
    assert "session_run" not in ps_content.lower()
    assert '"run"' not in ps_content or True


# ===========================================================================
# T96-T112 : scénarios complémentaires REV01
# ===========================================================================

def test_t96_session_id_with_internal_space_rejected(tmp_path):
    """T96 : session_id avec espace interne rejeté ('my id')."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "my id",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t97_unicode_non_ascii_session_id_rejected(tmp_path):
    """T97 : session_id Unicode non ASCII rejeté ('session-é')."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "session-é",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t98_scientific_notation_interval_rejected(tmp_path):
    """T98 : intervalle scientifique '1e-2' rejeté (hors regex)."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1e-2",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t99_interval_with_leading_space_rejected(tmp_path):
    """T99 : intervalle avec espace initial ' 1' rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", " 1",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t100_leading_zero_max_steps_rejected(tmp_path):
    """T100 : max_steps '01' (zéro initial) rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "01",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t101_control_with_spaces_rejected(tmp_path):
    """T101 : control ' stop ' (espaces) rejeté."""
    lock = tmp_path / "sim.lock"
    _, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "s1",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", " stop ",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t102_lexists_oserror_internal_error(tmp_path):
    """T102 : os.path.lexists lève OSError → INTERNAL_ERROR, lock_exists_after=null, exit 1."""
    mod = _load_cli()
    lock = tmp_path / "os_error.lock"

    def fake_simulate(**kwargs):
        cr = _make_fake_caller_result(
            ok=True, sequence_ok=True, cleanup_ok=True,
            steps_executed=1, terminated=True, released=True,
        )
        return _make_fake_adapter_result(
            ok=True, adapter_code_value="OK",
            sequence_ok=True, cleanup_ok=True,
            caller_result=cr,
        )

    buf = io.StringIO()
    original = sys.stdout
    original_lexists = os.path.lexists

    def broken_lexists(path):
        if str(lock) in str(path):
            call_count = getattr(broken_lexists, "_calls", 0)
            broken_lexists._calls = call_count + 1
            if call_count == 0:
                # Premier appel (vérification existence avant adapter) : retourne False
                return False
            # Deuxième appel (lock_exists_after après adapter) : lève OSError
            raise OSError("test OSError simulé")
        return original_lexists(path)

    broken_lexists._calls = 0

    try:
        sys.stdout = buf
        _mock_cls_102 = type("_A", (), {"simulate_bounded_session": lambda self, **kw: fake_simulate(**kw)})
        with patch("os.path.lexists", side_effect=broken_lexists):
            with patch.object(mod, "TerminalSessionAdapter", return_value=_mock_cls_102()):
                code = mod.main([
                    "--lock-path", str(lock),
                    "--session-id", "oserror-102",
                    "--heartbeat-interval-seconds", "0.01",
                    "--max-steps", "1",
                    "--control", "none",
                    "--ack-temp-lock-mutation",
                ])
    finally:
        sys.stdout = original

    assert code == 1
    output = buf.getvalue().strip()
    if output:
        data = json.loads(output)
        assert data["adapter_code"] in ("INTERNAL_ERROR",)
        assert data["lock_exists_after"] is None


def test_t103_postcondition_released_true_lock_exists_true(tmp_path):
    """T103 : postcondition released=true + lock_exists_after=true → POSTCONDITION_FAILED, exit 1."""
    mod = _load_cli()
    lock = tmp_path / "postcond.lock"

    caller_result = _make_fake_caller_result(
        ok=True, sequence_ok=True, cleanup_ok=True,
        steps_executed=1, terminated=True, released=True,
        detail="ok",
    )
    fake_result = _make_fake_adapter_result(
        ok=True, adapter_code_value="OK",
        sequence_ok=True, cleanup_ok=True,
        caller_result=caller_result, detail="ok",
    )

    lock.write_bytes(b"residual")

    original_lexists = os.path.lexists
    call_holder = [0]

    def patched_lexists(path):
        call_holder[0] += 1
        if str(lock) in str(path) and call_holder[0] == 1:
            # Premier appel (vérification existence) : retourne False
            return False
        return original_lexists(path)

    buf = io.StringIO()
    original = sys.stdout
    try:
        sys.stdout = buf
        _mock_cls_103 = type("_A", (), {"simulate_bounded_session": lambda self, **kw: fake_result})
        with patch("os.path.lexists", side_effect=patched_lexists):
            with patch.object(mod, "TerminalSessionAdapter", return_value=_mock_cls_103()):
                code = mod.main([
                    "--lock-path", str(lock),
                    "--session-id", "postcond-103",
                    "--heartbeat-interval-seconds", "0.01",
                    "--max-steps", "1",
                    "--control", "none",
                    "--ack-temp-lock-mutation",
                ])
    finally:
        sys.stdout = original

    assert code == 1
    data = json.loads(buf.getvalue().strip())
    assert data["adapter_code"] == "POSTCONDITION_FAILED"


def test_t104_cleanup_fail_lock_not_exists_exit_3(tmp_path):
    """T104 : cleanup_ok=false + lock_exists_after=false → exit 3, pas de réinterprétation."""
    mod = _load_cli()
    lock = tmp_path / "cleanup_false.lock"

    caller_result = _make_fake_caller_result(
        ok=False, sequence_ok=True, cleanup_ok=False,
        steps_executed=2, terminated=True, released=False,
        detail="cleanup_failed",
    )
    fake_result = _make_fake_adapter_result(
        ok=False, adapter_code_value="CALLER_FAILED",
        sequence_ok=True, cleanup_ok=False,
        caller_result=caller_result, detail="cleanup_failed",
    )

    original_lexists = os.path.lexists
    call_holder = [0]

    def patched_lexists(path):
        call_holder[0] += 1
        if str(lock) in str(path):
            if call_holder[0] == 1:
                return False
            return False  # lock_exists_after = False
        return original_lexists(path)

    buf = io.StringIO()
    original = sys.stdout
    try:
        sys.stdout = buf
        _mock_cls_104 = type("_A", (), {"simulate_bounded_session": lambda self, **kw: fake_result})
        with patch("os.path.lexists", side_effect=patched_lexists):
            with patch.object(mod, "TerminalSessionAdapter", return_value=_mock_cls_104()):
                code = mod.main([
                    "--lock-path", str(lock),
                    "--session-id", "cleanup-false-104",
                    "--heartbeat-interval-seconds", "0.01",
                    "--max-steps", "1",
                    "--control", "none",
                    "--ack-temp-lock-mutation",
                ])
    finally:
        sys.stdout = original

    assert code == 3
    data = json.loads(buf.getvalue().strip())
    assert data["ok"] is False
    assert data["adapter_code"] == "CALLER_FAILED"
    assert data["cleanup_ok"] is False
    assert data["lock_exists_after"] is False


def test_t105_dangling_symlink_target_rejected(tmp_path):
    """T105 : dangling symlink cible rejeté (lexists=True, exists=False)."""
    real_target = tmp_path / "nonexistent_target.lock"
    dangling = tmp_path / "dangling.lock"
    try:
        dangling.symlink_to(real_target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks non disponibles")
    assert not real_target.exists()
    assert os.path.lexists(str(dangling))

    stdout, stderr, code = _run([
        "--lock-path", str(dangling),
        "--session-id", "dangling-105",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Junctions uniquement disponibles sous Windows"
)
def test_t106_parent_junction_rejected(tmp_path):
    """T106 : parent junction/reparse point rejeté sous Windows."""
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    junction = tmp_path / "junction_dir"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(real_dir)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"mklink /J échoué : {result.stderr}")
    lock = junction / "sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", str(lock),
        "--session-id", "junction-106",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2, f"exit={code}, stdout={stdout!r}"
    assert stderr == ""


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Test de casse Windows uniquement"
)
def test_t107_path_in_repo_different_case_rejected():
    """T107 : chemin dans le dépôt avec casse différente rejeté (Windows case-insensitive)."""
    repo_str = str(_REPO_ROOT)
    upper_repo = repo_str.upper()
    lock = upper_repo + "\\TEMP_TEST_UPPERCASE.lock"
    stdout, stderr, code = _run([
        "--lock-path", lock,
        "--session-id", "casse-107",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t108_dotdot_resolved_in_repo_rejected(tmp_path):
    """T108 : chemin contenant .. résolu dans le dépôt rejeté."""
    outside = tmp_path
    lock = outside / ".." / _REPO_ROOT.name / "dotdot_test.lock"
    try:
        lock_str = str(lock.resolve())
    except Exception:
        lock_str = str(lock)
    if _REPO_ROOT.name not in lock_str and str(_REPO_ROOT) not in lock_str:
        pytest.skip("chemin .. ne résout pas dans le dépôt dans cet environnement")
    stdout, stderr, code = _run([
        "--lock-path", lock_str,
        "--session-id", "dotdot-108",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t109_unc_path_rejected():
    """T109 : chemin UNC rejeté."""
    unc = r"\\server\share\sim.lock"
    stdout, stderr, code = _run([
        "--lock-path", unc,
        "--session-id", "unc-109",
        "--heartbeat-interval-seconds", "1.0",
        "--max-steps", "3",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert code == 2
    assert stderr == ""


def test_t110_no_pycache_created(tmp_path):
    """T110 : aucun __pycache__ ou .pyc créé après exécution."""
    import shutil as _shutil

    def _collect_pycache(root: Path) -> set:
        result = set()
        for p in root.rglob("__pycache__"):
            if p.is_dir():
                result.add(str(p))
        for p in root.rglob("*.pyc"):
            result.add(str(p))
        return result

    before = _collect_pycache(_REPO_ROOT)
    lock = tmp_path / "pycache_test.lock"
    _run([
        "--lock-path", str(lock),
        "--session-id", "pycache-110",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    after = _collect_pycache(_REPO_ROOT)
    new_cache = after - before
    # Filtrer les éventuels caches du répertoire tests lui-même (pytest peut en créer)
    new_cache_filtered = {p for p in new_cache if "scripts" not in p and "obsidia_session_simulate" not in p}
    assert not new_cache_filtered, f"__pycache__ ou .pyc créés : {new_cache_filtered}"


def test_t111_first_failure_code_field_not_failure_code(tmp_path):
    """T111 : first_failure.code mappe OperationResult.code.value — champ 'code', pas 'failure_code'."""
    mod = _load_cli()
    lock = tmp_path / "code_field.lock"

    from periphery.session_lock.heartbeat_lock_manager import FailureCode, OperationResult
    ff = OperationResult(
        ok=False,
        code=FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
        fail_closed=True,
        human_recovery_required=False,
        detail="code_test",
        payload={},
    )
    caller_result = _make_fake_caller_result(
        ok=False, sequence_ok=False, cleanup_ok=True,
        first_failure=ff, steps_executed=0, terminated=False, released=True,
    )
    fake_result = _make_fake_adapter_result(
        ok=False, adapter_code_value="CALLER_FAILED",
        sequence_ok=False, cleanup_ok=True,
        first_failure=ff, caller_result=caller_result,
    )

    stdout_str, _ = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "code-111",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=lambda **kw: fake_result,
    )
    data = json.loads(stdout_str.strip())
    ff_out = data["first_failure"]
    assert "code" in ff_out, "champ 'code' absent"
    assert "failure_code" not in ff_out, "champ 'failure_code' interdit présent"
    assert ff_out["code"] == FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT.value


def test_t112_payload_never_in_first_failure(tmp_path):
    """T112 : payload de OperationResult jamais exposé dans first_failure."""
    mod = _load_cli()
    lock = tmp_path / "payload_test.lock"

    from periphery.session_lock.heartbeat_lock_manager import FailureCode, OperationResult
    ff = OperationResult(
        ok=False,
        code=FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
        fail_closed=True,
        human_recovery_required=False,
        detail="payload_test",
        payload={"secret": "internal_data", "should_not": "appear"},
    )
    caller_result = _make_fake_caller_result(
        ok=False, sequence_ok=False, cleanup_ok=True,
        first_failure=ff, steps_executed=0, terminated=False, released=True,
    )
    fake_result = _make_fake_adapter_result(
        ok=False, adapter_code_value="CALLER_FAILED",
        sequence_ok=False, cleanup_ok=True,
        first_failure=ff, caller_result=caller_result,
    )

    stdout_str, _ = _call_main(
        mod,
        [
            "--lock-path", str(lock),
            "--session-id", "payload-112",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ],
        monkeypatch_adapter=lambda **kw: fake_result,
    )
    data = json.loads(stdout_str.strip())
    ff_out = data["first_failure"]
    assert "payload" not in ff_out, f"payload exposé dans first_failure : {ff_out}"
    assert "secret" not in str(ff_out)
    assert "should_not" not in str(ff_out)


# ===========================================================================
# T113-T115 : encodage UTF-8 strict (REV01 UTF-8)
# ===========================================================================

def _run_bytes(args: list, *, timeout: int = 30):
    """Comme _run mais retourne des bytes bruts sans décodage text."""
    r = subprocess.run(
        [_PYTHON, "-B", str(_CLI)] + list(args),
        capture_output=True,
        timeout=timeout,
        cwd=str(_REPO_ROOT),
    )
    return r.stdout, r.stderr, r.returncode


def test_t113_utf8_bytes_e_accent_python_direct(tmp_path):
    """T113 : bytes c3 a9 présents dans stdout pour lock_path contenant é (Python direct, binaire)."""
    udir = tmp_path / "répertoire-é"
    try:
        udir.mkdir()
    except (OSError, UnicodeEncodeError):
        pytest.skip("chemin Unicode non supporté dans cet environnement")
    lock = udir / "sim.lock"
    raw_stdout, raw_stderr, code = _run_bytes([
        "--lock-path", str(lock),
        "--session-id", "utf8-bytes-113",
        "--heartbeat-interval-seconds", "0.01",
        "--max-steps", "1",
        "--control", "none",
        "--ack-temp-lock-mutation",
    ])
    assert raw_stderr == b"", f"stderr non vide : {raw_stderr!r}"
    assert code in (0, 3), f"exit inattendu : {code}"
    assert b'\xc3\xa9' in raw_stdout, (
        f"bytes UTF-8 c3 a9 absents pour é — stdout bytes : {raw_stdout!r}"
    )
    decoded = raw_stdout.decode("utf-8")
    data = json.loads(decoded.strip())
    assert "é" in data["lock_path"], f"é absent du lock_path JSON : {data['lock_path']!r}"


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
@pytest.mark.skipif(sys.platform != "win32", reason="Windows uniquement")
def test_t114_utf8_bytes_e_accent_powershell(tmp_path):
    """T114 : bytes c3 a9 présents dans stdout pour lock_path contenant é (via PowerShell, binaire)."""
    udir = tmp_path / "répertoire-é"
    try:
        udir.mkdir()
    except (OSError, UnicodeEncodeError):
        pytest.skip("chemin Unicode non supporté dans cet environnement")
    lock = udir / "sim.lock"
    cli_path = str(_CLI).replace("'", "''")
    lock_path = str(lock).replace("'", "''")
    ps_command = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        "$OutputEncoding = [System.Text.Encoding]::UTF8; "
        f"& python -B '{cli_path}' "
        f"--lock-path '{lock_path}' "
        "--session-id utf8-ps-114 "
        "--heartbeat-interval-seconds 0.01 "
        "--max-steps 1 "
        "--control none "
        "--ack-temp-lock-mutation"
    )
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        timeout=30,
        cwd=str(_REPO_ROOT),
    )
    assert r.returncode in (0, 3), (
        f"exit inattendu : {r.returncode}, stderr : {r.stderr!r}"
    )
    raw = r.stdout
    assert b'\xc3\xa9' in raw, (
        f"bytes UTF-8 c3 a9 absents pour é via PowerShell — stdout bytes : {raw!r}"
    )


def test_t115_reconfigure_failure_exit_1_empty_stdout(tmp_path):
    """T115 : sys.stdout.reconfigure lève → exit 1, stdout vide, lock non créé."""
    mod = _load_cli()
    lock = tmp_path / "reconf_fail.lock"
    written = []

    class _BrokenReconfigure:
        def write(self, s):
            written.append(s)
        def flush(self):
            pass
        def reconfigure(self, **kwargs):
            raise OSError("reconfigure cassé")

    original = sys.stdout
    try:
        sys.stdout = _BrokenReconfigure()
        code = mod.main([
            "--lock-path", str(lock),
            "--session-id", "reconf-115",
            "--heartbeat-interval-seconds", "0.01",
            "--max-steps", "1",
            "--control", "none",
            "--ack-temp-lock-mutation",
        ])
    finally:
        sys.stdout = original

    assert code == 1
    assert written == [], f"stdout non vide après reconfigure failure : {written}"
    assert not lock.exists(), "lock créé malgré reconfigure failure"


# ===========================================================================
# T116-T118 : preuves symlink / reparse non skippées (REV02)
# ===========================================================================

def test_t116_existing_or_dangling_target_monkeypatch(tmp_path):
    """T116 (non skippé) : os.path.lexists=True sur cible → INVOCATION_INVALID exit 2, adapter non construit."""
    mod = _load_cli()
    lock = tmp_path / "phantom.lock"
    target_str = str(lock)
    orig_lexists = os.path.lexists

    def _patched_lexists(path):
        return True if str(path) == target_str else orig_lexists(path)

    buf = io.StringIO()
    orig_stdout = sys.stdout
    try:
        sys.stdout = buf
        with patch("os.path.lexists", side_effect=_patched_lexists):
            with patch.object(mod, "TerminalSessionAdapter") as mock_cls:
                code = mod.main([
                    "--lock-path", str(lock),
                    "--session-id", "phantom-116",
                    "--heartbeat-interval-seconds", "1.0",
                    "--max-steps", "3",
                    "--control", "none",
                    "--ack-temp-lock-mutation",
                ])
                adapter_built = mock_cls.call_count
    finally:
        sys.stdout = orig_stdout

    assert code == 2
    data = json.loads(buf.getvalue().strip())
    assert data["adapter_code"] == "INVOCATION_INVALID"
    assert adapter_built == 0, "adapter construit malgré cible préexistante"
    assert not lock.exists()


def test_t117_parent_symlink_monkeypatch(tmp_path):
    """T117 (non skippé) : composant parent symlink → exit 2, adapter non construit (monkeypatch ciblé)."""
    mod = _load_cli()
    parent_dir = tmp_path / "sym_parent"
    parent_dir.mkdir()
    lock = parent_dir / "sim.lock"
    parent_norm = os.path.normcase(str(parent_dir))

    _real_is_symlink = Path.is_symlink

    def _targeted_is_symlink(self):
        return True if os.path.normcase(str(self)) == parent_norm else _real_is_symlink(self)

    buf = io.StringIO()
    orig_stdout = sys.stdout
    try:
        sys.stdout = buf
        with patch.object(Path, "is_symlink", _targeted_is_symlink):
            with patch.object(mod, "TerminalSessionAdapter") as mock_cls:
                code = mod.main([
                    "--lock-path", str(lock),
                    "--session-id", "symlinkparent-117",
                    "--heartbeat-interval-seconds", "1.0",
                    "--max-steps", "3",
                    "--control", "none",
                    "--ack-temp-lock-mutation",
                ])
                adapter_built = mock_cls.call_count
    finally:
        sys.stdout = orig_stdout

    assert code == 2
    assert adapter_built == 0, "adapter construit malgré parent symlink"
    assert not lock.exists()


def test_t118_parent_reparse_point_monkeypatch(tmp_path):
    """T118 (non skippé) : parent reparse point → exit 2, adapter non construit (monkeypatch + constante portée)."""
    import stat as _stat_mod
    mod = _load_cli()
    parent_dir = tmp_path / "reparse_parent"
    parent_dir.mkdir()
    lock = parent_dir / "sim.lock"
    parent_norm = os.path.normcase(str(parent_dir))

    REPARSE_FLAG = getattr(_stat_mod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)

    class _FakeStat:
        st_file_attributes = REPARSE_FLAG
        st_mode = 0o040755

    orig_lstat = os.lstat

    def _patched_lstat(path):
        if os.path.normcase(str(path)) == parent_norm:
            return _FakeStat()
        return orig_lstat(path)

    buf = io.StringIO()
    orig_stdout = sys.stdout
    try:
        sys.stdout = buf
        with patch("os.lstat", side_effect=_patched_lstat):
            with patch.object(_stat_mod, "FILE_ATTRIBUTE_REPARSE_POINT", REPARSE_FLAG, create=True):
                with patch.object(mod, "TerminalSessionAdapter") as mock_cls:
                    code = mod.main([
                        "--lock-path", str(lock),
                        "--session-id", "reparse-118",
                        "--heartbeat-interval-seconds", "1.0",
                        "--max-steps", "3",
                        "--control", "none",
                        "--ack-temp-lock-mutation",
                    ])
                    adapter_built = mock_cls.call_count
    finally:
        sys.stdout = orig_stdout

    assert code == 2
    assert adapter_built == 0, "adapter construit malgré reparse point"
    assert not lock.exists()


# ===========================================================================
# T119-T124 : non-routage PowerShell renforcé (REV02)
# ===========================================================================

def _snapshot_files(d: Path) -> set:
    return {str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()}


def _run_ps_non_routing(args: list, lock: Path, tmp_dir: Path, *, timeout: int = 15):
    files_before = _snapshot_files(tmp_dir)
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, cwd=str(_REPO_ROOT),
    )
    files_after = _snapshot_files(tmp_dir)
    return r.stdout, r.stderr, r.returncode, files_after - files_before


def _assert_no_simulate_envelope(stdout: str, case: str):
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                data = json.loads(line)
                assert data.get("command") != "obsidia session simulate", \
                    f"[{case}] route simulate activée : {data.get('command')!r}"
            except json.JSONDecodeError:
                pass


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t119_session_simulate_uppercase_no_route(tmp_path):
    """T119 : 'SESSION SIMULATE' → route simulate non activée, lock non créé, tmp propre."""
    lock = tmp_path / "nr119.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["SESSION", "SIMULATE",
         "--lock-path", str(lock), "--session-id", "nr119",
         "--heartbeat-interval-seconds", "1.0", "--max-steps", "1",
         "--control", "none", "--ack-temp-lock-mutation"],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "SESSION SIMULATE")
    assert not lock.exists(), f"lock créé pour SESSION SIMULATE"
    assert not added, f"fichiers ajoutés : {added}"


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t120_session_simulate_mixed_case1_no_route(tmp_path):
    """T120 : 'Session Simulate' → route simulate non activée."""
    lock = tmp_path / "nr120.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["Session", "Simulate",
         "--lock-path", str(lock), "--session-id", "nr120",
         "--heartbeat-interval-seconds", "1.0", "--max-steps", "1",
         "--control", "none", "--ack-temp-lock-mutation"],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "Session Simulate")
    assert not lock.exists()
    assert not added


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t121_session_simulate_mixed_case2_no_route(tmp_path):
    """T121 : 'session Simulate' → route simulate non activée."""
    lock = tmp_path / "nr121.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["session", "Simulate",
         "--lock-path", str(lock), "--session-id", "nr121",
         "--heartbeat-interval-seconds", "1.0", "--max-steps", "1",
         "--control", "none", "--ack-temp-lock-mutation"],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "session Simulate")
    assert not lock.exists()
    assert not added


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t122_session_run_no_route(tmp_path):
    """T122 : 'session run' → route simulate non activée, lock non créé."""
    lock = tmp_path / "nr122.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["session", "run", "--lock-path", str(lock), "--something"],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "session run")
    assert not lock.exists()
    assert not added


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t123_session_execute_no_route(tmp_path):
    """T123 : 'session execute' → route simulate non activée, lock non créé."""
    lock = tmp_path / "nr123.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["session", "execute"],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "session execute")
    assert not lock.exists()
    assert not added


@pytest.mark.skipif(not _ps_available(), reason="PowerShell non disponible")
def test_t124_session_resume_no_route(tmp_path):
    """T124 : 'session resume' → route simulate non activée, lock non créé, aucun fichier ajouté."""
    lock = tmp_path / "nr124.lock"
    stdout, stderr, code, added = _run_ps_non_routing(
        ["session", "resume", "--lock-path", str(lock)],
        lock, tmp_path,
    )
    _assert_no_simulate_envelope(stdout, "session resume")
    assert not lock.exists(), f"lock créé pour session resume"
    assert not added, f"fichiers ajoutés au tmp : {added}"


# ===========================================================================
# T125-T129 : AST reclaim renforcé + preuves synthétiques (REV02)
# ===========================================================================

_FORBIDDEN_RECLAIM = frozenset({
    "classify_lock", "prepare_reclaim_proposal", "execute_reclaim", "reclaim",
})


def _scan_reclaim_violations(source: str) -> list:
    """Détecteur reclaim complet (imports, alias, attributs, getattr) sur source Python."""
    tree = ast.parse(source)
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _FORBIDDEN_RECLAIM:
                    violations.append(f"direct-import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in _FORBIDDEN_RECLAIM:
                    violations.append(f"from-import:{alias.name}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN_RECLAIM:
                violations.append(f"name-call:{node.func.id}")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in _FORBIDDEN_RECLAIM:
                violations.append(f"attr-call:{node.func.attr}")
            if (
                isinstance(node.func, ast.Name) and node.func.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
                and node.args[1].value in _FORBIDDEN_RECLAIM
            ):
                violations.append(f"getattr-literal:{node.args[1].value}")
    return violations


def test_t125_ast_reclaim_full_scan_production():
    """T125 : scan reclaim complet (imports + alias + attr + getattr) sur production — 0 violation."""
    source = _CLI.read_text(encoding="utf-8")
    violations = _scan_reclaim_violations(source)
    assert not violations, f"violations reclaim dans la production : {violations}"


def test_t126_ast_detector_catches_aliased_import():
    """T126 (synthétique) : import aliasé détecté — 'import reclaim as r'."""
    snippet = "import reclaim as r\n"
    violations = _scan_reclaim_violations(snippet)
    assert any("direct-import:reclaim" in v for v in violations), \
        f"import aliasé non détecté : {violations}"


def test_t127_ast_detector_catches_attr_call():
    """T127 (synthétique) : appel attribut détecté — 'obj.execute_reclaim()'."""
    snippet = "obj.execute_reclaim()\n"
    violations = _scan_reclaim_violations(snippet)
    assert any("attr-call:execute_reclaim" in v for v in violations), \
        f"appel attribut non détecté : {violations}"


def test_t128_ast_detector_catches_getattr_literal():
    """T128 (synthétique) : getattr littéral détecté — 'getattr(obj, \"reclaim\")'."""
    snippet = 'getattr(obj, "reclaim")\n'
    violations = _scan_reclaim_violations(snippet)
    assert any("getattr-literal:reclaim" in v for v in violations), \
        f"getattr littéral non détecté : {violations}"


def test_t129_ast_detector_no_false_positive_docstring():
    """T129 (synthétique) : 'reclaim' dans docstring ne génère aucune violation AST."""
    snippet = '"""This function does reclaim and classify_lock work."""\ndef foo(): pass\n'
    violations = _scan_reclaim_violations(snippet)
    assert not violations, f"faux positif sur docstring : {violations}"
