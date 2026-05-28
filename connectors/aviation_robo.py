from __future__ import annotations

import os
import random
import time
from typing import Any

import requests


DEFAULT_API_BASE = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")
GPS_ENDPOINT = "/api/periphery/monitoring/adapters/gps"


def build_gps_payload() -> dict[str, Any]:
    return {
        "payload": {
            "action_id": "aviation-robo-flow",
            "actor_id": "aviation-connector",
            "intent": "trajectory_integrity_review",
            "action_type": "trajectory_decision",
            "irreversible": True,
            "mission_id": "F23A48",
            "flight_id": f"AF{random.randint(100, 999)}",
            "altitude": random.randint(30000, 35000),
            "ground_speed": random.randint(400, 500),
            "gps_status": "ONLINE",
            "satellites_count": random.randint(8, 12),
            "signal_noise_ratio": round(random.uniform(0.80, 0.98), 2),
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
    }


def send_gps_payload(api_base: str = DEFAULT_API_BASE, timeout: int = 10):
    url = f"{api_base.rstrip('/')}{GPS_ENDPOINT}"
    return requests.post(url, json=build_gps_payload(), timeout=timeout)


def run_flight_flow(api_base: str = DEFAULT_API_BASE):
    print(f"✈️ [OBSIDIA-AVIONICS] Flux GPS Defense vers {api_base}{GPS_ENDPOINT}")

    while True:
        try:
            res = send_gps_payload(api_base=api_base, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", res.json())
                env = data.get("domain_sigma_envelope", {})
                print(
                    "✅ [AERO] Sigma envelope | "
                    f"domain={env.get('domain')} gate={env.get('x108_gate')} "
                    f"authority={env.get('decision_authority')} emits_act={env.get('emits_act')}"
                )
            else:
                print(f"⚠️ [AERO] API error: {res.status_code} {res.text[:250]}")
        except Exception as e:
            print(f"❌ [AERO] Connection error: {e}")

        time.sleep(4)


if __name__ == "__main__":
    run_flight_flow()
