from scripts.providers.provider_lifecycle_manager_v0 import (
    ProviderLifecycleManager,
    ProviderLifecycleState,
)

from scripts.providers.provider_capability_arbitration_v0 import (
    ProviderCapabilityArbitration,
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

from scripts.providers.provider_flow_runner_v0 import (
    ProviderFlowRunner,
)

from scripts.providers.provider_arbitration_v0 import (
    ProviderArbitration,
)


def test_cg9_global_conformance_flow():

    # 1. Capability comparison

    capability = ProviderCapabilityArbitration(
        comparison_id="cap-001"
    )

    capability_result = capability.compare_capabilities(
        "reasoning",
        [
            {
                "provider_id": "brody",
                "capabilities": ["reasoning"],
            }
        ]
    )

    assert len(
        capability_result["compatible_providers"]
    ) == 1


    # 2. Provider lifecycle

    lifecycle = ProviderLifecycleManager(
        provider_id="brody"
    )

    lifecycle.declare()
    lifecycle.validate()
    lifecycle.enable()

    assert lifecycle.state == ProviderLifecycleState.ENABLED


    # 3. Invocation envelope

    envelope = ProviderInvocationEnvelope(
        mission_ref="mission-global-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
        authorization_ref="receipt-global-001",
        execution_session_id="session-global-001",
        input_ref="input-global-001",
    )

    assert envelope.validate() is True


    # 4. Session

    session = ProviderExecutionSession(
        mission_submission_id="mission-global-001",
        authorization_receipt_id="receipt-global-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
    )


    # 5. Adapter

    adapter = BrodyAdapter()


    # 6. Binding

    binding = ProviderResultBinding(
        execution_session_id=session.session_id,
        invocation_id=envelope.invocation_id,
        provider_id="brody",
        result_ref="result-global-001",
    )


    # 7. Runner

    runner = ProviderFlowRunner()

    output = runner.run(
        envelope,
        session,
        adapter,
        binding,
    )


    assert output["result_bound"] is True
    assert output["session_state"] == "CLOSED"


    # 8. Result arbitration

    arbitration = ProviderArbitration(
        comparison_id="result-global-001"
    )

    comparison = arbitration.compare(
        [
            {
                "provider_id": "brody",
                "result_ref": "result-global-001",
            }
        ]
    )

    assert comparison["comparison_only"] is True


    # 9. Global authority invariants

    assert output["decision_authority"] is False
    assert output["execution_authority"] is False
    assert output["memory_write"] is False
    assert output["kernel_mutation"] is False
    assert output["emits_act"] is False
