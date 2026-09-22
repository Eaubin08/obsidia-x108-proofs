from scripts.providers.provider_flow_runner_v0 import (
    ProviderFlowRunner,
)

from scripts.providers.provider_invocation_envelope_v0 import (
    ProviderInvocationEnvelope,
)

from scripts.providers.provider_execution_session_v0 import (
    ProviderExecutionSession,
)

from scripts.providers.brody_adapter_v0 import (
    BrodyAdapter,
)

from scripts.providers.provider_result_binding_v0 import (
    ProviderResultBinding,
)


def test_full_provider_flow_runner():

    envelope = ProviderInvocationEnvelope(
        mission_ref="mission-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
        authorization_ref="receipt-001",
        execution_session_id="session-001",
        input_ref="input-001",
    )


    session = ProviderExecutionSession(
        mission_submission_id="mission-001",
        authorization_receipt_id="receipt-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
    )


    adapter = BrodyAdapter()


    binding = ProviderResultBinding(
        execution_session_id=session.session_id,
        invocation_id=envelope.invocation_id,
        provider_id="brody",
        result_ref="result-001",
    )


    runner = ProviderFlowRunner()


    output = runner.run(
        envelope,
        session,
        adapter,
        binding,
    )


    assert output["provider_id"] == "brody"
    assert output["result_bound"] is True
    assert output["session_state"] == "CLOSED"

    assert output["execution_authority"] is False
    assert output["decision_authority"] is False
    assert output["memory_write"] is False
    assert output["kernel_mutation"] is False
    assert output["emits_act"] is False
