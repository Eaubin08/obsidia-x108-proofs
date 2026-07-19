#!/usr/bin/env python3
"""
combinatorial_coverage_layer/boundary_case_generator.py

COMBINATORIAL COVERAGE LAYER — Générateur de matrices de stress.

Invariants:
- decision_authority = KX108_ONLY
- emits_verdict = False
- emits_act = False
- kernel_mutation = False
- memory_write = False

Role:
- Générer des scénarios limites.
- Ne pas les injecter automatiquement.
- Ne pas décider.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, asdict
from typing import Any


DECISION_AUTHORITY = "KX108_ONLY"
EMITS_VERDICT = False
EMITS_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False


@dataclass(frozen=True)
class BoundaryScenario:
    domain: str
    scenario_id: str
    injected_noise_level: float
    parameters: dict[str, Any]
    decision_authority: str = DECISION_AUTHORITY
    emits_verdict: bool = EMITS_VERDICT
    emits_act: bool = EMITS_ACT
    kernel_mutation: bool = KERNEL_MUTATION
    memory_write: bool = MEMORY_WRITE


class CombinatorialMatrix:
    """Génère des permutations extrêmes readonly pour stress tests contrôlés."""

    def __init__(self, domain: str):
        self.domain = domain.upper()

        self.vectors: dict[str, list[Any]] = {
            "risk_score": [0.01, 0.5, 0.99, 1.5],
            "confidence_index": [0.1, 0.9],
            "contradiction_flag": [True, False],
            "unknown_counterparty": [True, False],
            "temporal_skew": [0.0, 0.25, 1.0],
        }

    def generate_matrix(self) -> list[BoundaryScenario]:
        keys = list(self.vectors.keys())
        combinations = itertools.product(*(self.vectors[k] for k in keys))

        scenarios: list[BoundaryScenario] = []

        for idx, combo in enumerate(combinations):
            params = dict(zip(keys, combo))

            noise = float(params["risk_score"])
            if params["contradiction_flag"]:
                noise += 0.75
            if params["unknown_counterparty"]:
                noise += 0.50
            noise += float(params["temporal_skew"])

            scenarios.append(
                BoundaryScenario(
                    domain=self.domain,
                    scenario_id=f"BND_{self.domain}_{idx:04d}",
                    injected_noise_level=round(noise, 6),
                    parameters=params,
                )
            )

        return scenarios


def summarize(domain: str) -> dict[str, Any]:
    matrix = CombinatorialMatrix(domain).generate_matrix()

    max_noise = max(s.injected_noise_level for s in matrix) if matrix else 0.0
    high_risk = [s for s in matrix if s.injected_noise_level >= 2.0]

    return {
        "layer": "COMBINATORIAL_COVERAGE_LAYER",
        "domain": domain.upper(),
        "scenarios_generated": len(matrix),
        "high_risk_scenarios": len(high_risk),
        "max_noise": max_noise,
        "sample": [asdict(s) for s in matrix[:5]],
        "readonly": True,
        "advisory_only": True,
        "decision_authority": DECISION_AUTHORITY,
        "emits_verdict": EMITS_VERDICT,
        "emits_act": EMITS_ACT,
        "kernel_mutation": KERNEL_MUTATION,
        "memory_write": MEMORY_WRITE,
        "graphiti_write": GRAPHITI_WRITE,
        "neo4j_write": NEO4J_WRITE,
        "note": "Scenarios are generated only. No automatic injection into Guard X-108.",
    }


def main() -> int:
    print("=== COMBINATORIAL COVERAGE LAYER READONLY ===")
    print("decision_authority=KX108_ONLY")
    print("emits_verdict=False")
    print("emits_act=False")
    print("kernel_mutation=False")
    print("")

    for domain in ["BANK", "TRADING", "GPS_AVIATION"]:
        print(json.dumps(summarize(domain), indent=2, ensure_ascii=False))
        print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
