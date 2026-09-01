from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_adapter_v0 as A


def test_brody_adapter_resolve():
    x = A.resolve_adapter("brody")

    assert x["status"] == "ADAPTER_READY"
    assert x["connected"] is False


def test_unknown_adapter_rejected():
    x = A.resolve_adapter("unknown")

    assert x["status"] == "ADAPTER_REJECTED"


def test_payload_is_bounded():
    adapter = A.resolve_adapter("obsidure")

    payload = A.prepare_provider_payload(
        adapter=adapter,
        invocation={
            "capability_request_ref": "gcap-test"
        },
    )

    assert payload["payload_only"] is True
    assert payload["memory_write"] is False

    assert A.verify_adapter_payload(payload) == (True, None)


def test_adapter_cannot_gain_authority():
    adapter = A.resolve_adapter("claude")

    payload = A.prepare_provider_payload(
        adapter=adapter,
        invocation={
            "capability_request_ref": "gcap-test"
        },
    )

    payload["execution_authority"] = True

    ok, why = A.verify_adapter_payload(payload)

    assert ok is False
    assert why == "EXECUTION_AUTHORITY_FORBIDDEN"
