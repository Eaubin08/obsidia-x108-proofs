#!/usr/bin/env python3
from _thermo_domain_stress_lib import cli_run

CONFIG = {
    "domain": "BANK",
    "scenario": "DDOS_MICRO_TX_FRAUD_UNKNOWN_COUNTERPARTIES",
    "target_n": 1000000,
    "batch_size": 25000,
    "energy_budget": 5000.0,
    "verdict": "BLOCK_FRAUD",
    "banner": "BANK DDOS / FRAUD FLOOD — THERMODYNAMIC FIREWALL TEST",
    "closing": "MUR DE BETON: Kernel X-108 non mute. Money flow blocked.",
    "exp_factor": 0.17,
    "heat_factor": 11.0,
    "sleep_s": 0.04,
}

if __name__ == "__main__":
    raise SystemExit(cli_run(CONFIG))
