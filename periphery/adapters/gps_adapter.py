from __future__ import annotations

from periphery.common import ActionCandidate
from sigma.contracts import GpsDefenseAviationState

DEFAULT_GPS_STATE = {
    "mission_id": "DEMO-MISSION",
    "flight_id": "DEMO-FLIGHT",
    "altitude": 1000.0,
    "ground_speed": 220.0,
    "gps_status": "ONLINE",
    "satellites_count": 8,
    "signal_noise_ratio": 0.95,
    "gps_available": True,
    "inertial_available": True,
    "radio_available": True,
    "trajectory_drift_score": 0.0,
    "source_conflict_score": 0.0,
    "time_skew_score": 0.0,
    "brownout_score": 0.0,
    "attestation_ready": True,
    "rollback_possible": True,
}

def build_gps_action(payload: dict) -> ActionCandidate:
    return ActionCandidate(
        action_id=payload.get("action_id", "gps-action"),
        domain="gps_defense_aviation",
        actor_id=payload.get("actor_id", "gps-agent"),
        intent=payload.get("intent", "trajectory_integrity_review"),
        action_type=payload.get("action_type", "trajectory_decision"),
        irreversible=bool(payload.get("irreversible", True)),
        timestamp_plan=payload.get("timestamp_plan", ""),
        timestamp_exec=payload.get("timestamp_exec"),
        payload=payload,
    )

def build_gps_state(payload: dict) -> GpsDefenseAviationState:
    data = dict(DEFAULT_GPS_STATE)
    for k, v in payload.items():
        if k in data:
            data[k] = v
    return GpsDefenseAviationState(**data)
