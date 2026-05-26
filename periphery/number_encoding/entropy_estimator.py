"""
Entropy Estimator — estimates Shannon entropy of a byte sequence.
Sandbox only. Does not perform cryptographic analysis.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class EntropyEstimate:
    data_len: int
    entropy_bits: float
    entropy_normalized: float
    unique_symbols: int
    is_high_entropy: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_len": self.data_len,
            "entropy_bits": self.entropy_bits,
            "entropy_normalized": self.entropy_normalized,
            "unique_symbols": self.unique_symbols,
            "is_high_entropy": self.is_high_entropy,
        }


def estimate_entropy(data: bytes | str) -> EntropyEstimate:
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not data:
        return EntropyEstimate(0, 0.0, 0.0, 0, False)

    counts = Counter(data)
    total = len(data)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    max_entropy = math.log2(256)
    normalized = entropy / max_entropy if max_entropy > 0 else 0.0

    return EntropyEstimate(
        data_len=total,
        entropy_bits=round(entropy, 4),
        entropy_normalized=round(normalized, 4),
        unique_symbols=len(counts),
        is_high_entropy=normalized > 0.8,
    )
