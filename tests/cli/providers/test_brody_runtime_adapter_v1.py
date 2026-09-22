import pytest

from scripts.providers.brody_runtime_adapter_v1 import (
    BrodyRuntimeAdapter,
    BrodyRuntimeAdapterError,
)


def fake_runtime(payload):
    return {
        "response": "brody-output",
        "input": payload,
    }


def build_adapter():
    return BrodyRuntimeAdapter(
        runtime=fake_runtime
    )


def test_runtime_adapter_metadata():

    adapter = build_adapter()

    assert adapter.provider_id == "brody"
    assert adapter.adapter_id == "brody-runtime-v1"


def test_supported_capability():

    adapter = build_adapter()

    assert adapter.supports("reasoning") is True


def test_runtime_execution_returns_bounded_result():

    adapter = build_adapter()

    result = adapter.invoke(
        "reasoning",
        {
            "input_ref": "input-001"
        }
    )

    assert result["status"] == "PRODUCED"
    assert result["output"]["response"] == "brody-output"


def test_authority_invariants():

    adapter = build_adapter()

    result = adapter.invoke(
        "analysis",
        {}
    )

    assert result["execution_authority"] is False
    assert result["decision_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False


def test_unknown_capability_blocked():

    adapter = build_adapter()

    with pytest.raises(BrodyRuntimeAdapterError):

        adapter.invoke(
            "act",
            {}
        )
