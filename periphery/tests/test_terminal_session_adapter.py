"""Tests de TERMINAL_SESSION_ADAPTER_V0.

Fixture de configuration :
    HeartbeatConfig(enabled=True, heartbeat_interval_seconds=1.0, ...)
    La valeur 1.0 est : TEST_FIXTURE_ONLY_NOT_PRODUCTION

Couvre 24 scénarios conformément à la spécification normative
docs/paliers/TERMINAL_SESSION_ADAPTER_V0_APPROVED.md.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Optional

import pytest

from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    FailureCode,
    HeartbeatConfig,
    HeartbeatLockManager,
    OperationResult,
)
from periphery.session_lock.terminal_session_adapter import (
    AdapterCode,
    AdapterOperation,
    TerminalSessionAdapter,
    TerminalSessionAdapterResult,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

WORKTREE_ROOT = Path(__file__).resolve().parents[2]

# TEST_FIXTURE_ONLY_NOT_PRODUCTION — valeur 1.0 non normative pour la production
_TEST_CONFIG = HeartbeatConfig(
    enabled=True,
    heartbeat_interval_seconds=1.0,  # TEST_FIXTURE_ONLY_NOT_PRODUCTION
    max_v2_future_clock_skew_seconds=None,
    human_approved_corrected_gf_r01_sha256=None,
)

_PART_A_REF_SHA = "69b8985ab21eb678ab7ed507e67c5c41e3441eaa"
_CALLER_REF_SHA = "b2011885bd7f9b52ce486983034f5046f2e56ea6"

_ADAPTER_MODULE = (
    WORKTREE_ROOT / "periphery" / "session_lock" / "terminal_session_adapter.py"
)

_FORBIDDEN_IMPORTS = frozenset({
    "scripts", "apps", "sigma", "kernel", "lean",
    "obsidure", "brody", "subprocess", "threading",
    "asyncio", "multiprocessing", "socket", "requests",
    "httpx",
})

_FORBIDDEN_URLLIB_MODULES = frozenset({"urllib.request"})

_FORBIDDEN_CALLS = frozenset({
    "classify_lock",
    "prepare_reclaim_proposal",
    "execute_reclaim",
})

_PROTECTED_FILES = [
    "periphery/session_lock/heartbeat_lock_manager.py",
    "periphery/session_lock/heartbeat_caller.py",
    "periphery/session_lock/__init__.py",
    "periphery/tests/test_heartbeat_lock_manager.py",
    "periphery/tests/test_heartbeat_caller.py",
]

_PART_A_FILES = [
    "periphery/session_lock/heartbeat_lock_manager.py",
    "periphery/session_lock/__init__.py",
    "periphery/tests/test_heartbeat_lock_manager.py",
]

_CALLER_FILES = [
    "periphery/session_lock/heartbeat_caller.py",
    "periphery/tests/test_heartbeat_caller.py",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_lock(session_id: str = "TEST_SESSION_01", now: float = 1000.0) -> bytes:
    record = {
        "session_id": session_id,
        "lock_version": "V2",
        "created_at": now,
        "heartbeat_at": now,
    }
    return json.dumps(record, sort_keys=True).encode("utf-8")


def _git_blob_hash_at_commit(commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "ls-tree", commit, path],
        capture_output=True, text=True, cwd=str(WORKTREE_ROOT),
    )
    parts = result.stdout.strip().split()
    return parts[2] if len(parts) >= 3 else ""


def _git_current_blob_hash(path: str) -> str:
    result = subprocess.run(
        ["git", "hash-object", path],
        capture_output=True, text=True, cwd=str(WORKTREE_ROOT),
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Test 1 : constructeur sans effet de bord
# ---------------------------------------------------------------------------

def test_constructor_no_side_effects(tmp_path):
    sentinel = tmp_path / "sentinel"
    sentinel.mkdir()
    before = sorted(sentinel.iterdir())
    _adapter = TerminalSessionAdapter()
    after = sorted(sentinel.iterdir())
    assert before == after


# ---------------------------------------------------------------------------
# Test 2 : inspect chemin absent
# ---------------------------------------------------------------------------

def test_inspect_absent_path(tmp_path):
    adapter = TerminalSessionAdapter()
    r = adapter.inspect_lock(tmp_path / "nonexistent.json")
    assert r.ok is False
    assert r.adapter_code == AdapterCode.LOCK_NOT_FOUND
    assert r.lock_record is None
    assert r.caller_result is None
    assert r.operation == AdapterOperation.INSPECT_LOCK


# ---------------------------------------------------------------------------
# Test 3 : inspect chemin non fichier (répertoire)
# ---------------------------------------------------------------------------

def test_inspect_not_a_file(tmp_path):
    adapter = TerminalSessionAdapter()
    r = adapter.inspect_lock(tmp_path)
    assert r.ok is False
    assert r.adapter_code == AdapterCode.LOCK_NOT_FILE
    assert r.lock_record is None


# ---------------------------------------------------------------------------
# Test 4 : inspect JSON invalide (texte malformé)
# ---------------------------------------------------------------------------

def test_inspect_json_invalid(tmp_path):
    lock_file = tmp_path / "lock.json"
    lock_file.write_bytes(b"{invalid json content")
    adapter = TerminalSessionAdapter()
    r = adapter.inspect_lock(lock_file)
    assert r.ok is False
    assert r.adapter_code == AdapterCode.LOCK_JSON_INVALID
    assert r.lock_record is None


# ---------------------------------------------------------------------------
# Test 5 : inspect structure invalide (champ manquant)
# ---------------------------------------------------------------------------

def test_inspect_schema_invalid(tmp_path):
    lock_file = tmp_path / "lock.json"
    lock_file.write_bytes(json.dumps({"only_unknown_field": 1}).encode())
    adapter = TerminalSessionAdapter()
    r = adapter.inspect_lock(lock_file)
    assert r.ok is False
    assert r.adapter_code == AdapterCode.LOCK_SCHEMA_INVALID
    assert r.lock_record is None


# ---------------------------------------------------------------------------
# Test 6 : inspect lock valide
# ---------------------------------------------------------------------------

def test_inspect_valid_lock(tmp_path):
    lock_file = tmp_path / "lock.json"
    lock_file.write_bytes(_make_valid_lock("TEST_SESSION_ALPHA"))
    adapter = TerminalSessionAdapter()
    r = adapter.inspect_lock(lock_file)
    assert r.ok is True
    assert r.adapter_code == AdapterCode.OK
    assert r.session_id == "TEST_SESSION_ALPHA"
    assert r.lock_record is not None
    assert r.lock_record["lock_version"] == "V2"
    assert r.lock_record["session_id"] == "TEST_SESSION_ALPHA"
    assert r.caller_result is None
    assert r.simulated is False
    assert r.mutation_scope == "NONE"
    assert r.authority == "NONE"
    assert r.sovereign is False
    assert r.decision_authority == "KX108_ONLY"
    assert r.kx108_decision_present is False
    assert r.isolated is True
    assert r.wired is False
    assert r.operation == AdapterOperation.INSPECT_LOCK


# ---------------------------------------------------------------------------
# Test 7 : inspect ne modifie pas les octets du fichier
# ---------------------------------------------------------------------------

def test_inspect_does_not_modify_bytes(tmp_path):
    lock_file = tmp_path / "lock.json"
    raw = _make_valid_lock("TEST_SESSION_BETA")
    lock_file.write_bytes(raw)
    adapter = TerminalSessionAdapter()
    adapter.inspect_lock(lock_file)
    assert lock_file.read_bytes() == raw


# ---------------------------------------------------------------------------
# Test 8 : simulation manager disabled → fail-closed
# ---------------------------------------------------------------------------

def test_simulate_disabled_fail_closed(tmp_path):
    adapter = TerminalSessionAdapter()
    disabled_config = HeartbeatConfig(enabled=False)
    lock_file = tmp_path / "lock.json"
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_01",
        heartbeat_config=disabled_config,
        max_steps=1,
    )
    assert r.ok is False
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 9 : configuration incomplète → fail-closed (interval manquant)
# ---------------------------------------------------------------------------

def test_simulate_incomplete_config_fail_closed(tmp_path):
    adapter = TerminalSessionAdapter()
    incomplete = HeartbeatConfig(
        enabled=True,
        heartbeat_interval_seconds=None,
    )
    lock_file = tmp_path / "lock.json"
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_01",
        heartbeat_config=incomplete,
        max_steps=1,
    )
    assert r.ok is False
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 10 : simulation nominale bornée
# ---------------------------------------------------------------------------

def test_simulate_nominal_bounded(tmp_path):
    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_NOMINAL",
        heartbeat_config=_TEST_CONFIG,
        max_steps=3,
    )
    assert r.ok is True
    assert r.sequence_ok is True
    assert r.cleanup_ok is True
    assert r.first_failure is None
    assert r.simulated is True
    assert r.mutation_scope == "TEMP_LOCK_ONLY"
    assert r.authority == "NONE"
    assert r.sovereign is False
    assert r.decision_authority == "KX108_ONLY"
    assert r.kx108_decision_present is False
    assert r.isolated is True
    assert r.wired is False
    assert r.caller_result is not None
    assert r.caller_result.released is True
    assert r.caller_result.steps_executed == 3
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 11 : simulation avec STOP
# ---------------------------------------------------------------------------

def test_simulate_with_stop(tmp_path):
    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_STOP",
        heartbeat_config=_TEST_CONFIG,
        max_steps=10,
        control_request=ControlRequest.STOP,
    )
    assert r.ok is True
    assert r.sequence_ok is True
    assert r.cleanup_ok is True
    assert r.caller_result is not None
    assert r.caller_result.terminated is True
    assert r.caller_result.released is True
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 12 : simulation avec ABORT
# ---------------------------------------------------------------------------

def test_simulate_with_abort(tmp_path):
    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_ABORT",
        heartbeat_config=_TEST_CONFIG,
        max_steps=10,
        control_request=ControlRequest.ABORT,
    )
    assert r.ok is True
    assert r.sequence_ok is True
    assert r.cleanup_ok is True
    assert r.caller_result is not None
    assert r.caller_result.terminated is True
    assert r.caller_result.released is True
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 13 : lock déjà présent → refus
# ---------------------------------------------------------------------------

def test_simulate_lock_already_present(tmp_path):
    lock_file = tmp_path / "lock.json"
    original_bytes = _make_valid_lock("TEST_SESSION_PRE")
    lock_file.write_bytes(original_bytes)
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_NEW",
        heartbeat_config=_TEST_CONFIG,
        max_steps=3,
    )
    assert r.ok is False
    assert lock_file.read_bytes() == original_bytes


# ---------------------------------------------------------------------------
# Test 14 : bootstrap échoué → aucun tick
# ---------------------------------------------------------------------------

def test_simulate_bootstrap_failed_no_tick(tmp_path):
    lock_file = tmp_path / "lock.json"
    lock_file.write_bytes(_make_valid_lock("TEST_SESSION_PRE"))
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_NEW",
        heartbeat_config=_TEST_CONFIG,
        max_steps=5,
    )
    assert r.ok is False
    assert r.caller_result is not None
    assert r.caller_result.steps_executed == 0


# ---------------------------------------------------------------------------
# Test 15 : tick échoué → première erreur conservée
# ---------------------------------------------------------------------------

def test_simulate_tick_failed_first_failure_preserved(tmp_path, monkeypatch):
    def _failing_tick(self) -> OperationResult:
        return OperationResult.failure(
            FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
            "mock tick failure",
        )

    monkeypatch.setattr(HeartbeatLockManager, "heartbeat_tick", _failing_tick)

    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_TICK_FAIL",
        heartbeat_config=_TEST_CONFIG,
        max_steps=3,
    )
    assert r.ok is False
    assert r.sequence_ok is False
    assert r.first_failure is not None
    assert r.caller_result is not None
    assert r.caller_result.steps_executed == 0


# ---------------------------------------------------------------------------
# Test 16 : release réussi
# ---------------------------------------------------------------------------

def test_simulate_release_success(tmp_path):
    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_RELEASE_OK",
        heartbeat_config=_TEST_CONFIG,
        max_steps=1,
    )
    assert r.cleanup_ok is True
    assert r.caller_result is not None
    assert r.caller_result.released is True
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 17 : release échoué
# ---------------------------------------------------------------------------

def test_simulate_release_failed(tmp_path, monkeypatch):
    def _failing_release(self) -> OperationResult:
        return OperationResult.failure(
            FailureCode.RELEASE_LOCK_DELETE_FAILED,
            "mock release failure",
        )

    monkeypatch.setattr(HeartbeatLockManager, "release_session", _failing_release)

    lock_file = tmp_path / "lock.json"
    adapter = TerminalSessionAdapter()
    r = adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_RELEASE_FAIL",
        heartbeat_config=_TEST_CONFIG,
        max_steps=1,
    )
    assert r.ok is False
    assert r.cleanup_ok is False
    assert r.caller_result is not None
    assert r.caller_result.released is False


# ---------------------------------------------------------------------------
# Test 18 : aucune mutation hors tmp_path
# ---------------------------------------------------------------------------

def test_no_mutation_outside_tmp_path(tmp_path):
    sentinel_dir = tmp_path / "sentinel"
    sentinel_dir.mkdir()
    sentinel_file = sentinel_dir / "check.txt"
    sentinel_content = b"unchanged_sentinel"
    sentinel_file.write_bytes(sentinel_content)

    lock_dir = tmp_path / "session"
    lock_dir.mkdir()
    lock_file = lock_dir / "lock.json"

    adapter = TerminalSessionAdapter()
    adapter.simulate_bounded_session(
        lock_path=lock_file,
        session_id="TEST_SESSION_MUT",
        heartbeat_config=_TEST_CONFIG,
        max_steps=2,
    )

    assert sentinel_file.read_bytes() == sentinel_content
    assert sorted(sentinel_dir.iterdir()) == [sentinel_file]
    assert not lock_file.exists()


# ---------------------------------------------------------------------------
# Test 19 : aucun appel aux méthodes de reclaim (AST)
# ---------------------------------------------------------------------------

def test_no_reclaim_methods_called():
    source = _ADAPTER_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                assert func.attr not in _FORBIDDEN_CALLS, (
                    f"appel interdit détecté dans l'adaptateur : {func.attr}"
                )
            elif isinstance(func, ast.Name):
                assert func.id not in _FORBIDDEN_CALLS, (
                    f"appel interdit détecté dans l'adaptateur : {func.id}"
                )


# ---------------------------------------------------------------------------
# Test 20 : aucun import interdit (AST)
# ---------------------------------------------------------------------------

def test_no_forbidden_imports():
    source = _ADAPTER_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0].lower()
                assert top not in _FORBIDDEN_IMPORTS, (
                    f"import interdit dans l'adaptateur : {alias.name}"
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0].lower()
                assert top not in _FORBIDDEN_IMPORTS, (
                    f"import interdit dans l'adaptateur : {node.module}"
                )
                full = node.module.lower()
                assert full not in _FORBIDDEN_URLLIB_MODULES, (
                    f"import interdit dans l'adaptateur : {node.module}"
                )


# ---------------------------------------------------------------------------
# Test 21 : déterminisme — mêmes entrées → résultats identiques
# ---------------------------------------------------------------------------

def test_determinism(tmp_path):
    adapter = TerminalSessionAdapter()
    lock_a = tmp_path / "lock_a.json"
    lock_b = tmp_path / "lock_b.json"

    r_a = adapter.simulate_bounded_session(
        lock_path=lock_a,
        session_id="TEST_SESSION_DET",
        heartbeat_config=_TEST_CONFIG,
        max_steps=2,
    )
    r_b = adapter.simulate_bounded_session(
        lock_path=lock_b,
        session_id="TEST_SESSION_DET",
        heartbeat_config=_TEST_CONFIG,
        max_steps=2,
    )

    assert r_a.ok == r_b.ok
    assert r_a.sequence_ok == r_b.sequence_ok
    assert r_a.cleanup_ok == r_b.cleanup_ok
    assert r_a.caller_result is not None
    assert r_b.caller_result is not None
    assert r_a.caller_result.steps_executed == r_b.caller_result.steps_executed
    assert r_a.caller_result.released == r_b.caller_result.released


# ---------------------------------------------------------------------------
# Test 22 : aucune mutation Git sur les fichiers protégés
# ---------------------------------------------------------------------------

def test_no_git_mutation():
    result = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--"] + _PROTECTED_FILES,
        capture_output=True, text=True, cwd=str(WORKTREE_ROOT),
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "", (
        f"fichiers protégés modifiés détectés : {result.stdout.strip()}"
    )


# ---------------------------------------------------------------------------
# Test 23 : PART_A byte-identique au commit de référence
# ---------------------------------------------------------------------------

def test_part_a_byte_identical():
    for f in _PART_A_FILES:
        current = _git_current_blob_hash(f)
        expected = _git_blob_hash_at_commit(_PART_A_REF_SHA, f)
        assert current and expected, f"hash introuvable pour {f}"
        assert current == expected, (
            f"PART_A modifié : {f}\n  attendu  : {expected}\n  obtenu   : {current}"
        )


# ---------------------------------------------------------------------------
# Test 24 : caller byte-identique au commit de référence
# ---------------------------------------------------------------------------

def test_caller_byte_identical():
    for f in _CALLER_FILES:
        current = _git_current_blob_hash(f)
        expected = _git_blob_hash_at_commit(_CALLER_REF_SHA, f)
        assert current and expected, f"hash introuvable pour {f}"
        assert current == expected, (
            f"Caller modifié : {f}\n  attendu  : {expected}\n  obtenu   : {current}"
        )
