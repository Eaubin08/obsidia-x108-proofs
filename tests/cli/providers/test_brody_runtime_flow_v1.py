from scripts.providers.provider_invocation_envelope_v0 import (
    ProviderInvocationEnvelope,
)

from scripts.providers.provider_execution_session_v0 import (
    ProviderExecutionSession,
)

from scripts.providers.brody_runtime_adapter_v1 import (
    BrodyRuntimeAdapter,
)

from scripts.providers.provider_result_binding_v0 import (
    ProviderResultBinding,
)

from scripts.providers.provider_flow_runner_v0 import (
    ProviderFlowRunner,
)


def fake_brody_runtime(payload):
    return {
        "runtime": "brody",
        "response": "runtime-output",
        "payload": payload,
    }


def test_brody_runtime_full_flow():

    envelope = ProviderInvocationEnvelope(
        mission_ref="mission-runtime-001",
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        capability="reasoning",
        authorization_ref="receipt-runtime-001",
        execution_session_id="session-runtime-001",
        input_ref="input-runtime-001",
    )


    session = ProviderExecutionSession(
        mission_submission_id="mission-runtime-001",
        authorization_receipt_id="receipt-runtime-001",
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        capability="reasoning",
    )


    adapter = BrodyRuntimeAdapter(
        runtime=fake_brody_runtime
    )


    binding = ProviderResultBinding(
        execution_session_id=session.session_id,
        invocation_id=envelope.invocation_id,
        provider_id="brody",
        result_ref="runtime-result-001",
    )


    runner = ProviderFlowRunner()


    output = runner.run(
        envelope,
        session,
        adapter,
        binding,
    )


    assert output["provider_id"] == "brody"
    assert output["result"]["output"]["runtime"] == "brody"
    assert output["result_bound"] is True
    assert output["session_state"] == "CLOSED"


    assert output["execution_authority"] is False
    assert output["decision_authority"] is False
    assert output["memory_write"] is False
    assert output["kernel_mutation"] is False
    assert output["emits_act"] is False
