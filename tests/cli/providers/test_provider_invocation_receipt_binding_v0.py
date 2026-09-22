from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_invocation_receipt_binding_v0 as B


def test_binding_valid():

    binding = B.build_binding(
        authorization_receipt={
            "receipt_hash": "hash123",
        },
        invocation_record={
            "invocation_id": "inv-1",
            "provider_id": "brody",
        },
        result_envelope={
            "invocation_id": "inv-1",
        },
    )

    assert B.verify_binding(
        binding
    ) == (True, None)


def test_result_wrong_invocation_rejected():

    binding = B.build_binding(
        authorization_receipt={
            "receipt_hash": "hash123",
        },
        invocation_record={
            "invocation_id": "inv-1",
            "provider_id": "brody",
        },
        result_envelope={
            "invocation_id": "inv-2",
        },
    )

    ok, why = B.verify_binding(binding)

    assert ok is False
    assert why == "INVOCATION_RESULT_MISMATCH"


def test_binding_has_no_authority():

    binding = B.build_binding(
        authorization_receipt={
            "receipt_hash": "hash123",
        },
        invocation_record={
            "invocation_id": "inv-1",
            "provider_id": "obsidure",
        },
        result_envelope={
            "invocation_id": "inv-1",
        },
    )

    assert binding["execution_authority"] is False
    assert binding["kx_authority"] is False


def test_fake_memory_write_rejected():

    binding = B.build_binding(
        authorization_receipt={
            "receipt_hash": "hash123",
        },
        invocation_record={
            "invocation_id": "inv-1",
            "provider_id": "claude",
        },
        result_envelope={
            "invocation_id": "inv-1",
        },
    )

    binding["memory_write"] = True

    ok, why = B.verify_binding(binding)

    assert ok is False
    assert why == "MEMORY_WRITE_FORBIDDEN"
