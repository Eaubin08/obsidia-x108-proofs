from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_binder_v0 as B
from providers.provider_result_envelope_v0 import build_provider_result


def _mission():
    return dict(
        relay_mission_id="rmis-" + "a"*32,
        mission_submission_id="gsub-" + "b"*32,
        capability_request_ref="gcap-" + "c"*32,
        lease_id="cclease-" + "d"*32,
        lease_record_hash="e"*64,
        mission_capability_scope_id="mcs-" + "f"*32,
        allowed_providers=["brody"],
        requested_capability="ENGINEERING_REASONING",
        reason="bounded cognitive evidence request",
    )


def test_full_cg9_provider_chain():
    binding = B.prepare_provider_binding(**_mission())

    assert binding["status"] == "BINDER_READY"
    assert binding["provider"] == "brody"
    assert binding["provider_called"] is False
    assert binding["execution_started"] is False

    invocation = binding["invocation"]

    result = build_provider_result(
        invocation_id="pinv-" + "x"*32,
        selected_provider=invocation["selected_provider"],
        result_kind="EVIDENCE",
        summary="validated reasoning evidence",
        evidence_refs=["proof-e2e-1"],
    )

    accepted = B.accept_provider_result(result)

    assert accepted["status"] == "RESULT_ACCEPTED"
    assert accepted["execution_started"] is False


def test_full_chain_never_creates_authority():
    binding = B.prepare_provider_binding(**_mission())

    invocation = binding["invocation"]

    assert invocation["is_execution_authority"] is False
    assert invocation["is_kx_authority"] is False
    assert invocation["grants_tool_access"] is False
    assert invocation["grants_scope"] is False

    result = build_provider_result(
        invocation_id="pinv-" + "y"*32,
        selected_provider="brody",
        result_kind="PROPOSAL",
        summary="proposal only",
    )

    accepted = B.accept_provider_result(result)

    assert accepted["result"]["emits_act"] is False
    assert accepted["result"]["emits_decision"] is False
