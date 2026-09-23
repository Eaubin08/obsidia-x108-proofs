#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
import time
from dataclasses import dataclass, asdict


DECISION_AUTHORITY = "KX108_ONLY"
EMITS_ACT = False
ALLOWED_TO_ACT = False
ALLOWED_TO_DECIDE = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False


@dataclass
class Receipt:
    domain: str
    scenario: str
    processed: int
    energy: float
    dE_dt: float
    ffs: float
    state: str
    market_verdict: str
    severity: str
    sigma_override: bool
    reason: str
    decision_authority: str = DECISION_AUTHORITY
    emits_act: bool = EMITS_ACT
    allowed_to_act: bool = ALLOWED_TO_ACT
    allowed_to_decide: bool = ALLOWED_TO_DECIDE
    kernel_mutation: bool = KERNEL_MUTATION
    memory_write: bool = MEMORY_WRITE
    graphiti_write: bool = GRAPHITI_WRITE
    neo4j_write: bool = NEO4J_WRITE


def signal(domain: str, i: int) -> dict:
    r = random.random()

    if domain == "TRADING":
        return {
            "contradiction": abs(math.sin(i * 0.041)),
            "volatility": abs(math.cos(i * 0.029)),
            "unknown": 1.0 if i % 17 == 0 else 0.15,
            "irreversible": 0.85 if i % 23 == 0 else 0.25,
            "noise": r,
        }

    if domain == "GPS_AVIATION":
        return {
            "contradiction": abs(math.sin(i * 0.037)),
            "volatility": abs(math.cos(i * 0.021)),
            "unknown": 1.0 if i % 19 == 0 else 0.30,
            "irreversible": 0.95 if i % 29 == 0 else 0.40,
            "noise": r,
        }

    return {
        "contradiction": abs(math.cos(i * 0.033)),
        "volatility": abs(math.sin(i * 0.019)),
        "unknown": 1.0 if i % 13 == 0 else 0.35,
        "irreversible": 0.90 if i % 11 == 0 or i % 37 == 0 else 0.35,
        "noise": r,
    }


def signal_energy(s: dict, step: int, exp_factor: float, heat_factor: float) -> float:
    base = 0.0
    base += s["contradiction"] * 14.0
    base += s["volatility"] * 11.0
    base += s["unknown"] * 12.0
    base += s["irreversible"] * 18.0
    base += s["noise"] * 3.0

    thermo = math.exp(step * exp_factor) * heat_factor
    return base + thermo


def ffs_score(contradiction_pressure: float, energy_total: float, dE_dt: float, budget: float, processed: int, target: int) -> float:
    convergence = max(0.0, 1.0 - contradiction_pressure)
    throughput = min(1.0, processed / max(target, 1))
    heat_penalty = min(1.0, dE_dt / max(budget * 20.0, 1.0))
    saturation_penalty = min(1.0, energy_total / max(budget * 6.0, 1.0))

    ffs = (0.55 * convergence) + (0.20 * throughput) - (0.45 * heat_penalty) - (0.35 * saturation_penalty)
    return max(0.0, min(1.0, ffs))


