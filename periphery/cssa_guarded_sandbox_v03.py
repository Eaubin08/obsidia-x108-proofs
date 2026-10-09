"""CSSA V0.3 guarded single-process entrypoint, synthetic-only.

Preflight runs before the V0.2 checkpoint operation. Exclusive lock-file
creation is nonblocking, local and best-effort; stale-lock recovery and
cross-host guarantees are intentionally NOT provided.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path

from periphery.cssa_local_checkpoint_v02 import run_cssa_local_checkpoint
from periphery.cssa_security_preflight_v03 import (
    check_cssa_checkpoint_location, inspect_cssa_sender_claim, preflight_cssa_batch,
)


@contextmanager
def _exclusive_cssa_lock(path):
    lock = Path(str(path) + ".lock")
    fd = None
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        yield
    except FileExistsError as exc:
        raise ValueError("CSSA_V03_CONCURRENT_ACCESS_BLOCKED") from exc
    finally:
        if fd is not None:
            os.close(fd)
            lock.unlink()


def run_cssa_guarded_v03(deliveries, *, sandbox_root, checkpoint_path,
                         batch_size=1, resume=False):
    check_cssa_checkpoint_location(sandbox_root, checkpoint_path)
    preflight_cssa_batch(deliveries)
    for item in deliveries:
        if not isinstance(item, dict):
            raise ValueError("CSSA_V03_DELIVERY_INVALID")
        sender_check = inspect_cssa_sender_claim(item)
        if sender_check["status"] != "HOLD":
            raise ValueError("CSSA_V03_SENDER_BLOCKED:" + sender_check["reason"])
    with _exclusive_cssa_lock(checkpoint_path):
        result = run_cssa_local_checkpoint(
            deliveries, checkpoint_path, batch_size=batch_size, resume=resume
        )
    return {
        "schema": "CSSA_GUARDED_SANDBOX_V03",
        "status": result["report"]["status"],
        "processed": result["report"]["processed"],
        "checkpoint": result["report"]["checkpoint"],
        "external_actions": [],
        "provider_writes": False,
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
    }
