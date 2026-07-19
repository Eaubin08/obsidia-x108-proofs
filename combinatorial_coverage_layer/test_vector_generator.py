#!/usr/bin/env python3
"""
combinatorial_coverage_layer/test_vector_generator.py

Readonly test vector generator for Obsidia domains.

This module derives compact test vectors from boundary scenarios.
It does not inject them into runtime.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from boundary_case_generator import CombinatorialMatrix


def build_vectors(domain: str, limit: int = 10) -> dict:
    scenarios = CombinatorialMatrix(domain).generate_matrix()

    vectors = []
    for s in scenarios[:limit]:
        vectors.append(
            {
                "vector_id": s.scenario_id,
                "domain": s.domain,
                "noise": s.injected_noise_level,
                "payload": s.parameters,
                "expected_boundary": "HOLD_OR_BLOCK" if s.injected_noise_level >= 2.0 else "ANALYZE",
                "decision_authority": "KX108_ONLY",
                "emits_act": False,
            }
        )

    return {
        "generator": "test_vector_generator_v0",
        "domain": domain.upper(),
        "vectors_count": len(vectors),
        "vectors": vectors,
        "readonly": True,
        "emits_act": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
    }


def main() -> int:
    for domain in ["BANK", "TRADING", "GPS_AVIATION"]:
        print(json.dumps(build_vectors(domain), indent=2, ensure_ascii=False))
        print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
