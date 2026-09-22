from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_result_envelope_v0 as R


def make():
    return R.build_provider_result(
        invocation_id="pinv-" + "a"*32,
        selected_provider="brody",
        result_kind="EVIDENCE",
        summary="bounded reasoning evidence",
        evidence_refs=["proof-1"],
    )


def test_valid_result():
    x = make()
    assert x["result_kind"] == "EVIDENCE"
    assert x["emits_act"] is False
    assert R.verify_provider_result(x) == (True, None)


def test_proposal_allowed():
    x = R.build_provider_result(
        invocation_id="pinv-" + "a"*32,
        selected_provider="obsidure",
        result_kind="PROPOSAL",
        summary="formal proposal",
    )
    assert R.verify_provider_result(x) == (True, None)


def test_authority_forbidden():
    x = make()
    x["is_execution_authority"] = True
    ok, why = R.verify_provider_result(x)
    assert ok is False
    assert why == "IS_EXECUTION_AUTHORITY_FORBIDDEN"


def test_decision_emission_forbidden():
    x = make()
    x["emits_decision"] = True
    ok, why = R.verify_provider_result(x)
    assert ok is False
    assert why == "EMITS_DECISION_FORBIDDEN"
