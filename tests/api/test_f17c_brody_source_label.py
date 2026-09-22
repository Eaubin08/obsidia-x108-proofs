"""F17C ? Brody runtime source labels follow the provider-neutral contract.

Historical Graphiti-specific source labeling was retired by the C2B/native-memory
provider-neutral cutover. These tests verify the current runtime contract without
reintroducing Graphiti as a response-provider authority.
"""

from apps.obsidia_api.brody_real_response_pipeline import (
    run_brody_real_response_pipeline,
)


def test_normal_response_uses_provider_neutral_runtime_source():
    result = run_brody_real_response_pipeline(
        message="X108",
        language="fr",
        session_id="f17c_provider_neutral_normal",
    )

    assert result["source"] == "REAL_BRODY_RUNTIME"
    assert result["response_source"] == "REAL_BRODY_RUNTIME"
    assert "GRAPHITI" not in result["source"]


def test_unresolved_symbol_uses_pre_reasoning_source():
    result = run_brody_real_response_pipeline(
        message="florvaxium",
        language="fr",
        session_id="f17c_provider_neutral_unknown",
    )

    assert result["source"] == "PRE_REASONING_UNRESOLVED_SYMBOL"
    assert result["response_source"] == "PRE_REASONING_UNRESOLVED_SYMBOL"

    snapshot = result.get("pre_reasoning_snapshot", {})
    directive = snapshot.get("reasoning_directive", {})

    assert directive.get("resolution_required") is True
    assert "florvaxium" in directive.get("resolution_targets", [])


def test_source_and_response_source_remain_consistent_and_provider_neutral():
    for message in ("bonjour", "X108", "florvaxium"):
        result = run_brody_real_response_pipeline(
            message=message,
            language="fr",
            session_id=f"f17c_provider_neutral_{message}",
        )

        assert result["source"] == result["response_source"]

        assert result["source"] in {
            "REAL_BRODY_RUNTIME",
            "PRE_REASONING_UNRESOLVED_SYMBOL",
            "C275_RESPONSE_CALIBRATION_REQUIRED",
            "BACKEND_STUB_LAST_RESORT",
        }

        assert not result["source"].startswith(
            "REAL_BRODY_GRAPHITI"
        )
