from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_binder_v0 as B
from providers.provider_result_envelope_v0 import build_provider_result


def base():
    return dict(
        relay_mission_id="rmis-"+"a"*32,
        mission_submission_id="gsub-"+"b"*32,
        capability_request_ref="gcap-"+"c"*32,
        lease_id="cclease-"+"d"*32,
        lease_record_hash="e"*64,
        mission_capability_scope_id="mcs-"+"f"*32,
        allowed_providers=["brody"],
        requested_capability="ENGINEERING_REASONING",
        reason="bounded request",
    )


def test_binder_ready():
    out = B.prepare_provider_binding(**base())
    assert out["status"] == "BINDER_READY"
    assert out["provider_called"] is False
    assert out["execution_started"] is False


def test_multiple_provider_requires_choice():
    x = base()
    x["allowed_providers"] = ["brody", "claude"]
    out = B.prepare_provider_binding(**x)
    assert out["status"] == "BINDER_REJECTED"


def test_result_acceptance():
    result = build_provider_result(
        invocation_id="pinv-"+"a"*32,
        selected_provider="brody",
        result_kind="EVIDENCE",
        summary="proof",
    )
    out = B.accept_provider_result(result)
    assert out["status"] == "RESULT_ACCEPTED"


def test_result_authority_rejected():
    result = build_provider_result(
        invocation_id="pinv-"+"a"*32,
        selected_provider="brody",
        result_kind="EVIDENCE",
        summary="proof",
    )
    result["is_execution_authority"] = True

    out = B.accept_provider_result(result)

    assert out["status"] == "RESULT_REJECTED"
