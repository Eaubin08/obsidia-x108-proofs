#!/usr/bin/env python3
"""
tests/run_combinatorial_ecom.py
LOCAL SIMULATION ONLY — ECOM / DEFENSE boundary stress.
Does not call Kernel 3001 or API 8000.
"""

import json
import math
from pathlib import Path

DECISION_AUTHORITY = "KX108_ONLY"
EMITS_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
ENERGY_BUDGET_MAX = 5000.0

def guard_x108_decide(payload):
    risk = float(payload.get("risk_score", 0.0))
    confidence = float(payload.get("confidence_index", 1.0))
    contradiction = bool(payload.get("contradiction_flag", False))
    temporal_skew = float(payload.get("temporal_skew", 0.0))

    if contradiction and risk > 0.8:
        return "BLOCK", f"Critical contradiction + high risk ({risk})."

    if temporal_skew > 0.5 or confidence < 0.45:
        return "HOLD", f"Temporal skew or low confidence (skew={temporal_skew}, confidence={confidence})."

    return "ALLOW", "Nominal local transaction."

def main():
    vectors = [
        {
            "id": "BND_ECOM_001",
            "desc": "Botnet temporal skew",
            "payload": {
                "risk_score": 0.4,
                "confidence_index": 0.2,
                "contradiction_flag": False,
                "temporal_skew": 0.9,
            },
        },
        {
            "id": "BND_ECOM_002",
            "desc": "Contradictory cart / double spend",
            "payload": {
                "risk_score": 0.95,
                "confidence_index": 0.8,
                "contradiction_flag": True,
                "temporal_skew": 0.1,
            },
        },
        {
            "id": "BND_DEFENSE_001",
            "desc": "Telemetry jamming",
            "payload": {
                "risk_score": 0.99,
                "confidence_index": 0.1,
                "contradiction_flag": True,
                "temporal_skew": 1.5,
            },
        },
        {
            "id": "BND_ECOM_003",
            "desc": "Verified purchase baseline",
            "payload": {
                "risk_score": 0.05,
                "confidence_index": 0.95,
                "contradiction_flag": False,
                "temporal_skew": 0.0,
            },
        },
    ]

    current_energy = 0.0
    results = []

    print("=" * 72)
    print("LOCAL COMBINATORIAL BOMBARDMENT — ECOM / DEFENSE")
    print(f"decision_authority={DECISION_AUTHORITY}")
    print(f"emits_act={EMITS_ACT}")
    print(f"kernel_mutation={KERNEL_MUTATION}")
    print("mode=LOCAL_SIMULATION_ONLY")
    print("=" * 72)

    for v in vectors:
        heat = math.exp(v["payload"]["risk_score"] * 3)
        current_energy += heat

        if current_energy > ENERGY_BUDGET_MAX:
            decision, reason = "HOLD", "Forced HOLD by local thermodynamic budget."
        else:
            decision, reason = guard_x108_decide(v["payload"])

        row = {
            "id": v["id"],
            "desc": v["desc"],
            "decision": decision,
            "reason": reason,
            "heat": round(heat, 6),
            "energy_total": round(current_energy, 6),
            "decision_authority": DECISION_AUTHORITY,
            "emits_act": EMITS_ACT,
            "kernel_mutation": KERNEL_MUTATION,
            "mode": "LOCAL_SIMULATION_ONLY",
        }
        results.append(row)

        print(f"{v['id']} | {v['desc']} -> {decision} | {reason}")

    out = Path("tests/run_combinatorial_ecom_report.json")
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=" * 72)
    print(f"report_written={out.resolve()}")

if __name__ == "__main__":
    main()
