"""Tests bornés — PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_A_REV10.

Couvre les comportements exigés par le mandat IMPLEMENT_BOUNDED :
verrou actif, candidat stale, horodatage futur au-delà du skew, état
absent/incomplet/corrompu, GF_R01 absent, disabled by default,
impossibilité d'un reclaim réel, déterminisme, absence de mutation hors
périmètre.

Les valeurs numériques utilisées ici (interval=10, skew=5) sont des
FIXTURES DE TEST locales : elles n'établissent aucune valeur par défaut
de production (les paramètres humains restent non résolus).

DECISION_AUTHORITY=KX108_ONLY. No IO hors tmp_path. No network. No ACT.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    FailureCode,
    HeartbeatConfig,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
    LockClassification,
)


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def make_manager(tmp_path: Path, clock: FakeClock, **cfg) -> HeartbeatLockManager:
    config = HeartbeatConfig(**cfg)
    return HeartbeatLockManager(
        config, tmp_path / "session.lock.json", "sess-t1", clock=clock)


ENABLED = dict(enabled=True, heartbeat_interval_seconds=10.0)


# ── disabled by default ──────────────────────────────────────────────────────

def test_disabled_by_default_all_operations_fail_closed(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock)  # HeartbeatConfig() par défaut
    for op in (mgr.acquire_session_lock, mgr.heartbeat_tick,
               mgr.consume_control, mgr.commit_termination,
               mgr.classify_lock, mgr.release_session,
               mgr.prepare_reclaim_proposal):
        res = op()
        assert res.ok is False
        assert res.code is FailureCode.MANAGER_DISABLED
        assert res.fail_closed is True
    assert not (tmp_path / "session.lock.json").exists()
    assert mgr.runtime_state is HeartbeatRuntimeState.NOT_STARTED


def test_enabled_without_interval_fails_closed(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, enabled=True)  # interval absent
    res = mgr.acquire_session_lock()
    assert res.ok is False
    assert res.code is FailureCode.HEARTBEAT_CONFIG_MISSING
    assert mgr.runtime_state is HeartbeatRuntimeState.NOT_STARTED
    assert not (tmp_path / "session.lock.json").exists()


# ── SECTION_12 : verrou actif, contrôle, terminaison, faute ─────────────────

def test_active_lock_with_valid_heartbeat(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    assert mgr.acquire_session_lock().ok
    clock.advance(3)
    res = mgr.heartbeat_tick()
    assert res.ok and res.payload["handoff_action"] == "RESUME_WAIT"
    cls = mgr.classify_lock()
    assert cls.ok
    assert cls.payload["classification"] == LockClassification.ACTIVE.value


def test_control_consumption_forbidden_in_active_tick_and_invalid_states(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    # état invalide (NOT_STARTED simulé) → aucun champ de contrôle modifié
    mgr.request_control(ControlRequest.STOP)
    saved = (mgr.control_request, mgr.control_request_pending,
             mgr.control_consumed, mgr.control_consumed_sequence)
    mgr.runtime_state = HeartbeatRuntimeState.NOT_STARTED
    res = mgr.consume_control()
    assert res.code is FailureCode.HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID
    assert (mgr.control_request, mgr.control_request_pending,
            mgr.control_consumed, mgr.control_consumed_sequence) == saved
    # ACTIVE_TICK → FORBIDDEN, requête préservée, routage post-tick
    mgr.runtime_state = HeartbeatRuntimeState.ACTIVE_TICK
    res = mgr.consume_control()
    assert res.ok is False
    assert res.payload.get("routed_to") == "HEARTBEAT_POST_TICK_CONTROL_HANDOFF"
    assert mgr.control_request_pending is True


def test_stop_flow_handoff_consume_terminate(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    mgr.request_control(ControlRequest.STOP)
    res = mgr.heartbeat_tick()  # handoff → CONTROL_PENDING
    assert res.payload["handoff_action"] == "CONSUME_CONTROL"
    assert mgr.runtime_state is HeartbeatRuntimeState.CONTROL_PENDING
    assert mgr.consume_control().ok
    assert mgr.runtime_state is HeartbeatRuntimeState.STOPPING
    res = mgr.commit_termination()
    assert res.ok
    assert mgr.terminal_event is True
    assert mgr.periodic_loop_terminated is True
    # le lock JSON n'est jamais supprimé par la terminaison
    assert (tmp_path / "session.lock.json").exists()


def test_termination_drain_refused_outside_stopping_aborting(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    res = mgr.commit_termination()  # ACTIVE_WAITING → refus
    assert res.code is FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID
    assert mgr.termination_committed is False
    assert mgr.terminal_event is False


def test_fault_on_lock_identity_mismatch_preserves_first_fault(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    lock = tmp_path / "session.lock.json"
    lock.write_bytes(b'{"tampered": true}')
    res = mgr.heartbeat_tick()
    assert res.code is FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT
    assert mgr.runtime_state is HeartbeatRuntimeState.FAULTED
    assert mgr.termination_reason == "POST_ACTIVATION_HEARTBEAT_FAULT"
    assert "HEARTBEAT_LOCK_IDENTITY_MISMATCH" in mgr.runtime_fault
    # faute : jamais de suppression du lock, Level 3 intact
    assert lock.exists()
    assert mgr.session_level3_owned is True
    assert mgr.session_target_handle_resource is not None


# ── classification : stale / futur / absent / corrompu / incomplet ──────────

def test_stale_candidate_detection_no_mutation(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    before = (tmp_path / "session.lock.json").read_bytes()
    clock.advance(100)  # > 2 × interval
    cls = mgr.classify_lock()
    assert cls.payload["classification"] == LockClassification.STALE_CANDIDATE.value
    assert (tmp_path / "session.lock.json").read_bytes() == before


def test_future_timestamp_without_skew_param_fails_closed(tmp_path):
    clock = FakeClock(start=1000.0)
    mgr = make_manager(tmp_path, clock, **ENABLED)  # skew ABSENT
    lock = tmp_path / "session.lock.json"
    lock.write_text(json.dumps({
        "session_id": "x", "lock_version": "V2",
        "created_at": 900.0, "heartbeat_at": 5000.0}), encoding="utf-8")
    res = mgr.classify_lock()
    assert res.ok is False and res.fail_closed is True
    assert res.payload["classification"] == \
        LockClassification.UNCLASSIFIABLE_FAIL_CLOSED.value


def test_future_timestamp_beyond_skew_classified(tmp_path):
    clock = FakeClock(start=1000.0)
    # skew=5.0 : fixture de test locale, pas une valeur de production
    mgr = make_manager(tmp_path, clock, **ENABLED,
                       max_v2_future_clock_skew_seconds=5.0)
    lock = tmp_path / "session.lock.json"
    lock.write_text(json.dumps({
        "session_id": "x", "lock_version": "V2",
        "created_at": 900.0, "heartbeat_at": 1050.0}), encoding="utf-8")
    res = mgr.classify_lock()
    assert res.payload["classification"] == \
        LockClassification.FUTURE_TIMESTAMP_BEYOND_SKEW.value


def test_absent_incomplete_corrupted(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    assert mgr.classify_lock().payload["classification"] == \
        LockClassification.ABSENT.value
    lock = tmp_path / "session.lock.json"
    lock.write_bytes(b"\xff\xfenot-json")
    assert mgr.classify_lock().payload["classification"] == \
        LockClassification.CORRUPTED.value
    lock.write_text(json.dumps({"session_id": "x"}), encoding="utf-8")
    assert mgr.classify_lock().payload["classification"] == \
        LockClassification.INCOMPLETE.value


# ── SECTION_13 : release ─────────────────────────────────────────────────────

def test_release_full_transaction_released(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    res = mgr.release_session()
    assert res.ok and res.detail == "RELEASED"
    assert mgr.session_release_state == "RELEASED"
    assert mgr.session_release_completed is True
    # postconditions PART_H
    assert mgr.level1_locked is False and mgr.level2_locked is False
    assert mgr.session_level3_owned is False
    assert mgr.session_target_handle_resource is None
    assert not (tmp_path / "session.lock.json").exists()


def test_release_entry_guard_invalid_state(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    mgr.runtime_state = HeartbeatRuntimeState.NOT_STARTED
    res = mgr.release_session()
    assert res.code is FailureCode.RELEASE_SESSION_STATE_INVALID
    assert (tmp_path / "session.lock.json").exists()
    assert mgr.session_level3_owned is True


def test_release_lock_state_mismatch_no_deletion(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    lock = tmp_path / "session.lock.json"
    tampered = b'{"replaced": true}'
    lock.write_bytes(tampered)
    res = mgr.release_session()
    assert res.code is FailureCode.RELEASE_LOCK_STATE_MISMATCH
    assert res.human_recovery_required is True
    # aucune suppression, Level 3 non libéré, handle non fermé
    assert lock.read_bytes() == tampered
    assert mgr.session_level3_owned is True
    assert mgr.session_target_handle_resource is not None
    # verrous d'arbitrage relâchés malgré la faute (exception_safety)
    assert mgr.level1_locked is False and mgr.level2_locked is False


# ── SECTION_14 : reclaim — porte d'autorisation et interdiction réelle ───────

def _valid_proof(clock: FakeClock, session_id: str = "sess-t1") -> dict:
    return {
        "approval_id": "APR-1",
        "repository_path_hash": "deadbeef",
        "orphan_session_id": session_id,
        "authorized_reason": "test fixture",
        "issued_at": clock.now - 10,
        "expires_at": clock.now + 100,
    }


def test_reclaim_blocked_without_gf_r01(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED)  # GF_R01 ABSENT
    mgr.acquire_session_lock()
    res = mgr.prepare_reclaim_proposal(_valid_proof(clock))
    assert res.ok is False
    assert res.code is FailureCode.RECLAIM_AUTHORIZATION_INVALID
    assert "GF_R01" in res.detail
    assert (tmp_path / "session.lock.json").exists()


def test_reclaim_v2_blocked_without_skew(tmp_path):
    clock = FakeClock()
    mgr = make_manager(tmp_path, clock, **ENABLED,
                       human_approved_corrected_gf_r01_sha256="ab" * 32)
    mgr.acquire_session_lock()
    res = mgr.prepare_reclaim_proposal(_valid_proof(clock))
    assert res.code is FailureCode.RECLAIM_AUTHORIZATION_INVALID
    assert "MAX_V2_FUTURE_CLOCK_SKEW_SECONDS" in res.detail


def test_reclaim_proposal_prepared_but_real_execution_impossible(tmp_path):
    clock = FakeClock()
    mgr = make_manager(
        tmp_path, clock, **ENABLED,
        human_approved_corrected_gf_r01_sha256="ab" * 32,
        max_v2_future_clock_skew_seconds=5.0)
    mgr.acquire_session_lock()
    lock = tmp_path / "session.lock.json"
    before = lock.read_bytes()
    res = mgr.prepare_reclaim_proposal(_valid_proof(clock))
    assert res.ok is True
    assert res.payload["proposal"]["real_execution_authorized"] is False
    # la préparation n'a RIEN muté
    assert lock.read_bytes() == before
    # l'exécution réelle est structurellement refusée, quels que soient
    # les arguments
    exe = mgr.execute_reclaim(res.payload["proposal"])
    assert exe.ok is False
    assert exe.code is FailureCode.RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED
    assert lock.read_bytes() == before


def test_reclaim_proof_session_mismatch(tmp_path):
    clock = FakeClock()
    mgr = make_manager(
        tmp_path, clock, **ENABLED,
        human_approved_corrected_gf_r01_sha256="ab" * 32,
        max_v2_future_clock_skew_seconds=5.0)
    mgr.acquire_session_lock()
    proof = _valid_proof(clock, session_id="other-session")
    res = mgr.prepare_reclaim_proposal(proof)
    assert res.code is FailureCode.RECLAIM_LOCK_STATE_MISMATCH


# ── déterminisme et absence de mutation hors périmètre ──────────────────────

def test_determinism_same_inputs_same_results(tmp_path):
    def run(run_id: str) -> list:
        clock = FakeClock()
        d = tmp_path / f"run_{run_id}"
        d.mkdir()
        mgr = HeartbeatLockManager(
            HeartbeatConfig(**ENABLED), d / "l.json", "sess-t1", clock=clock)
        out = [mgr.acquire_session_lock()]
        clock.advance(3)
        out.append(mgr.heartbeat_tick())
        out.append(mgr.classify_lock())
        clock.advance(100)
        out.append(mgr.classify_lock())
        return [(r.ok, r.code, r.detail, r.payload) for r in out]

    first, second = run("a"), run("b")
    assert first == second


def test_no_mutation_outside_lock_path(tmp_path):
    clock = FakeClock()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("untouched", encoding="utf-8")
    mgr = make_manager(tmp_path, clock, **ENABLED)
    mgr.acquire_session_lock()
    clock.advance(3)
    mgr.heartbeat_tick()
    mgr.classify_lock()
    mgr.prepare_reclaim_proposal()
    mgr.execute_reclaim()
    mgr.release_session()
    assert sentinel.read_text(encoding="utf-8") == "untouched"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["sentinel.txt"]
