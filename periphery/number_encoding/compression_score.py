"""
Compression Score — estimates compressibility of data. Sandbox only.
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Any


@dataclass
class CompressionScore:
    original_size: int
    compressed_size: int
    compression_ratio: float
    compressibility: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "compressibility": self.compressibility,
        }


def compute_compression_score(data: bytes | str) -> CompressionScore:
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not data:
        return CompressionScore(0, 0, 1.0, "EMPTY")

    compressed = zlib.compress(data, level=9)
    ratio = len(compressed) / len(data)

    if ratio < 0.3:
        label = "HIGH_COMPRESSIBILITY"
    elif ratio < 0.7:
        label = "MODERATE_COMPRESSIBILITY"
    elif ratio < 1.0:
        label = "LOW_COMPRESSIBILITY"
    else:
        label = "INCOMPRESSIBLE"

    return CompressionScore(
        original_size=len(data),
        compressed_size=len(compressed),
        compression_ratio=round(ratio, 4),
        compressibility=label,
    )
