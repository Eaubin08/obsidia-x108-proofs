#!/usr/bin/env python3
"""
research/math/prime_seeker_v1.py

AGENT PRIMESEEKER — Explorateur combinatoire et nombres premiers.

Invariants:
- decision_authority = KX108_ONLY
- emits_verdict = False
- emits_act = False
- kernel_mutation = False
- memory_write = False

Role:
- Recherche mathématique périphérique readonly.
- Ne décide pas.
- Ne modifie pas le kernel.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


DECISION_AUTHORITY = "KX108_ONLY"
EMITS_VERDICT = False
EMITS_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False


@dataclass(frozen=True)
class MathPartition:
    number: int
    components: list[int]
    symmetry_score: float


class PartitionEngine:
    """Génère des partitions simples readonly pour décomposer un nombre."""

    def generate(self, n: int) -> list[MathPartition]:
        if n <= 1:
            return [MathPartition(number=n, components=[n], symmetry_score=0.0)]

        partitions: list[MathPartition] = []

        # Partition triviale
        partitions.append(MathPartition(number=n, components=[n], symmetry_score=1.0))

        # Partitions 2-termes simples
        for a in range(1, n // 2 + 1):
            b = n - a
            symmetry = 1.0 - abs(a - b) / max(n, 1)
            partitions.append(
                MathPartition(
                    number=n,
                    components=[a, b],
                    symmetry_score=round(symmetry, 6),
                )
            )

        return partitions


class DiophantineMapper:
    """Transforme les partitions en empreintes diophantiennes readonly."""

    def map(self, partitions: list[MathPartition]) -> dict[str, Any]:
        equations = []

        for p in partitions:
            equations.append(
                {
                    "number": p.number,
                    "components": p.components,
                    "sum_ok": sum(p.components) == p.number,
                    "symmetry_score": p.symmetry_score,
                }
            )

        return {
            "equations_generated": len(equations),
            "equations": equations,
            "status": "MAPPED_READONLY",
        }


class MathematicalBalance:
    """BALMA V0: cohérence logique + tension de symétrie."""

    def cross_validate(self, equations: dict[str, Any]) -> float:
        eqs = equations.get("equations", [])
        if not eqs:
            return 0.0

        valid_ratio = sum(1 for e in eqs if e.get("sum_ok")) / len(eqs)
        symmetry_mean = sum(float(e.get("symmetry_score", 0.0)) for e in eqs) / len(eqs)

        score = (0.70 * valid_ratio) + (0.30 * symmetry_mean)
        return round(max(0.0, min(1.0, score)), 6)


def is_prime_basic(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2

    return True


class PrimeSeekerAgent:
    def __init__(self) -> None:
        self.partition_engine = PartitionEngine()
        self.diophantine_mapper = DiophantineMapper()
        self.prime_validator = MathematicalBalance()

    def explore(self, n: int) -> dict[str, Any]:
        partitions = self.partition_engine.generate(n)
        diophantine_eqs = self.diophantine_mapper.map(partitions)
        coherence = self.prime_validator.cross_validate(diophantine_eqs)
        prime_flag = is_prime_basic(n)

        return {
            "agent": "PrimeSeekerAgent",
            "target_number": n,
            "partitions_count": len(partitions),
            "coherence_score": coherence,
            "classification": "PRIME_CANDIDATE" if prime_flag else "COMPOSITE_CANDIDATE",
            "basic_prime_check": prime_flag,
            "sample_partitions": [asdict(p) for p in partitions[:8]],
            "decision_authority": DECISION_AUTHORITY,
            "emits_verdict": EMITS_VERDICT,
            "emits_act": EMITS_ACT,
            "kernel_mutation": KERNEL_MUTATION,
            "memory_write": MEMORY_WRITE,
            "readonly": True,
            "advisory_only": True,
        }


def main() -> int:
    seeker = PrimeSeekerAgent()

    print("=== PRIMESEEKER READONLY ===")
    print("decision_authority=KX108_ONLY")
    print("emits_verdict=False")
    print("kernel_mutation=False")
    print("")

    for n in [7, 12, 17, 21, 31]:
        result = seeker.explore(n)
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
