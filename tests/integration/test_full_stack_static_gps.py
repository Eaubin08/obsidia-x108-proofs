from sigma.contracts import GpsDefenseAviationState

from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_gps_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def test_gps_static_full_stack_is_bounded():
    action = ActionCandidate(
        action_id="static_gps_001",
        domain="gps_defense_aviation",
        actor_id="integration_test",
        intent="route_review",
        action_type="navigation",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "gross_value": 10.0,
        },
    )

    state = GpsDefenseAviationState(
        mission_id="STATIC_MISSION_001",
        flight_id="STATIC_FLIGHT_001",
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

    packet = run_control_plane(action)
    assert packet.can_emit_act is False

    envelope = run_gps_with_periphery(
        state,
        packet,
    )
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(
        action,
        packet,
        envelope,
    )
    assert ticket.input_hash
    assert ticket.trace_hash

    gencoin = compute_gencoin(
        action,
        packet,
        ticket,
    )

    replay = run_replay(
        ticket,
        action,
        packet,
        envelope,
    )
    assert replay.replay_status == "PASS"

    world = run_world_action_stub(
        action,
        ticket,
        gencoin.gencoin_candidate,
    )
    assert world.dry_run_only is True
    assert world.world_action_allowed is False

    memory = build_memory_candidate(
        ticket,
        packet,
        action,
    )
    assert memory.memory_write_allowed is False
