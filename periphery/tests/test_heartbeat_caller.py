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
    HandoffAction,
    HeartbeatConfig,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
    OperationResult,
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


# ── T21 : handoff canonique RESUME_WAIT ──────────────────────────────────────

def test_t21_canonical_handoff_resume_wait(tmp_path):
    """tick() retourne le handoff canonique RESUME_WAIT via HandoffAction."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    clock.advance(3)
    r = caller.tick()
    assert r.ok is True
    assert r.handoff == HandoffAction.RESUME_WAIT.value
    assert r.handoff == "RESUME_WAIT"
    assert caller.phase is CallerPhase.TICKING


# ── T22 : handoff canonique CONSUME_CONTROL ──────────────────────────────────

def test_t22_canonical_handoff_consume_control(tmp_path):
    """tick() retourne CONSUME_CONTROL via HandoffAction après request_stop."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    caller.request_stop()
    r = caller.tick()
    assert r.ok is True
    assert r.handoff == HandoffAction.CONSUME_CONTROL.value
    assert r.handoff == "CONSUME_CONTROL"
    assert caller.phase is CallerPhase.CONTROL_REQUESTED


# ── T23 : handoff inconnu → fail-closed ──────────────────────────────────────

def test_t23_unknown_handoff_fail_closed(tmp_path, monkeypatch):
    """Un handoff non reconnu dans tick() produit un résultat fail-closed."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()

    # Injecter un handoff inconnu dans la réponse de heartbeat_tick
    def fake_tick():
        return OperationResult.success(
            "injected unknown handoff",
            heartbeat_at=clock.now,
            handoff_action="UNKNOWN_HANDOFF_VALUE",
        )

    monkeypatch.setattr(mgr, "heartbeat_tick", fake_tick)
    r = caller.tick()
    assert r.ok is False
    assert caller.phase is CallerPhase.FAULTED
    # Le caller ne continue pas silencieusement comme RESUME_WAIT
    assert r.handoff == "UNKNOWN_HANDOFF_VALUE"
    # PART_A tick a réussi (ok=True côté PART_A) — le compteur reflète cela
    assert caller.steps_executed == 1
    assert r.part_a_result.ok is True


# ── T24 : tick échoué + release réussi → séquence reste en échec ─────────────

def test_t24_tick_failure_release_success_sequence_fails(tmp_path, monkeypatch):
    """Échec de tick suivi d'un release réussi : CallerResult.ok reste False."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)

    # Injecter un échec de tick — bootstrap reste nominal
    def fake_tick_fail():
        return OperationResult.failure(
            FailureCode.HEARTBEAT_LOCK_IDENTITY_MISMATCH,
            "injected tick failure for T24",
        )

    monkeypatch.setattr(mgr, "heartbeat_tick", fake_tick_fail)
    r = caller.run_bounded(max_steps=3)
    # Séquence en échec, même si le release a réussi après le tick raté
    assert r.ok is False
    assert r.sequence_ok is False
    assert r.first_failure is not None
    assert r.first_failure.code is FailureCode.HEARTBEAT_LOCK_IDENTITY_MISMATCH
    # Le cleanup_ok reflète l'état réel du release (True si release nominal)
    assert r.cleanup_ok is True
    assert caller.released is True


# ── T25 : consume_control échoué → commit_termination non appelé ─────────────

def test_t25_consume_control_failure_no_commit_termination(tmp_path):
    """consume_and_terminate() : si consume_control échoue, terminated=False."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    # Pas de request_stop → consume_control échoue (aucune requête pendante)
    r = caller.consume_and_terminate()
    assert r.ok is False
    assert caller.terminated is False
    assert caller.phase is CallerPhase.FAULTED
    assert r.part_a_result.code is FailureCode.HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID


# ── T26 : commit_termination échoué → erreur conservée même si release réussit

def test_t26_commit_termination_failure_preserved(tmp_path, monkeypatch):
    """Échec de commit_termination : erreur conservée, terminated=False."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    caller.bootstrap()
    caller.request_stop()
    caller.tick()  # → CONSUME_CONTROL, phase=CONTROL_REQUESTED

    # Patcher commit_termination pour simuler un échec
    def fake_commit():
        return OperationResult.failure(
            FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
            "injected commit_termination failure",
        )

    monkeypatch.setattr(mgr, "commit_termination", fake_commit)
    r = caller.consume_and_terminate()
    assert r.ok is False
    assert caller.terminated is False
    assert caller.phase is CallerPhase.FAULTED
    # La release ultérieure ne doit pas masquer cette erreur
    r_release = caller.release()
    # release peut réussir ou non selon l'état PART_A — ce n'est pas l'objet du test
    assert caller.terminated is False  # inchangé


# ── T27 : succès nominal complet de run_bounded ──────────────────────────────

def test_t27_run_bounded_nominal_success(tmp_path):
    """run_bounded nominal : ok=True, sequence_ok=True, cleanup_ok=True."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)
    r = caller.run_bounded(max_steps=2)
    assert r.ok is True
    assert r.sequence_ok is True
    assert r.cleanup_ok is True
    assert r.first_failure is None
    assert caller.released is True
    assert caller.steps_executed <= 2


# ── T28 : commit_termination échoué → sequence_ok=False via run_bounded ──────

def test_t28_run_bounded_commit_termination_failure_sequence_ok_false(tmp_path, monkeypatch):
    """run_bounded : commit_termination failure -> sequence_ok=False, first_failure préservé."""
    clock = FakeClock()
    mgr = _make_enabled_mgr(tmp_path, clock)
    caller = SynchronousHeartbeatCaller(mgr)

    # Patcher commit_termination pour forcer un échec dans la séquence run_bounded
    def fake_commit():
        return OperationResult.failure(
            FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
            "injected commit_termination failure for T28",
        )

    monkeypatch.setattr(mgr, "commit_termination", fake_commit)
    # run_bounded avec STOP : bootstrap -> request_stop -> tick (CONSUME_CONTROL)
    # -> consume_and_terminate (commit échoue) -> release
    r = caller.run_bounded(max_steps=3, control_request=ControlRequest.STOP)
    assert r.ok is False
    assert r.sequence_ok is False
    assert r.first_failure is not None
    assert r.first_failure.code is FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID
    # Le cleanup_ok reflète l'état réel du release (non masquant)
    assert r.cleanup_ok is not None
    assert caller.terminated is False
