"""Tests bornés — PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B_REV01.

Couvre SynchronousHeartbeatCaller (heartbeat_caller.py).

Toutes les valeurs numériques (interval, steps) sont des
TEST_FIXTURE_ONLY — elles n'établissent aucune valeur par défaut
de production (DECISION_H/I/J: PRODUCTION_VALUE_UNRESOLVED).

DECISION_AUTHORITY=KX108_ONLY. No IO hors tmp_path. No network. No ACT.
MUST_REMAIN_FALSE_UNDER_PART_B_REV01.
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    FailureCode,
    HeartbeatConfig,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
)
from periphery.session_lock.heartbeat_caller import (
    CallerPhase,
    CallerResult,
    SynchronousHeartbeatCaller,
)

# TEST_FIXTURE_ONLY — aucune valeur de production
_INTERVAL: float = 10.0  # TEST_FIXTURE_ONLY


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make_enabled_mgr(tmp_path: Path, clock: FakeClock) -> HeartbeatLockManager:
    config = HeartbeatConfig(enabled=True, heartbeat_interval_seconds=_INTERVAL)
    return HeartbeatLockManager(
        config, tmp_path / "session.lock.json", "sess-caller", clock=clock
    )


def _make_disabled_mgr(tmp_path: Path, clock: FakeClock) -> HeartbeatLockManager:
    config = HeartbeatConfig()  # disabled by default
    return HeartbeatLockManager(
        config, tmp_path / "session.lock.json", "sess-caller", clock=clock
    )


def _make_partial_mgr(tmp_path: Path, clock: FakeClock) -> HeartbeatLockManager:
    config = HeartbeatConfig(enabled=True)  # interval absent
    return HeartbeatLockManager(
        config, tmp_path / "session.lock.json", "sess-caller", clock=clock
    )


# ── T01 : construction sans activation automatique ───────────────────────────

def test_t01_construction_no_auto_activation(tmp_path):
    """Construire le caller ne déclenche aucune opération sur PART_A."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    assert caller.phase is CallerPhase.IDLE
    assert caller.steps_executed == 0
    assert caller.terminated is False
    assert caller.released is False
    assert not (tmp_path / "session.lock.json").exists()
    assert mgr.runtime_state is HeartbeatRuntimeState.NOT_STARTED


# ── T02 : aucune opération au constructeur ────────────────────────────────────

def test_t02_no_operation_at_construction(tmp_path):
    """Le constructeur ne crée pas le lock JSON."""
    clock = FakeClock()
    before_files = set(tmp_path.iterdir())
    mgr = _make_enabled_mgr(tmp_path, clock)
    SynchronousHeartbeatCaller(mgr)
    after_files = set(tmp_path.iterdir())
    assert before_files == after_files


# ── T03 : manager disabled → fail-closed ─────────────────────────────────────

def test_t03_disabled_manager_fail_closed(tmp_path):
    clock = FakeClock()
    mgr = _make_disabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    r = caller.bootstrap()
    assert r.ok is False
    assert r.part_a_result.code is FailureCode.MANAGER_DISABLED
    assert r.part_a_result.fail_closed is True
    assert caller.phase is CallerPhase.FAULTED
    assert not (tmp_path / "session.lock.json").exists()


# ── T04 : config incomplète → fail-closed ────────────────────────────────────

def test_t04_incomplete_config_fail_closed(tmp_path):
    clock = FakeClock()
    mgr = _make_partial_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    r = caller.bootstrap()
    assert r.ok is False
    assert r.part_a_result.code is FailureCode.HEARTBEAT_CONFIG_MISSING
    assert caller.phase is CallerPhase.FAULTED


# ── T05 : bootstrap nominal ───────────────────────────────────────────────────

