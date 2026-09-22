from scripts.providers.provider_invocation_envelope_v0 import (
    ProviderInvocationEnvelope,
)

from scripts.providers.provider_execution_session_v0 import (
    ProviderExecutionSession,
)

from scripts.providers.brody_runtime_adapter_v1 import (
    BrodyRuntimeAdapter,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)

from scripts.providers.provider_result_binding_v0 import (
    ProviderResultBinding,
)

from scripts.providers.provider_flow_runner_v0 import (
    ProviderFlowRunner,
)


def fake_runtime(payload):

    return {
        "runtime": "brody",
        "response": "receipt-flow-output",
        "payload": payload,
    }


def test_brody_runtime_receipt_complete_flow():

    envelope = ProviderInvocationEnvelope(
        mission_ref="mission-receipt-001",
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        capability="reasoning",
        authorization_ref="receipt-auth-001",
        execution_session_id="session-receipt-001",
        input_ref="input-receipt-001",
    )


    session = ProviderExecutionSession(
        mission_submission_id="mission-receipt-001",
        authorization_receipt_id="receipt-auth-001",
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        capability="reasoning",
    )


    adapter = BrodyRuntimeAdapter(
        runtime=fake_runtime
    )


    runtime_receipt = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        invocation_id=envelope.invocation_id,
    )


    result = adapter.invoke(
        "reasoning",
        {
            "input_ref": envelope.input_ref
        }
    )


    runtime_receipt.complete(
        "result-receipt-001"
    )


    runtime_binding = ProviderRuntimeReceiptBinding(
        runtime_execution_id=runtime_receipt.runtime_execution_id,
        invocation_id=envelope.invocation_id,
        result_ref="result-receipt-001",
    )


    assert runtime_binding.bind() is True


    result_binding = ProviderResultBinding(
        execution_session_id=session.session_id,
        invocation_id=envelope.invocation_id,
        provider_id="brody",
        result_ref="result-receipt-001",
    )


    runner = ProviderFlowRunner()

    output = runner.run(
        envelope,
        session,
        adapter,
        result_binding,
    )


    assert result["status"] == "PRODUCED"

    assert runtime_receipt.status == "COMPLETED"

    assert runtime_binding.bound is True

    assert output["result_bound"] is True

    assert output["session_state"] == "CLOSED"


    assert output["decision_authority"] is False
    assert output["execution_authority"] is False
    assert output["memory_write"] is False
    assert output["kernel_mutation"] is False
    assert output["emits_act"] is False
