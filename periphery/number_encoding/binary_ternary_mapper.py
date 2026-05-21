"""
Binary-Ternary Mapper — maps between binary and ternary (balanced ternary) representations.
Symbolic/educational sandbox only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BinaryTernaryMapping:
    value: int
    binary_str: str
    ternary_str: str
    balanced_ternary: str
    bit_count: int
    trit_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "binary_str": self.binary_str,
            "ternary_str": self.ternary_str,
            "balanced_ternary": self.balanced_ternary,
            "bit_count": self.bit_count,
            "trit_count": self.trit_count,
        }


def _to_ternary(n: int) -> str:
    if n == 0:
        return "0"
    neg = n < 0
    n = abs(n)
    digits = []
    while n:
        digits.append(str(n % 3))
        n //= 3
    if neg:
        digits.append("-")
    return "".join(reversed(digits))


def _to_balanced_ternary(n: int) -> str:
    if n == 0:
        return "0"
    digits = []
    while n != 0:
        r = n % 3
        if r == 2:
            r = -1
        digits.append({-1: "T", 0: "0", 1: "1"}[r])
        n = (n - r) // 3
    return "".join(reversed(digits))


def map_binary_ternary(value: int) -> BinaryTernaryMapping:
    b = bin(value)
    t = _to_ternary(value)
    bt = _to_balanced_ternary(value)
    return BinaryTernaryMapping(
        value=value,
        binary_str=b,
        ternary_str=t,
        balanced_ternary=bt,
        bit_count=len(b.lstrip("-").replace("0b", "")),
        trit_count=len(t.lstrip("-")),
    )
