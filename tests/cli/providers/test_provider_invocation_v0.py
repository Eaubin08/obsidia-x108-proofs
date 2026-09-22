from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from providers import provider_invocation_v0 as I


def _make():
    return I.build_provider_invocation(
        relay_mission_id="rmis-" + "a"*32,
        mission_submission_id="gsub-" + "b"*32,
        capability_request_ref="gcap-" + "c"*32,
        lease_id="cclease-" + "d"*32,
        lease_record_hash="e"*64,
        mission_capability_scope_id="mcs-" + "f"*32,
        selected_provider="brody",
        requested_capability="ENGINEERING_REASONING",
        reason="bounded cognitive request",
    )


def test_build_is_non_authority():
    x = _make()
    assert x["selected_provider"] == "brody"
    assert x["provider_called"] is False
    assert x["is_execution_authority"] is False
    assert x["is_kx_authority"] is False
    assert I.verify_provider_invocation(x) == (True, None)


def test_unknown_provider_rejected():
    try:
        _make().update({"selected_provider": "bad"})
        I.build_provider_invocation(
            relay_mission_id="rmis-a",
            mission_submission_id="gsub-b",
            capability_request_ref="gcap-c",
            lease_id="cclease-d",
            lease_record_hash="hash",
            mission_capability_scope_id="mcs-e",
            selected_provider="bad",
            requested_capability="x",
            reason="x",
        )
        assert False
    except ValueError:
        assert True


def test_execution_authority_tamper_rejected():
    x = _make()
    x["is_execution_authority"] = True
    ok, why = I.verify_provider_invocation(x)
    assert ok is False
    assert why == "IS_EXECUTION_AUTHORITY_FORBIDDEN"


def test_provider_call_tamper_rejected():
    x = _make()
    x["provider_called"] = True
    ok, why = I.verify_provider_invocation(x)
    assert ok is False
    assert why == "PROVIDER_CALLED_FORBIDDEN"
