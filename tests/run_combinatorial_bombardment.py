#!/usr/bin/env python3
"""
tests/run_combinatorial_bombardment.py

LABORATOIRE COMBINATOIRE — Bombardement logique du Guard X-108.

Invariants:
- decision_authority = KX108_ONLY
- emits_act = False
- kernel_mutation = False
- memory_write = False

Mode:
- Test terminal local.
- Charge les vecteurs du Combinatorial Coverage Layer si disponible.
- Sinon fallback sur vecteurs critiques hardcodés.
- Applique BLOCK > HOLD > ALLOW.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMBI = ROOT / "combinatorial_coverage_layer"

if str(COMBI) not in sys.path:
    sys.path.insert(0, str(COMBI))


DECISION_AUTHORITY = "KX108_ONLY"
EMITS_ACT = False
ALLOWED_TO_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False


def guard_x108_decide(payload: dict[str, Any]) -> tuple[str, str]:
    """
    Loi souveraine locale:
    BLOCK > HOLD > ALLOW.
    """
    risk = float(payload.get("risk_score", 0.0))
    confidence = float(payload.get("confidence_index", 1.0))
    contradiction = bool(payload.get("contradiction_flag", False))
    unknown = bool(payload.get("unknown_counterparty", False))
    temporal_skew = float(payload.get("temporal_skew", 0.0))

    # 1. BLOCK prioritaire
    if contradiction and risk > 0.5:
        return "BLOCK", f"Contradiction critique + risk_score={risk}."

    if risk > 1.0 and contradiction:
        return "BLOCK", f"Risk hors borne + contradiction: risk_score={risk}."

    # 2. HOLD temporel / incertitude
    if temporal_skew > 0.5:
        return "HOLD", f"Temporal skew critique: temporal_skew={temporal_skew}."

    if unknown:
        return "HOLD", "Contrepartie inconnue: unknown_counterparty=True."

    if confidence < 0.45:
        return "HOLD", f"Confiance sous seuil: confidence_index={confidence}."

    if contradiction:
        return "HOLD", "Contradiction mineure: audit requis."

    # 3. ALLOW seulement si structure propre
    return "ALLOW", "Structure stable: aucun verrou critique."


def load_vectors_from_generator() -> list[dict[str, Any]]:
    """
    Charge les scénarios générés par combinatorial_coverage_layer/boundary_case_generator.py.
    Sélectionne les plus agressifs + quelques cas baselines.
    """
    try:
        from boundary_case_generator import CombinatorialMatrix
    except Exception as exc:
        print(f"[WARN] Generator import failed: {exc}")
        return []

    vectors: list[dict[str, Any]] = []

    for domain in ["BANK", "TRADING", "GPS_AVIATION"]:
        matrix = CombinatorialMatrix(domain).generate_matrix()

        # Top bruit
        top = sorted(matrix, key=lambda s: s.injected_noise_level, reverse=True)[:6]

        # Baseline low noise
        low = sorted(matrix, key=lambda s: s.injected_noise_level)[:2]

        for scenario in top + low:
            vectors.append(
                {
                    "id": scenario.scenario_id,
                    "domain": scenario.domain,
                    "noise": scenario.injected_noise_level,
                    "payload": scenario.parameters,
                }
            )

    return vectors


def fallback_vectors() -> list[dict[str, Any]]:
    return [
        {
            "id": "BND_TRADING_0002",
            "domain": "TRADING",
            "noise": 2.26,
            "payload": {
                "risk_score": 0.01,
                "confidence_index": 0.1,
                "contradiction_flag": True,
                "unknown_counterparty": True,
                "temporal_skew": 1.0,
            },
        },
        {
            "id": "BND_TRADING_0009",
            "domain": "TRADING",
            "noise": 0.01,
            "payload": {
                "risk_score": 0.01,
                "confidence_index": 0.9,
                "contradiction_flag": False,
                "unknown_counterparty": False,
                "temporal_skew": 0.0,
            },
        },
        {
            "id": "BND_GPS_AVIATION_0007",
            "domain": "GPS_AVIATION",
            "noise": 0.76,
            "payload": {
                "risk_score": 0.01,
                "confidence_index": 0.1,
                "contradiction_flag": False,
                "unknown_counterparty": True,
                "temporal_skew": 0.25,
            },
        },
        {
            "id": "BND_GPS_AVIATION_0008",
            "domain": "GPS_AVIATION",
            "noise": 1.51,
            "payload": {
                "risk_score": 0.01,
                "confidence_index": 0.1,
                "contradiction_flag": False,
                "unknown_counterparty": True,
                "temporal_skew": 1.0,
            },
        },
        {
            "id": "BND_BANK_FRAUD_MAX",
            "domain": "BANK",
            "noise": 3.25,
            "payload": {
                "risk_score": 1.5,
                "confidence_index": 0.1,
                "contradiction_flag": True,
                "unknown_counterparty": True,
                "temporal_skew": 1.0,
            },
        },
    ]


def run_bombardment() -> dict[str, Any]:
    vectors = load_vectors_from_generator()

    if not vectors:
        print("[WARN] Using fallback vectors.")
        vectors = fallback_vectors()

    print("=" * 72)
    print("COMBINATORIAL BOMBARDMENT — X-108 LOCAL GUARD TEST")
    print("=" * 72)
    print(f"vectors_loaded={len(vectors)}")
    print(f"decision_authority={DECISION_AUTHORITY}")
    print(f"emits_act={EMITS_ACT}")
    print(f"allowed_to_act={ALLOWED_TO_ACT}")
    print(f"kernel_mutation={KERNEL_MUTATION}")
    print("rule=BLOCK > HOLD > ALLOW")
    print("")

    counts = {"ALLOW": 0, "HOLD": 0, "BLOCK": 0}
    receipts = []

    for v in vectors:
        decision, reason = guard_x108_decide(v["payload"])
        counts[decision] += 1

        if decision == "BLOCK":
            marker = "MUR_DE_BETON"
        elif decision == "HOLD":
            marker = "VERROU_TEMPOREL"
        else:
            marker = "ALLOW_SAFE"

        print(
            f"[{marker}] id={v['id']} domain={v['domain']} "
            f"noise={v['noise']} -> {decision} | {reason}"
        )

        receipts.append(
            {
                "id": v["id"],
                "domain": v["domain"],
                "noise": v["noise"],
                "payload": v["payload"],
                "decision": decision,
                "reason": reason,
                "decision_authority": DECISION_AUTHORITY,
                "emits_act": EMITS_ACT,
                "allowed_to_act": ALLOWED_TO_ACT,
                "kernel_mutation": KERNEL_MUTATION,
            }
        )

    print("")
    print("=" * 72)
    print("FINAL BOMBARDMENT REPORT")
    print("=" * 72)
    print(f"ALLOW={counts['ALLOW']}")
    print(f"HOLD={counts['HOLD']}")
    print(f"BLOCK={counts['BLOCK']}")
    print("decision_authority=KX108_ONLY")
    print("emits_act=False")
    print("allowed_to_act=False")
    print("kernel_mutation=False")
    print("=" * 72)

    return {
        "test": "COMBINATORIAL_BOMBARDMENT_X108_LOCAL_GUARD",
        "vectors_loaded": len(vectors),
        "counts": counts,
        "receipts": receipts,
        "readonly": True,
        "decision_authority": DECISION_AUTHORITY,
        "emits_act": EMITS_ACT,
        "allowed_to_act": ALLOWED_TO_ACT,
        "kernel_mutation": KERNEL_MUTATION,
        "memory_write": MEMORY_WRITE,
        "graphiti_write": GRAPHITI_WRITE,
        "neo4j_write": NEO4J_WRITE,
    }


def main() -> int:
    report = run_bombardment()

    out = ROOT / "tests" / "run_combinatorial_bombardment_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("")
    print(f"report_written={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
