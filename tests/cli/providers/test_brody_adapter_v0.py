import pytest

from scripts.providers.brody_adapter_v0 import (
    BrodyAdapter,
    BrodyAdapterError,
)


def build_adapter():
    return BrodyAdapter()


def test_adapter_metadata():

    adapter = build_adapter()

    assert adapter.provider_id == "brody"
    assert adapter.adapter_id == "brody-adapter-v0"


def test_supported_capability():

    adapter = build_adapter()

    assert adapter.supports("reasoning") is True


def test_invoke_returns_bounded_result():

    adapter = build_adapter()

    result = adapter.invoke(
        "reasoning",
        {"input": "test"}
    )

    assert result["provider_id"] == "brody"
    assert result["status"] == "PRODUCED"
    assert result["execution_authority"] is False
    assert result["decision_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False


def test_unknown_capability_blocked():

    adapter = build_adapter()

    with pytest.raises(BrodyAdapterError):
        adapter.invoke(
            "act",
            {}
        )


def test_no_authority_exposed():

    adapter = build_adapter()

    assert adapter.execution_authority is False
    assert adapter.decision_authority is False
