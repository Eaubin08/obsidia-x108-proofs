"""
Symbolic Number Encoder — encodes numbers with symbolic meaning tags.
Candidate output only. Does not claim mathematical proof.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_SYMBOLIC_MAP = {
    0: "VOID",
    1: "UNITY",
    2: "DUALITY",
    3: "TRIAD",
    5: "PENTAD",
    7: "SEPTENARY",
    8: "OCTAVE",
    9: "ENNEAD",
    10: "DECADE",
    12: "DUODECIMAL",
    13: "CHAOS",
    34: "COGNITIVE_TREES",
    108: "X108_KERNEL",
    144: "FIBONACCI_12",
}

_FIBONACCI = {0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987}
_PRIMES_SMALL = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}


@dataclass
class SymbolicNumberPacket:
    value: int
    symbolic_name: str | None
    is_fibonacci: bool
    is_prime: bool
    divisors: list[int]
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "symbolic_name": self.symbolic_name,
            "is_fibonacci": self.is_fibonacci,
            "is_prime": self.is_prime,
            "divisors": self.divisors,
            "tags": self.tags,
        }


def encode_symbolic_number(value: int) -> SymbolicNumberPacket:
    sym = {0: "VOID", 1: "UNITY", 2: "DUALITY", 3: "TRIAD", 5: "PENTAD",
           7: "SEPTENARY", 8: "OCTAVE", 9: "ENNEAD", 10: "DECADE",
           12: "DUODECIMAL", 13: "CHAOS", 34: "COGNITIVE_TREES",
           108: "X108_KERNEL", 144: "FIBONACCI_12"}.get(abs(value))
    is_fib = abs(value) in _FIBONACCI
    is_prime = abs(value) in _PRIMES_SMALL
    divisors = [i for i in range(1, abs(value) + 1) if value != 0 and abs(value) % i == 0]
    tags = []
    if is_fib:
        tags.append("FIBONACCI")
    if is_prime:
        tags.append("PRIME")
    if sym:
        tags.append(f"SYMBOLIC:{sym}")
    return SymbolicNumberPacket(
        value=value,
        symbolic_name=sym,
        is_fibonacci=is_fib,
        is_prime=is_prime,
        divisors=divisors,
        tags=tags,
    )
