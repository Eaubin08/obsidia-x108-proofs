#!/usr/bin/env python3
from _thermo_domain_stress_lib import cli_run

CONFIG = {
    "domain": "GPS_AVIATION",
    "scenario": "GPS_INERTIAL_RADIO_SPOOFING_TIME_SKEW",
    "target_n": 200000,
    "batch_size": 5000,
    "energy_budget": 5000.0,
    "verdict": "ABORT_TRAJECTORY",
    "banner": "GPS / AVIATION SPOOFING — RADAR THERMO HOLD TEST",
    "closing": "NO PHYSICAL TRAJECTORY CHANGE SENT: emits_act=False.",
    "exp_factor": 0.19,
    "heat_factor": 12.0,
    "sleep_s": 0.04,
}

if __name__ == "__main__":
    raise SystemExit(cli_run(CONFIG))