def run_domain_stress(
    domain: str,
    scenario: str,
    verdict: str,
    banner: str,
    closing: str,
    target_n: int,
    batch_size: int,
    energy_budget: float,
    exp_factor: float,
    heat_factor: float,
    max_seconds: float,
    seed: int,
    sleep_s: float,
) -> Receipt:
    random.seed(seed)

    print("=" * 72)
    print(banner)
    print("=" * 72)
    print(f"DOMAIN={domain}")
    print(f"SCENARIO={scenario}")
    print(f"target_n={target_n}")
    print(f"batch={batch_size}")
    print(f"decision_authority={DECISION_AUTHORITY}")
    print(f"emits_act={EMITS_ACT}")
    print(f"kernel_mutation={KERNEL_MUTATION}")
    print("")

    started = time.perf_counter()
    last_t = started
    total_energy = 0.0
    processed = 0
    step = 0

    while processed < target_n:
        step += 1
        batch_energy = 0.0
        contradiction_sum = 0.0
        local_count = 0

        for _ in range(batch_size):
            if processed >= target_n:
                break

            sig = signal(domain, processed)
            batch_energy += signal_energy(sig, step, exp_factor, heat_factor)
            contradiction_sum += (sig["contradiction"] + sig["unknown"] + sig["irreversible"]) / 3.0
            processed += 1
            local_count += 1

        now = time.perf_counter()
        dt = max(now - last_t, 1e-9)

        # Normalisation volontaire : on simule la chauffe du batch, pas le coût brut de chaque item.
        normalized_batch_heat = batch_energy / max(local_count, 1)
        total_energy += normalized_batch_heat

        dE_dt = normalized_batch_heat / dt
        contradiction_pressure = contradiction_sum / max(local_count, 1)
        ffs = ffs_score(contradiction_pressure, total_energy, dE_dt, energy_budget, processed, target_n)

        if ffs < 0.22:
            state = "STERILE"
        elif contradiction_pressure > 0.70:
            state = "NOISY"
        else:
            state = "FERTILE"

        print(
            f"[{domain}] step={step:04d} processed={processed:08d} "
            f"E={total_energy:010.2f} dE/dt={dE_dt:010.2f} "
            f"FFS={ffs:.4f} state={state}"
        )

        if total_energy > energy_budget or state in ("STERILE", "NOISY"):
            reason = f"Thermodynamic rupture: E={total_energy:.2f}, dE/dt={dE_dt:.2f}, FFS={ffs:.4f}, state={state}"

            print("")
            print("=" * 72)
            print("LOOPBREAKER TRIGGERED")
            print("=" * 72)
            print(f"[SIGMA] market_verdict={verdict}")
            print("[SIGMA] severity=S4")
            print("[SIGMA] sigma_override=True")
            print("[THERMO] FFS collapsed into STERILE/NOISY")
            print("[BOUNDARY] decision_authority=KX108_ONLY")
            print("[BOUNDARY] emits_act=False")
            print("[BOUNDARY] allowed_to_act=False")
            print("[BOUNDARY] kernel_mutation=False")
            print(closing)
            print("=" * 72)

            return Receipt(
                domain=domain,
                scenario=scenario,
                processed=processed,
                energy=round(total_energy, 6),
                dE_dt=round(dE_dt, 6),
                ffs=round(ffs, 6),
                state=state,
                market_verdict=verdict,
                severity="S4",
                sigma_override=True,
                reason=reason,
            )

        if now - started >= max_seconds:
            print("")
            print("=" * 72)
            print("TIME BUDGET HOLD")
            print("=" * 72)
            print("[SIGMA] market_verdict=HOLD_STABILITY_ALERT")
            print("[SIGMA] severity=S3")
            print("[SIGMA] sigma_override=True")
            print("[BOUNDARY] emits_act=False")
            print("[BOUNDARY] decision_authority=KX108_ONLY")
            print("=" * 72)

            return Receipt(
                domain=domain,
                scenario=scenario,
                processed=processed,
                energy=round(total_energy, 6),
                dE_dt=round(dE_dt, 6),
                ffs=round(ffs, 6),
                state="TIME_BUDGET_HOLD",
                market_verdict="HOLD_STABILITY_ALERT",
                severity="S3",
                sigma_override=True,
                reason="Time budget reached before completion.",
            )

        last_t = now
        time.sleep(sleep_s)

    return Receipt(
        domain=domain,
        scenario=scenario,
        processed=processed,
        energy=round(total_energy, 6),
        dE_dt=0.0,
        ffs=1.0,
        state="COMPLETED_WITHOUT_BREAK",
        market_verdict="NO_ALERT",
        severity="S0",
        sigma_override=False,
        reason="Completed without thermodynamic rupture.",
    )


def cli_run(config: dict) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=config["target_n"])
    parser.add_argument("--batch", type=int, default=config["batch_size"])
    parser.add_argument("--max-seconds", type=float, default=12.0)
    parser.add_argument("--seed", type=int, default=108)
    args = parser.parse_args()

    receipt = run_domain_stress(
        domain=config["domain"],
        scenario=config["scenario"],
        verdict=config["verdict"],
        banner=config["banner"],
        closing=config["closing"],
        target_n=args.n,
        batch_size=args.batch,
        energy_budget=config["energy_budget"],
        exp_factor=config["exp_factor"],
        heat_factor=config["heat_factor"],
        max_seconds=args.max_seconds,
        seed=args.seed,
        sleep_s=config["sleep_s"],
    )

    print("")
    print("FINAL_RECEIPT")
    for key, value in asdict(receipt).items():
        print(f"{key}={value}")

    return 0
