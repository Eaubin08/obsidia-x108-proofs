import pytest
from sigma.contracts import GpsDefenseAviationState
from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_gps_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def _make_gps_action():
    return ActionCandidate(
        action_id="gps_v3_int_001",
        domain="gps_defense_aviation",
        actor_id="nav_system",
        intent="route_update",
        action_type="navigation",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 10.0},
    )


def _make_gps_state():
    return GpsDefenseAviationState(
        mission_id="MISSION_001",
        flight_id="FLIGHT_007",
        altitude=10000.0,
        ground_speed=850.0,
        gps_status="ACTIVE",
        satellites_count=8,
        signal_noise_ratio=42.0,
        gps_available=True,
        inertial_available=True,
        radio_available=True,
        trajectory_drift_score=0.05,
    )


def test_gps_v3_full_pipeline():
    action = _make_gps_action()
    state = _make_gps_state()

    packet = run_control_plane(action)
    assert not packet.can_emit_act

    envelope = run_gps_with_periphery(state, packet)
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(action, packet, envelope)
    assert ticket.input_hash and ticket.trace_hash

    gc = compute_gencoin(action, packet, ticket)

    replay = run_replay(ticket, action, packet, envelope)
    assert replay.replay_status == "PASS"

    wa = run_world_action_stub(action, ticket, gc.gencoin_candidate)
    assert wa.world_action_allowed is False

    mem = build_memory_candidate(ticket, packet, action)
    assert mem.memory_write_allowed is False

    assert "GPS_V3_FULL_STACK_PASS" == "GPS_V3_FULL_STACK_PASS"
