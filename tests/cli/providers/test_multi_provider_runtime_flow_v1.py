from scripts.providers.brody_runtime_adapter_v1 import (
    BrodyRuntimeAdapter,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)

from scripts.providers.multi_provider_runtime_comparison_v1 import (
    MultiProviderRuntimeComparison,
)


def fake_brody_runtime(payload):
    return {
        "provider": "brody",
        "output": "reasoning-a",
    }


def fake_second_runtime(payload):
    return {
        "provider": "provider-b",
        "output": "reasoning-b",
    }


def test_multi_provider_runtime_flow():

    brody = BrodyRuntimeAdapter(
        runtime=fake_brody_runtime
    )


    provider_b = BrodyRuntimeAdapter(
        runtime=fake_second_runtime
    )

    provider_b.provider_id = "provider-b"
    provider_b.adapter_id = "provider-b-runtime-v1"


    brody_result = brody.invoke(
        "reasoning",
        {
            "input_ref": "input-001"
        }
    )


    provider_b_result = provider_b.invoke(
        "reasoning",
        {
            "input_ref": "input-001"
        }
    )


    receipt_a = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        invocation_id="inv-a",
    )

    receipt_a.complete(
        "result-a"
    )


    receipt_b = ProviderRuntimeReceipt(
        provider_id="provider-b",
        adapter_id="provider-b-runtime-v1",
        invocation_id="inv-b",
    )

    receipt_b.complete(
        "result-b"
    )


    binding_a = ProviderRuntimeReceiptBinding(
        runtime_execution_id=receipt_a.runtime_execution_id,
        invocation_id="inv-a",
        result_ref="result-a",
    )


    binding_b = ProviderRuntimeReceiptBinding(
        runtime_execution_id=receipt_b.runtime_execution_id,
        invocation_id="inv-b",
        result_ref="result-b",
    )


    assert binding_a.bind() is True
    assert binding_b.bind() is True


    comparison = MultiProviderRuntimeComparison()


    output = comparison.compare(
        [
            {
                "provider_id": "brody",
                "result": brody_result,
            },
            {
                "provider_id": "provider-b",
                "result": provider_b_result,
            },
        ]
    )


    assert output["providers_compared"] == 2
    assert output["comparison_only"] is True

    assert "decision" not in output

    assert comparison.decision_authority is False
    assert comparison.execution_authority is False
    assert comparison.memory_write is False
    assert comparison.kernel_mutation is False
    assert comparison.emits_act is False
