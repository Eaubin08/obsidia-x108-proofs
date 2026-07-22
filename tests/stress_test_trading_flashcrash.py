#!/usr/bin/env python3
from _thermo_domain_stress_lib import cli_run

CONFIG = {
    "domain": "TRADING",
    "scenario": "FLASH_CRASH_CONTRADICTORY_MARKET_SIGNALS",
    "target_n": 500000,
    "batch_size": 10000,
    "energy_budget": 5000.0,
    "verdict": "HOLD_STABILITY_ALERT",
    "banner": "TRADING FLASH CRASH — THERMODYNAMIC RUPTURE TEST",
    "closing": "MARKET GATE HELD: no order emitted, kernel protected.",
    "exp_factor": 0.18,
    "heat_factor": 10.0,
    "sleep_s": 0.04,
}

if __name__ == "__main__":
    raise SystemExit(cli_run(CONFIG))
