"""CSSA V0.3 bounded preflight policy for offline fixture checkpoints.

This is a conservative validator, not an OS security boundary or lock manager.
No filesystem mutation, no provider calls and no production credentials.
"""
from __future__ import annotations

from pathlib import Path
import re

SAFE_NAME = re.compile(r"^cssa-[a-z0-9_-]{1,48}\.json$")
ALLOWED_SOURCES = frozenset({"MAILBOX_FAKE", "CRM_FAKE", "FORM_FAKE"})


def check_cssa_checkpoint_location(root, target) -> dict:
    base = Path(root)
    path = Path(target)
    if (not base.is_absolute() or not path.is_absolute()
            or not base.is_dir() or base.is_symlink()
            or not SAFE_NAME.fullmatch(path.name)):
        raise ValueError("CSSA_V03_PATH_POLICY")
    canonical_base = base.resolve(strict=True)
    if path.parent.resolve(strict=True) != canonical_base:
        raise ValueError("CSSA_V03_PATH_OUTSIDE_ROOT")
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("CSSA_V03_PATH_SYMLINK_OR_NONFILE")
    return {"schema": "CSSA_V03_PATH_PREFLIGHT", "status": "HOLD",
            "target": str(path), "external_actions": []}


def inspect_cssa_sender_claim(delivery: dict) -> dict:
    if not isinstance(delivery, dict):
        raise ValueError("CSSA_V03_DELIVERY_INVALID")
    source = delivery.get("source")
    sender = delivery.get("claimed_sender")
    attested = delivery.get("provider_attested_sender")
    if (source not in ALLOWED_SOURCES or not isinstance(sender, str)
            or not isinstance(attested, str) or not sender or not attested):
        return {"status": "BLOCK", "reason": "UNVERIFIED_SENDER",
                "external_actions": []}
    # Exact comparison is a synthetic consistency check, NOT SPF/DKIM/DMARC proof.
    if sender.casefold().strip() != attested.casefold().strip():
        return {"status": "BLOCK", "reason": "SENDER_CLAIM_MISMATCH",
                "external_actions": []}
    return {"status": "HOLD", "reason": "SYNTHETIC_SENDER_MATCH_ONLY",
            "sender_visible": False, "external_actions": []}


def preflight_cssa_batch(deliveries, *, max_items=100, max_chars=120000):
    if type(max_items) is not int or max_items < 1 or type(max_chars) is not int or max_chars < 1:
        raise ValueError("CSSA_V03_LIMIT_INVALID")
    if not isinstance(deliveries, list) or len(deliveries) > max_items:
        raise ValueError("CSSA_V03_BATCH_LIMIT")
    import json
    try:
        serialized = json.dumps(deliveries, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("CSSA_V03_BATCH_MALFORMED") from exc
    if len(serialized) > max_chars:
        raise ValueError("CSSA_V03_BATCH_SIZE_LIMIT")
    return {"status": "HOLD", "items": len(deliveries),
            "contains_personal_data": "UNKNOWN", "external_actions": []}