def test_t05_bootstrap_nominal(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    r = caller.bootstrap()
    assert r.ok is True
    assert caller.phase is CallerPhase.BOOTSTRAPPED
    assert mgr.runtime_state is HeartbeatRuntimeState.ACTIVE_WAITING
    assert (tmp_path / "session.lock.json").exists()


# ── T06 : tick nominal RESUME_WAIT ───────────────────────────────────────────

def test_t06_tick_nominal_resume_wait(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    clock.advance(3)
    r = caller.tick()
    assert r.ok is True
    assert r.handoff == "RESUME_WAIT"
    assert caller.steps_executed == 1
    assert caller.phase is CallerPhase.TICKING


# ── T07 : STOP → CONSUME_CONTROL → terminaison ───────────────────────────────

def test_t07_stop_consume_control_terminate(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    caller.request_stop()
    r = caller.tick()
    assert r.handoff == "CONSUME_CONTROL"
    assert caller.phase is CallerPhase.CONTROL_REQUESTED
    r = caller.consume_and_terminate()
    assert r.ok is True
    assert caller.terminated is True
    assert caller.phase is CallerPhase.TERMINATED
    r = caller.release()
    assert r.ok is True
    assert caller.released is True
    assert caller.phase is CallerPhase.RELEASED


# ── T08 : ABORT → CONSUME_CONTROL → terminaison ──────────────────────────────

def test_t08_abort_consume_control_terminate(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    caller.request_abort()
    r = caller.tick()
    assert r.handoff == "CONSUME_CONTROL"
    r = caller.consume_and_terminate()
    assert r.ok is True
    assert caller.terminated is True


# ── T09 : aucun sommeil automatique ──────────────────────────────────────────

def test_t09_no_auto_sleep(tmp_path):
    """tick() retourne immédiatement — pas de sleep."""
    import time
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    t0 = time.monotonic()
    caller.tick()
    elapsed = time.monotonic() - t0
    assert elapsed < 1.0, f"tick() trop lent : {elapsed:.3f}s — sleep suspecté"


# ── T10 : aucune boucle infinie ───────────────────────────────────────────────

def test_t10_no_infinite_loop_in_source():
    """Le source de heartbeat_caller.py ne contient aucun 'while True'."""
    src = Path(__file__).parent.parent / "session_lock" / "heartbeat_caller.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            test = node.test
            if isinstance(test, ast.Constant) and test.value is True:
                pytest.fail("'while True' détecté dans heartbeat_caller.py")


# ── T11 : run_bounded respecte max_steps ─────────────────────────────────────

def test_t11_run_bounded_respects_max_steps(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    r = caller.run_bounded(max_steps=3)
    # 3 ticks au plus, puis release automatique
    assert caller.steps_executed <= 3
    assert caller.released is True


# ── T12 : arrêt immédiat sur première erreur PART_A ──────────────────────────

def test_t12_stop_on_first_part_a_error(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    # Corrompre le lock pour provoquer une faute
    (tmp_path / "session.lock.json").write_bytes(b'{"tampered": true}')
    r = caller.tick()
    assert r.ok is False
    assert caller.phase is CallerPhase.FAULTED
    assert caller.steps_executed == 0


# ── T13 : état FAULTED exposé dans le résultat ───────────────────────────────

def test_t13_faulted_state_in_result(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    (tmp_path / "session.lock.json").write_bytes(b"{}")
    r = caller.tick()
    assert r.ok is False
    assert r.phase is CallerPhase.FAULTED
    assert r.runtime_state is HeartbeatRuntimeState.FAULTED


# ── T14 : release nominal ────────────────────────────────────────────────────

def test_t14_release_nominal(tmp_path):
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    r = caller.release()
    assert r.ok is True
    assert caller.released is True
    assert not (tmp_path / "session.lock.json").exists()


# ── T15 : release refusé sans suppression manuelle ───────────────────────────

def test_t15_release_refused_no_manual_deletion(tmp_path):
    """Release refusé → lock intact, pas de suppression manuelle."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    # Forcer un état invalide pour le release
    mgr.runtime_state = HeartbeatRuntimeState.NOT_STARTED
    r = caller.release()
    assert r.ok is False
    assert r.part_a_result.code is FailureCode.RELEASE_SESSION_STATE_INVALID
    # Lock encore présent — pas de suppression manuelle
    assert (tmp_path / "session.lock.json").exists()
    assert caller.released is False


# ── T16 : aucune mutation hors lock_path ─────────────────────────────────────

def test_t16_no_mutation_outside_lock_path(tmp_path):
    clock = FakeClock()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("intact", encoding="utf-8")
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.run_bounded(max_steps=2)
    assert sentinel.read_text(encoding="utf-8") == "intact"


# ── T17 : aucun appel à execute_reclaim ──────────────────────────────────────

def test_t17_no_execute_reclaim_call_in_source():
    """heartbeat_caller.py ne contient aucun appel (AST) à execute_reclaim."""
    src = Path(__file__).parent.parent / "session_lock" / "heartbeat_caller.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # attr call : mgr.execute_reclaim(...)
            if isinstance(func, ast.Attribute) and func.attr == "execute_reclaim":
                pytest.fail(
                    "Appel à execute_reclaim() détecté dans heartbeat_caller.py"
                    " — interdit par DECISION_G / MUST_REMAIN_FALSE_UNDER_PART_B_REV01"
                )
            # bare call : execute_reclaim(...)
            if isinstance(func, ast.Name) and func.id == "execute_reclaim":
                pytest.fail(
                    "Appel à execute_reclaim() détecté dans heartbeat_caller.py"
                )


# ── T18 : aucun import interdit ──────────────────────────────────────────────

def test_t18_no_forbidden_imports():
    """heartbeat_caller.py n'importe rien de apps/, scripts/, sigma/, kernel/."""
    src = Path(__file__).parent.parent / "session_lock" / "heartbeat_caller.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = ("apps", "scripts", "sigma", "kernel", "lean", "threading", "asyncio", "subprocess")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ""
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
            elif isinstance(node, ast.Import):
                module = ",".join(alias.name for alias in node.names)
            for fb in forbidden:
                assert fb not in module, (
                    f"Import interdit détecté : '{module}' contient '{fb}'"
                )


# ── T19 : déterminisme ───────────────────────────────────────────────────────

def test_t19_determinism(tmp_path):
    def run(sub: str) -> list:
        clock = FakeClock()
        d = tmp_path / sub
        d.mkdir()
        config = HeartbeatConfig(enabled=True, heartbeat_interval_seconds=_INTERVAL)
        mgr = HeartbeatLockManager(config, d / "s.json", "sess-det", clock=clock)
        caller = SynchronousHeartbeatCaller(mgr)
        results = []
        results.append(caller.bootstrap())
        clock.advance(3)
        results.append(caller.tick())
        results.append(caller.release())
        return [(r.ok, r.phase, r.part_a_result.ok) for r in results]

    assert run("a") == run("b")


# ── T20 : PART_A byte-identique à 69b8985 ────────────────────────────────────

def test_t20_part_a_unchanged(tmp_path):
    """Les 3 fichiers PART_A n'ont pas été touchés."""
    import subprocess
    worktree = Path(__file__).parent.parent.parent
    result = subprocess.run(
        ["git", "diff", "--name-only", "69b8985", "HEAD",
         "--", "periphery/session_lock/heartbeat_lock_manager.py",
                "periphery/session_lock/__init__.py",
                "periphery/tests/test_heartbeat_lock_manager.py"],
        cwd=str(worktree),
        capture_output=True, text=True,
    )
    changed = result.stdout.strip()
    assert changed == "", (
        f"PART_A modifiée depuis 69b8985 : {changed}"
    )
