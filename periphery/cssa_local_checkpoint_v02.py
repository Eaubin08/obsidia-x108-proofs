"""CSSA V0.2 offline local checkpoint runner.

The ONLY write is an explicitly supplied JSON checkpoint path in the isolated
test directory; no provider, native store or message mutation. A checkpoint
receipt is a consistency digest, not a signature or execution authorization.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from periphery.cssa_sandbox_hardening_v01 import harden_cssa_sandbox, verify_cssa_hardening


def _digest(payload):
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _checkpoint_payload(token):
    return {"schema": "CSSA_LOCAL_CHECKPOINT_V02", "token": token, "receipt": _digest(token)}


def run_cssa_local_checkpoint(deliveries, checkpoint_path, *, batch_size=1, resume=False):
    if type(batch_size) is not int or batch_size < 1:
        raise ValueError("CSSA_BATCH_SIZE_INVALID")
    path = Path(checkpoint_path)
    if path.suffix != ".json" or not path.parent.is_dir() or path.is_symlink():
        raise ValueError("CSSA_CHECKPOINT_PATH_INVALID")
    if path.exists() and not resume:
        raise ValueError("CSSA_CHECKPOINT_ALREADY_EXISTS")
    token = None
    if resume:
        try:
            if not path.is_file() or path.stat().st_size > 4096:
                raise ValueError("CSSA_CHECKPOINT_MISSING_OR_TOO_LARGE")
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if (not isinstance(envelope, dict)
                    or set(envelope) != {"schema", "token", "receipt"}
                    or envelope["schema"] != "CSSA_LOCAL_CHECKPOINT_V02"
                    or not isinstance(envelope["token"], dict)
                    or envelope["receipt"] != _digest(envelope["token"])):
                raise ValueError("CSSA_CHECKPOINT_RECEIPT_INVALID")
            token = envelope["token"]
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("CSSA_CHECKPOINT_READ_FAILED") from exc
    result = harden_cssa_sandbox(deliveries, checkpoint=token, stop_after=batch_size)
    if not verify_cssa_hardening(result):
        raise ValueError("CSSA_HARDENING_RECEIPT_INVALID")
    if result["report"]["status"] != "HOLD":
        return result
    next_token = result["report"]["checkpoint"]
    if next_token is None:
        raise ValueError("CSSA_CHECKPOINT_NOT_ISSUED")
    serialized = json.dumps(_checkpoint_payload(next_token), sort_keys=True, ensure_ascii=False)
    tmpname = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                prefix=".cssa-checkpoint-", suffix=".tmp",
                                delete=False) as f:
            tmpname = f.name
            f.write(serialized)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmpname, path)
    finally:
        if tmpname and os.path.exists(tmpname):
            os.unlink(tmpname)
    return result
