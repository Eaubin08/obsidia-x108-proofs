"""CSSA sandbox V0.1 hardening: source aliases, thread grouping, attachment metadata, replay.

Pure in-memory fixtures. Attachments are never opened, parsed or downloaded.
Replay produces inspection receipts only, never sends/applies operations.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping

from periphery.cssa_provider_sandbox_v01 import simulate_cssa_sandbox, verify_cssa_sandbox


def _sha(obj: object) -> str:
    return sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def harden_cssa_sandbox(
    deliveries: list[Mapping[str, object]], *,
    stop_after: int | None = None,
    checkpoint: Mapping[str, object] | None = None,
) -> dict:
    """Replay deterministic deliveries with strict fail-closed source identifiers."""
    if not isinstance(deliveries, list):
        raise ValueError("CSSA_DELIVERIES_INVALID")
    if stop_after is not None and (type(stop_after) is not int or stop_after < 0):
        raise ValueError("CSSA_CHECKPOINT_OFFSET_INVALID")
    normalized = []
    seen = {}
    duplicates = []
    conflicts = []
    threads = {}
    attachment_count = 0
    for item in deliveries:
        if not isinstance(item, Mapping):
            raise ValueError("CSSA_DELIVERY_INVALID")
        source, source_id = item.get("source"), item.get("source_id")
        thread_id, message = item.get("thread_id"), item.get("message")
        attachments = item.get("attachments", [])
        if (not isinstance(source, str) or not source.strip()
                or not isinstance(source_id, str) or not source_id.strip()
                or not isinstance(thread_id, str) or not thread_id.strip()
                or not isinstance(message, dict) or not isinstance(attachments, list)):
            raise ValueError("CSSA_DELIVERY_METADATA_INVALID")
        if any(not isinstance(a, dict)
               or not isinstance(a.get("name"), str)
               or not isinstance(a.get("sha256"), str)
               or len(a["sha256"]) != 64
               or any(c not in "0123456789abcdef" for c in a["sha256"])
               for a in attachments):
            raise ValueError("CSSA_ATTACHMENT_METADATA_INVALID")
        attachment_count += len(attachments)
        # Explicitly include attachment declarations in identity; never read bytes.
        fingerprint = _sha({"message": message, "attachments": attachments})
        key = source.strip() + ":" + source_id.strip()
        old = seen.get(key)
        if old is not None:
            (duplicates if old == fingerprint else conflicts).append(key)
            continue
        seen[key] = fingerprint
        normalized.append((key, thread_id, message))
        threads.setdefault(thread_id, []).append(key)

    if conflicts:
        # A collision in any provider namespace blocks all downstream evaluation.
        return _report("BLOCK", "SOURCE_ID_COLLISION", [], duplicates, conflicts,
                       threads, attachment_count, None, 0, _sha(deliveries))
    dataset_sha = _sha(deliveries)
    start = 0
    if checkpoint is not None:
        if (not isinstance(checkpoint, Mapping)
                or checkpoint.get("dataset_sha256") != dataset_sha
                or type(checkpoint.get("next_index")) is not int
                or not 0 <= checkpoint["next_index"] <= len(normalized)):
            raise ValueError("CSSA_CHECKPOINT_INVALID")
        start = checkpoint["next_index"]
    end = len(normalized) if stop_after is None else min(len(normalized), start + stop_after)
    portion = normalized[start:end]
    # Re-key source IDs to ensure aliases from separate providers cannot collide in intake.
    messages = []
    for key, _, message in portion:
        copy = dict(message)
        if not isinstance(copy.get("message_id"), str):
            raise ValueError("CSSA_MESSAGE_ID_INVALID")
        copy["message_id"] = "cssa-" + _sha(key)[:40]
        messages.append(copy)
    sandbox = simulate_cssa_sandbox(messages)
    if not verify_cssa_sandbox(sandbox):
        raise ValueError("CSSA_SANDBOX_RECEIPT_INVALID")
    checkpoint_out = {"dataset_sha256": dataset_sha, "next_index": end}
    return _report(sandbox["report"]["status"], "INSPECTION_ONLY",
                   sandbox["report"]["events"], duplicates, conflicts, threads,
                   attachment_count, checkpoint_out, len(portion), dataset_sha)


def _report(status, reason, events, duplicates, conflicts, threads,
            attachment_count, checkpoint, processed, dataset_sha):
    report = {
        "schema": "CSSA_SANDBOX_HARDENING_V01",
        "status": status,
        "reason": reason,
        "dataset_sha256": dataset_sha,
        "processed": processed,
        "threads": threads,
        "declared_attachments": attachment_count,
        "attachment_content_accessed": False,
        "duplicates": duplicates,
        "conflicts": conflicts,
        "events": events,
        "checkpoint": checkpoint,
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "external_actions": [],
        "provider_writes": False,
        "native_store_writes": False,
    }
    return {"report": report, "receipt_sha256": _sha(report)}


def verify_cssa_hardening(bundle: Mapping[str, object]) -> bool:
    if not isinstance(bundle, Mapping) or set(bundle) != {"report", "receipt_sha256"}:
        return False
    report = bundle["report"]
    if not isinstance(report, dict):
        return False
    try:
        return (_sha(report) == bundle["receipt_sha256"]
                and report["schema"] == "CSSA_SANDBOX_HARDENING_V01"
                and report["status"] in ("HOLD", "BLOCK")
                and report["decision_authority"] == "KX108_ONLY"
                and report["kx108_decision"] is None
                and report["external_actions"] == []
                and report["provider_writes"] is False
                and report["native_store_writes"] is False
                and report["attachment_content_accessed"] is False)
    except (ValueError, TypeError, KeyError):
        return False
