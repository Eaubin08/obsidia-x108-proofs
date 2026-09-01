from scripts.providers.provider_lifecycle_manager_v0 import (
    ProviderLifecycleManager,
    ProviderLifecycleState,
)

from scripts.providers.provider_execution_session_v0 import (
    ProviderExecutionSession,
    ExecutionState,
)

from scripts.providers.brody_adapter_v0 import (
    BrodyAdapter,
)

from scripts.providers.provider_result_binding_v0 import (
    ProviderResultBinding,
)


def test_cg9_full_provider_flow():

    # 1. Provider lifecycle

    lifecycle = ProviderLifecycleManager(
        provider_id="brody"
    )

    lifecycle.declare()
    lifecycle.validate()
    lifecycle.enable()

    assert lifecycle.state == ProviderLifecycleState.ENABLED
    assert lifecycle.can_invoke() is True


    # 2. Execution session

    session = ProviderExecutionSession(
        mission_submission_id="mission-001",
        authorization_receipt_id="receipt-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
    )

    session.authorize()

    assert session.state == ExecutionState.AUTHORIZED


    session.start()

    assert session.state == ExecutionState.RUNNING


    # 3. Provider adapter

    adapter = BrodyAdapter()

    result = adapter.invoke(
        "reasoning",
        {
            "input": "analyse"
        }
    )

    assert result["provider_id"] == "brody"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False


    # 4. Complete execution

    session.complete(
        "result-001"
    )

    assert session.state == ExecutionState.COMPLETED


    # 5. Bind result

    binding = ProviderResultBinding(
        execution_session_id=session.session_id,
        invocation_id="invocation-001",
        provider_id="brody",
        result_ref=session.result_ref,
    )

    binding.bind()

    assert binding.bound is True


    # 6. Close execution

    session.close()

    assert session.state == ExecutionState.CLOSED
