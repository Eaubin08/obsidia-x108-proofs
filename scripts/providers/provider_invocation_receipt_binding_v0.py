from __future__ import annotations

from typing import Optional


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_INVOCATION_RECEIPT_BINDING_V0"


def build_binding(
    *,
    authorization_receipt: dict,
    invocation_record: dict,
    result_envelope: dict,
) -> dict:

    return {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,

        "receipt_hash": authorization_receipt.get(
            "receipt_hash"
        ),

        "invocation_id": invocation_record.get(
            "invocation_id"
        ),

        "provider_id": invocation_record.get(
            "provider_id"
        ),

        "result_invocation_id": result_envelope.get(
            "invocation_id"
        ),

        "execution_authority": False,
        "kx_authority": False,
        "memory_write": False,
    }


def verify_binding(
    binding: object,
) -> tuple[bool, Optional[str]]:

    if not isinstance(binding, dict):
        return False, "BINDING_MISSING"

    required = (
        "receipt_hash",
        "invocation_id",
        "provider_id",
        "result_invocation_id",
    )

    for key in required:
        if not binding.get(key):
            return False, f"MISSING_{key.upper()}"

    if binding["invocation_id"] != binding["result_invocation_id"]:
        return False, "INVOCATION_RESULT_MISMATCH"

    if binding.get("execution_authority") is not False:
        return False, "EXECUTION_AUTHORITY_FORBIDDEN"

    if binding.get("kx_authority") is not False:
        return False, "KX_AUTHORITY_FORBIDDEN"

    if binding.get("memory_write") is not False:
        return False, "MEMORY_WRITE_FORBIDDEN"

    return True, None
