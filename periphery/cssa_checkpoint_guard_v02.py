"""CSSA V0.2 checkpoint audit with caller-trusted anchor (offline only).

SHA-256 alone does not authenticate a writable checkpoint. This separate guard
compares its exact bytes with an externally held expected digest; it never
grants execution authority and never uses a network/provider.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from periphery.cssa_local_checkpoint_v02 import run_cssa_local_checkpoint


def fingerprint_cssa_checkpoint(path) -> str:
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 4096:
        raise ValueError("CSSA_ANCHOR_SOURCE_INVALID")
    return sha256(source.read_bytes()).hexdigest()


def resume_cssa_anchored(deliveries, checkpoint_path, trusted_sha256, *, batch_size=1):
    if (not isinstance(trusted_sha256, str) or len(trusted_sha256) != 64
            or any(c not in "0123456789abcdef" for c in trusted_sha256)):
        raise ValueError("CSSA_TRUSTED_ANCHOR_INVALID")
    if fingerprint_cssa_checkpoint(checkpoint_path) != trusted_sha256:
        raise ValueError("CSSA_CHECKPOINT_ANCHOR_MISMATCH")
    return run_cssa_local_checkpoint(
        deliveries, checkpoint_path, batch_size=batch_size, resume=True
    )
