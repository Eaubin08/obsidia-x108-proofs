"""
Radix Systems — represents integers in various bases for symbolic analysis.
Sandbox only. Does not claim to replace standard cryptographic primitives.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RadixRepresentation:
    value: int
    binary: str
    ternary: str
    octal: str
    decimal: str
    hexadecimal: str
    base36: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "binary": self.binary,
            "ternary": self.ternary,
            "octal": self.octal,
            "decimal": self.decimal,
            "hexadecimal": self.hexadecimal,
            "base36": self.base36,
        }


_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def _to_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    negative = n < 0
    n = abs(n)
    digits = []
    while n:
        digits.append(_DIGITS[n % base])
        n //= base
    if negative:
        digits.append("-")
    return "".join(reversed(digits))


def represent_in_radices(value: int) -> RadixRepresentation:
    return RadixRepresentation(
        value=value,
        binary=bin(value),
        ternary=_to_base(value, 3),
        octal=oct(value),
        decimal=str(value),
        hexadecimal=hex(value),
        base36=_to_base(value, 36),
    )
