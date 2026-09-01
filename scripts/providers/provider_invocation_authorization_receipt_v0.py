from __future__ import annotations

import hashlib
import json


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_INVOCATION_AUTHORIZATION_RECEIPT_V0"


def _hash(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def build_authorization_receipt(
    *,
    mission_submission_id: str,
    capability_request_ref: str,
    provider_id: str,
    activation_status: str,
    adapter_id: str,
) -> dict:

    body = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "mission_submission_id": mission_submission_id,
        "capability_request_ref": capability_request_ref,
        "provider_id": provider_id,
        "activation_status": activation_status,
        "adapter_id": adapter_id,
        "execution_authority": False,
        "kx_authority": False,
        "memory_write": False,
    }

    return {
        **body,
        "receipt_hash": _hash(body),
    }


def verify_authorization_receipt(receipt: object):

    if not isinstance(receipt, dict):
        return False, "RECEIPT_MISSING"

    body = {
        k: v
        for k, v in receipt.items()
        if k != "receipt_hash"
    }

    if receipt.get("receipt_hash") != _hash(body):
        return False, "RECEIPT_HASH_MISMATCH"

    if receipt.get("execution_authority") is not False:
        return False, "EXECUTION_AUTHORITY_FORBIDDEN"

    if receipt.get("kx_authority") is not False:
        return False, "KX_AUTHORITY_FORBIDDEN"

    if receipt.get("memory_write") is not False:
        return False, "MEMORY_WRITE_FORBIDDEN"

    return True, None
