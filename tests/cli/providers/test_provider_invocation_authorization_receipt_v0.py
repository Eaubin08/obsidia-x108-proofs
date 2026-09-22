from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_invocation_authorization_receipt_v0 as R


def test_receipt_creation():

    receipt = R.build_authorization_receipt(
        mission_submission_id="ms-test",
        capability_request_ref="cap-test",
        provider_id="brody",
        activation_status="ACTIVATION_READY",
        adapter_id="BRODY_ADAPTER_V0",
    )

    assert receipt["provider_id"] == "brody"
    assert R.verify_authorization_receipt(
        receipt
    ) == (True, None)


def test_receipt_hash_detects_mutation():

    receipt = R.build_authorization_receipt(
        mission_submission_id="ms-test",
        capability_request_ref="cap-test",
        provider_id="brody",
        activation_status="ACTIVATION_READY",
        adapter_id="BRODY_ADAPTER_V0",
    )

    receipt["provider_id"] = "claude"

    ok, why = R.verify_authorization_receipt(
        receipt
    )

    assert ok is False
    assert why == "RECEIPT_HASH_MISMATCH"


def test_receipt_has_no_authority():

    receipt = R.build_authorization_receipt(
        mission_submission_id="ms-test",
        capability_request_ref="cap-test",
        provider_id="obsidure",
        activation_status="ACTIVATION_READY",
        adapter_id="OBSIDURE_ADAPTER_V0",
    )

    assert receipt["execution_authority"] is False
    assert receipt["kx_authority"] is False


def test_fake_memory_write_rejected():

    receipt = R.build_authorization_receipt(
        mission_submission_id="ms-test",
        capability_request_ref="cap-test",
        provider_id="claude",
        activation_status="ACTIVATION_READY",
        adapter_id="CLAUDE_ADAPTER_V0",
    )

    receipt["memory_write"] = True

    ok, why = R.verify_authorization_receipt(
        receipt
    )

    assert ok is False
    assert why == "RECEIPT_HASH_MISMATCH"
